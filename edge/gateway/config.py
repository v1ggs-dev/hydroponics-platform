"""
Hydroponics Platform — Edge Gateway Configuration
Loads and manages configuration parameters for the Edge Gateway service.
Supports Multi-ESP32 Serial Ingestion (e.g., esp32-env & esp32-chem).
"""

import os
import sys
from typing import List
import serial.tools.list_ports

class GatewayConfig:
    # Serial Port Settings
    # Can be a comma-separated list: "COM6,COM8" or single "COM6"
    SERIAL_PORTS_ENV = os.getenv("GATEWAY_SERIAL_PORTS", os.getenv("GATEWAY_SERIAL_PORT", ""))
    SERIAL_BAUD = int(os.getenv("GATEWAY_SERIAL_BAUD", "115200"))
    SERIAL_TIMEOUT = float(os.getenv("GATEWAY_SERIAL_TIMEOUT", "0.1"))
    SERIAL_RECONNECT_DELAY = float(os.getenv("GATEWAY_SERIAL_RECONNECT_DELAY", "3.0"))

    # MQTT Settings
    MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
    MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
    MQTT_CLIENT_ID = os.getenv("GATEWAY_MQTT_CLIENT_ID", "hydro-edge-gateway")
    MQTT_USERNAME = os.getenv("MQTT_USERNAME", "")
    MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
    MQTT_KEEPALIVE = int(os.getenv("MQTT_KEEPALIVE", "60"))

    # Topic Templates
    DEFAULT_DEVICE_ID = os.getenv("DEFAULT_DEVICE_ID", "esp32-01")
    TOPIC_TELEMETRY = "hydroponics/{deviceId}/telemetry"
    TOPIC_STATUS    = "hydroponics/{deviceId}/status"
    TOPIC_COMMANDS  = "hydroponics/{deviceId}/commands"
    TOPIC_EVENTS    = "hydroponics/{deviceId}/events"
    TOPIC_EDGE_HEALTH = "hydroponics/edge/health"

    # Offline Buffer Settings
    BUFFER_DB_PATH = os.getenv("BUFFER_DB_PATH", "edge_telemetry_buffer.db")
    BUFFER_MAX_RECORDS = int(os.getenv("BUFFER_MAX_RECORDS", "10000"))
    BUFFER_FLUSH_BATCH_SIZE = int(os.getenv("BUFFER_FLUSH_BATCH_SIZE", "50"))

    @classmethod
    def resolve_serial_ports(cls) -> List[str]:
        """Resolves list of active serial ports for all connected ESP32 controllers."""
        if cls.SERIAL_PORTS_ENV:
            ports = [p.strip() for p in cls.SERIAL_PORTS_ENV.split(",") if p.strip()]
            if ports:
                return ports

        discovered = []
        com_ports = list(serial.tools.list_ports.comports())
        for p in com_ports:
            desc = p.description.lower()
            # Filter CP210x, CH340, USB-to-UART, FTDI
            if any(k in desc for k in ["cp210", "ch340", "ftdi", "uart", "esp32", "usb to uart", "usb serial"]):
                discovered.append(p.device)
            elif "ttyusb" in p.device.lower() or "ttyacm" in p.device.lower():
                discovered.append(p.device)

        if discovered:
            return discovered

        fallback = ["COM6"] if sys.platform == "win32" else ["/dev/ttyUSB0"]
        return fallback

    @classmethod
    def resolve_serial_port(cls) -> str:
        """Backwards compatible single-port resolver."""
        ports = cls.resolve_serial_ports()
        return ports[0] if ports else ("COM6" if sys.platform == "win32" else "/dev/ttyUSB0")
