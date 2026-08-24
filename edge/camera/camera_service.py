"""
Hydroponics Platform — Edge Camera Service
Handles image acquisition from ESP32-CAM (USB Serial / Wi-Fi IP), IP Cameras, or USB Webcams.
Provides a clean 1-line Python interface for AI/ML inference pipelines.
"""

import os
import time
import io
import glob
import urllib.request
from datetime import datetime
from typing import Optional, Union

# Optional dependencies with graceful fallbacks
try:
    import serial
except ImportError:
    serial = None

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    import numpy as np
except ImportError:
    np = None

SNAPSHOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "snapshots"))
ARCHIVE_DIR = os.path.join(SNAPSHOT_DIR, "archive")
LATEST_IMAGE_PATH = os.path.join(SNAPSHOT_DIR, "latest.jpg")

os.makedirs(SNAPSHOT_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)


class CameraService:
    """Singleton service for managing wired serial and wireless IP camera frame acquisition."""

    def __init__(self, port: Optional[str] = None, ip_url: Optional[str] = None, baudrate: int = 115200):
        self.port = port or os.environ.get("CAMERA_SERIAL_PORT")
        self.ip_url = ip_url or os.environ.get("CAMERA_IP_URL")
        self.baudrate = baudrate
        self._ensure_sample_image()

    def _ensure_sample_image(self):
        """Creates a sample test frame if no camera snapshot exists yet."""
        if not os.path.exists(LATEST_IMAGE_PATH):
            if Image:
                img = Image.new("RGB", (800, 600), color=(18, 30, 22))
                img.save(LATEST_IMAGE_PATH, "JPEG")
            else:
                with open(LATEST_IMAGE_PATH, "wb") as f:
                    f.write(b"")

    def capture_from_ip(self, url: str, timeout: float = 5.0) -> Optional[bytes]:
        """
        Captures a frame from an IP Camera stream (HTTP, MJPEG, ESP32-CAM /capture or /stream).
        Supports:
          - Direct JPEG snapshot endpoints (e.g. http://192.168.1.50:8080/shot.jpg)
          - MJPEG multipart video streams (e.g. http://192.168.1.50:8080/video or http://192.168.1.50/stream)
        """
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "AgroEye-Hydroponics-Edge/1.0"}
            )
            with urllib.request.urlopen(req, timeout=timeout) as response:
                content_type = response.headers.get("Content-Type", "")
                
                # Case 1: Direct Image (JPEG / PNG)
                if "image" in content_type:
                    return response.read()

                # Case 2: MJPEG multipart stream -> extract first complete JPEG frame
                bytes_buffer = bytearray()
                start_time = time.time()
                while time.time() - start_time < timeout:
                    chunk = response.read(4096)
                    if not chunk:
                        break
                    bytes_buffer.extend(chunk)
                    
                    # Look for JPEG Start of Image (SOI 0xFFD8) and End of Image (EOI 0xFFD9)
                    a = bytes_buffer.find(b"\xff\xd8")
                    b = bytes_buffer.find(b"\xff\xd9")
                    if a != -1 and b != -1 and b > a:
                        jpg_data = bytes(bytes_buffer[a:b+2])
                        return jpg_data

            return None
        except Exception as e:
            print(f"❌ [CameraService] IP Camera capture failed ({url}): {e}")
            return None

    def capture_from_serial(self, port: str) -> Optional[bytes]:
        """Requests a high-res JPEG frame from the ESP32-CAM via Wired USB Serial."""
        if not serial:
            print("[ERROR] [CameraService] pyserial not installed.")
            return None

        try:
            print(f"[CAMERA] [CameraService] Connecting to ESP32-CAM on {port}...")
            ser = serial.Serial(port=port, baudrate=self.baudrate, timeout=1.0)
            ser.dtr = False
            ser.rts = False
            
            time.sleep(2.0)
            ser.reset_input_buffer()

            ser.write(b"CAPTURE\n")
            ser.flush()

            start_time = time.time()
            frame_len = 0
            header_found = False

            while (time.time() - start_time) < 6.0:
                raw_line = ser.readline()
                if not raw_line:
                    continue
                line = raw_line.decode("utf-8", errors="ignore").strip()
                if line.startswith("---FRAME_START:"):
                    try:
                        frame_len = int(line.split(":")[1].replace("---", ""))
                        header_found = True
                        break
                    except Exception:
                        pass

            if not header_found or frame_len <= 0:
                ser.close()
                return None

            jpeg_bytes = bytearray()
            read_start = time.time()
            while len(jpeg_bytes) < frame_len and (time.time() - read_start) < 5.0:
                chunk = ser.read(min(4096, frame_len - len(jpeg_bytes)))
                if chunk:
                    jpeg_bytes.extend(chunk)

            ser.close()

            if len(jpeg_bytes) >= frame_len:
                return bytes(jpeg_bytes[:frame_len])
            return None

        except Exception as e:
            print(f"[ERROR] [CameraService] Serial capture failed on {port}: {e}")
            return None

    def capture(self, port: Optional[str] = None, ip_url: Optional[str] = None) -> str:
        """
        Triggers a fresh snapshot from either Serial or IP and saves it to snapshots/latest.jpg.
        """
        target_ip = ip_url or self.ip_url
        target_port = port or self.port
        jpeg_data = None

        if target_ip:
            jpeg_data = self.capture_from_ip(target_ip)
        elif target_port:
            jpeg_data = self.capture_from_serial(target_port)

        if jpeg_data:
            with open(LATEST_IMAGE_PATH, "wb") as f:
                f.write(jpeg_data)

            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            archive_path = os.path.join(ARCHIVE_DIR, f"plant_{timestamp}.jpg")
            with open(archive_path, "wb") as f:
                f.write(jpeg_data)

        return LATEST_IMAGE_PATH

    def get_latest_frame(self, as_numpy: bool = True):
        if not os.path.exists(LATEST_IMAGE_PATH):
            self.capture()

        if Image:
            try:
                pil_img = Image.open(LATEST_IMAGE_PATH).convert("RGB")
                if as_numpy and np:
                    return np.array(pil_img)
                return pil_img
            except Exception as e:
                print(f"❌ [CameraService] Error loading image: {e}")

        return None


# Global Singleton Instance
_camera_service = CameraService()


def capture_snapshot(port: Optional[str] = None, ip_url: Optional[str] = None) -> str:
    """Helper function to trigger an instant camera snapshot."""
    return _camera_service.capture(port=port, ip_url=ip_url)


def capture_from_ip(url: str, timeout: float = 5.0) -> Optional[bytes]:
    """Captures JPEG bytes from any IP camera URL."""
    return _camera_service.capture_from_ip(url, timeout=timeout)


def get_latest_frame(as_numpy: bool = True):
    return _camera_service.get_latest_frame(as_numpy=as_numpy)


def get_camera_status() -> dict:
    exists = os.path.exists(LATEST_IMAGE_PATH)
    mod_time = datetime.fromtimestamp(os.path.getmtime(LATEST_IMAGE_PATH)).isoformat() if exists else None
    size_bytes = os.path.getsize(LATEST_IMAGE_PATH) if exists else 0
    archive_count = len(glob.glob(os.path.join(ARCHIVE_DIR, "*.jpg")))

    return {
        "latestImagePath": LATEST_IMAGE_PATH,
        "available": exists,
        "lastCaptureTime": mod_time,
        "fileSizeBytes": size_bytes,
        "totalArchivedSnapshots": archive_count,
    }
