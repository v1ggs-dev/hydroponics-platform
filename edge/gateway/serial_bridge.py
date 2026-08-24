"""
Hydroponics Platform — Thread-Safe Serial Bridge
Manages resilient wired USB serial communication with the ESP32 controller.
"""

import time
import serial
import threading
import logging
from typing import Callable, Optional

logger = logging.getLogger("SerialBridge")

class SerialBridge:
    def __init__(self, port: str, baud: int = 115200, timeout: float = 0.1, on_line_callback: Optional[Callable[[str], None]] = None):
        self._port = port
        self._baud = baud
        self._timeout = timeout
        self._callback = on_line_callback

        self._ser: Optional[serial.Serial] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._write_lock = threading.Lock()

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, name="SerialBridgeThread", daemon=True)
        self._thread.start()
        logger.info(f"Serial Bridge started targeting {self._port} @ {self._baud} baud.")

    def stop(self):
        self._running = False
        if self._ser and self._ser.is_open:
            try:
                self._ser.close()
            except Exception:
                pass
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        logger.info("Serial Bridge stopped.")

    def send_command(self, cmd: str) -> bool:
        """Sends a command down the serial wire to the ESP32."""
        with self._write_lock:
            if not self._ser or not self._ser.is_open:
                logger.warning(f"Cannot send command '{cmd}': Serial port {self._port} is not open.")
                return False
            try:
                data = (cmd.strip() + "\r\n").encode("utf-8")
                self._ser.write(data)
                self._ser.flush()
                logger.info(f"Transmitted command to ESP32: '{cmd.strip()}'")
                return True
            except Exception as e:
                logger.error(f"Error transmitting command to ESP32: {e}")
                return False

    def is_connected(self) -> bool:
        return self._ser is not None and self._ser.is_open

    def _run_loop(self):
        while self._running:
            if not self._ser or not self._ser.is_open:
                try:
                    logger.info(f"Opening serial port {self._port} @ {self._baud} baud...")
                    self._ser = serial.Serial(self._port, self._baud, timeout=self._timeout)
                    logger.info(f"Successfully connected to ESP32 on {self._port}!")
                except Exception as e:
                    logger.warning(f"Failed to connect to {self._port}: {e}. Retrying in 3s...")
                    time.sleep(3.0)
                    continue

            try:
                if self._ser.in_waiting > 0:
                    raw_line = self._ser.readline().decode("utf-8", errors="replace").strip()
                    if raw_line and self._callback:
                        self._callback(raw_line)
                else:
                    time.sleep(0.01)
            except Exception as e:
                logger.warning(f"Serial read error on {self._port}: {e}. Reconnecting...")
                if self._ser:
                    try:
                        self._ser.close()
                    except Exception:
                        pass
                    self._ser = None
                time.sleep(2.0)
