#!/usr/bin/env python3
"""
Hydroponics Platform — Continuous Live Camera Stream Service
Continuously captures frames from the wired ESP32-CAM (COM9) and writes to snapshots/latest.jpg.
"""

import os
import sys
import time
import signal
import serial

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from edge.camera.camera_service import LATEST_IMAGE_PATH, ARCHIVE_DIR

running = True

def signal_handler(sig, frame):
    global running
    print("\n[Camera Stream] Stopping live camera stream...")
    running = False

signal.signal(signal.SIGINT, signal_handler)

def main():
    port = sys.argv[1] if len(sys.argv) > 1 else "COM9"
    baudrate = 115200

    print("\n" + "=" * 65)
    print("  📷 HYDROPONICS WIRED ESP32-CAM LIVE STREAM SERVICE")
    print(f"  Port: {port} | Target: snapshots/latest.jpg")
    print("=" * 65 + "\n")

    try:
        ser = serial.Serial(port=port, baudrate=baudrate, timeout=1.0)
        ser.dtr = False
        ser.rts = False
        time.sleep(2.0)
        ser.reset_input_buffer()
        print(f"[OK] Connected to ESP32-CAM on {port}. Starting stream loop...\n")
    except Exception as e:
        print(f"[ERROR] Could not open {port}: {e}")
        return

    frame_count = 0
    start_stream_time = time.time()

    while running:
        try:
            ser.write(b"CAPTURE\n")
            ser.flush()

            # Read frame header
            start_t = time.time()
            frame_len = 0
            header_found = False

            while (time.time() - start_t) < 3.0:
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

            if header_found and frame_len > 0:
                jpeg_bytes = bytearray()
                read_t = time.time()
                while len(jpeg_bytes) < frame_len and (time.time() - read_t) < 4.0:
                    chunk = ser.read(min(4096, frame_len - len(jpeg_bytes)))
                    if chunk:
                        jpeg_bytes.extend(chunk)

                if len(jpeg_bytes) >= frame_len:
                    # Write latest frame atomically
                    temp_path = LATEST_IMAGE_PATH + ".tmp"
                    with open(temp_path, "wb") as f:
                        f.write(jpeg_bytes[:frame_len])
                    os.replace(temp_path, LATEST_IMAGE_PATH)

                    frame_count += 1
                    fps = frame_count / (time.time() - start_stream_time)
                    print(f"\r[STREAM] Live Frame #{frame_count:04d} | Size: {frame_len/1024:.1f} KB | Rate: {fps:.2f} FPS", end="", flush=True)

            # Small yield to prevent serial line congestion
            time.sleep(0.1)

        except Exception as e:
            print(f"\n[STREAM ERROR]: {e}")
            time.sleep(1.0)

    try:
        ser.close()
    except Exception:
        pass
    print("\n[OK] Camera stream terminated.")

if __name__ == "__main__":
    main()
