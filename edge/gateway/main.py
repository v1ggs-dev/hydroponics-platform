#!/usr/bin/env python3
"""
Hydroponics Platform — Edge Gateway Service (Main Entrypoint)
Runs on Raspberry Pi 5 (or Windows PC during development).
Bridges Wired Multi-ESP32 Serial (esp32-env, esp32-chem) <-> MQTT Message Broker with Offline Buffering.
"""

import sys
import time
import signal
import logging
import psutil
from typing import Dict, Any, List

from config import GatewayConfig
from serial_bridge import SerialBridge
from telemetry_parser import TelemetryParser
from storage_buffer import StorageBuffer
from mqtt_bridge import MQTTBridge

# Setup colorful logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("EdgeGateway")

class EdgeGatewayService:
    def __init__(self):
        self._running = False
        self._serial_ports: List[str] = GatewayConfig.resolve_serial_ports()
        self._baud = GatewayConfig.SERIAL_BAUD

        logger.info("Initializing Hydroponics Multi-Node Edge Gateway...")
        logger.info(f"Target Serial Ports: {', '.join(self._serial_ports)} @ {self._baud} baud")
        logger.info(f"Target MQTT Broker: {GatewayConfig.MQTT_HOST}:{GatewayConfig.MQTT_PORT}")

        # 1. Offline Storage Buffer
        self._buffer = StorageBuffer(
            db_path=GatewayConfig.BUFFER_DB_PATH,
            max_records=GatewayConfig.BUFFER_MAX_RECORDS
        )

        # 2. Multi-Serial Bridges
        self._bridges: List[SerialBridge] = []
        for port in self._serial_ports:
            bridge = SerialBridge(
                port=port,
                baud=self._baud,
                on_line_callback=lambda line, p=port: self._handle_serial_line(line, p)
            )
            self._bridges.append(bridge)

        # 3. MQTT Bridge
        self._mqtt = MQTTBridge(
            host=GatewayConfig.MQTT_HOST,
            port=GatewayConfig.MQTT_PORT,
            client_id=GatewayConfig.MQTT_CLIENT_ID,
            username=GatewayConfig.MQTT_USERNAME,
            password=GatewayConfig.MQTT_PASSWORD,
            on_command_callback=self._handle_inbound_mqtt_command
        )

        self._last_health_report = 0

    def start(self):
        self._running = True
        logger.info("Starting Edge Gateway multi-serial & MQTT services...")
        for bridge in self._bridges:
            bridge.start()
        self._mqtt.start()

        print("\n" + "=" * 65)
        print("  🌿 HYDROPONICS MULTI-NODE EDGE GATEWAY RUNNING")
        print("=" * 65)
        for bridge in self._bridges:
            print(f"  Serial Bridge:    {bridge._port} (Active)")
        print(f"  MQTT Broker:      {GatewayConfig.MQTT_HOST}:{GatewayConfig.MQTT_PORT}")
        print(f"  Offline Buffer:   {GatewayConfig.BUFFER_DB_PATH} ({self._buffer.get_pending_count()} pending)")
        print("  Status:           READY & MONITORING")
        print("=" * 65 + "\n")

        while self._running:
            try:
                # 1. Flush offline buffer if MQTT is connected
                if self._mqtt.is_connected():
                    self._flush_offline_buffer()

                # 2. Periodic Edge Health heartbeat (Every 60s)
                now = time.time()
                if now - self._last_health_report >= 60:
                    self._last_health_report = now
                    self._publish_edge_health()

                time.sleep(0.1)
            except KeyboardInterrupt:
                break

        self.stop()

    def stop(self):
        if not self._running:
            return
        logger.info("Shutting down Edge Gateway gracefully...")
        self._running = False
        for bridge in self._bridges:
            bridge.stop()
        self._mqtt.stop()
        logger.info("Edge Gateway shutdown complete.")

    def _handle_serial_line(self, raw_line: str, port: str):
        """Processes incoming line from an ESP32 serial stream."""
        msg_type, payload = TelemetryParser.parse_line(raw_line)

        if msg_type == "telemetry" and payload:
            device_id = payload.get("deviceId", GatewayConfig.DEFAULT_DEVICE_ID)
            topic = f"hydroponics/{device_id}/telemetry"

            # Print readable summary to console
            metrics_summary = []
            for m in payload.get("measurements", []):
                metric = m.get("metric", "")
                val = m.get("value")
                unit = m.get("unit", "")
                if val is not None:
                    metrics_summary.append(f"{metric}: {val} {unit}")
            
            uptime = payload.get("uptimeSeconds", 0)
            print(f"\033[96m[EDGE TELEMETRY INGESTED]\033[0m (Port: {port} | Device: {device_id} | Uptime: {uptime}s)")
            print(f"  \033[93m└── {' | '.join(metrics_summary)}\033[0m")

            # Route to MQTT or Buffer
            if self._mqtt.is_connected():
                success = self._mqtt.publish_telemetry(topic, payload)
                if not success:
                    self._buffer.push(topic, payload)
            else:
                self._buffer.push(topic, payload)
                logger.info(f"MQTT offline. Buffered telemetry. Total pending: {self._buffer.get_pending_count()}")

        elif msg_type == "heartbeat" and payload:
            device_id = payload.get("deviceId", GatewayConfig.DEFAULT_DEVICE_ID)
            topic = f"hydroponics/{device_id}/heartbeat"
            if self._mqtt.is_connected():
                self._mqtt.publish_telemetry(topic, payload)

        else:
            # Informational / debug output from ESP32
            if raw_line.startswith("[SYSTEM]") or raw_line.startswith("[PUMP]") or raw_line.startswith("[CMD") or raw_line.startswith("[CHEM"):
                print(f"  \033[90m[{port}] {raw_line}\033[0m")

    def _handle_inbound_mqtt_command(self, cmd_dict: Dict[str, Any]):
        """Dispatches an incoming MQTT command down to all connected ESP32s."""
        logger.info(f"Dispatching remote command to ESP32s: {cmd_dict}")

        action = cmd_dict.get("action", "").upper()
        actuator_id = cmd_dict.get("actuatorId", cmd_dict.get("target", "")).lower()
        value = str(cmd_dict.get("value", "")).upper()

        cmd_to_send = None

        if action in ["SET_STATE", "PUMP"]:
            if value in ["ON", "1", "TRUE"]:
                cmd_to_send = "1"
            elif value in ["OFF", "0", "FALSE"]:
                cmd_to_send = "0"
        elif action == "TOGGLE":
            cmd_to_send = "t"
        elif action in ["RESET", "RESET_FAULT", "CLEAR_FAULT"]:
            cmd_to_send = "r"
        elif action in ["AUTO_ON", "AUTO"]:
            cmd_to_send = "a"
        elif action in ["AUTO_OFF"]:
            cmd_to_send = "d"

        if cmd_to_send:
            for bridge in self._bridges:
                if bridge.is_connected():
                    bridge.send_command(cmd_to_send)
            logger.info(f"Dispatched command '{cmd_to_send}' to all active serial bridges.")
        else:
            logger.warning(f"Unrecognized command format: {cmd_dict}")

    def _flush_offline_buffer(self):
        batch = self._buffer.peek_batch(limit=GatewayConfig.BUFFER_FLUSH_BATCH_SIZE)
        if not batch:
            return

        sent_ids = []
        for r_id, topic, payload in batch:
            if self._mqtt.publish_telemetry(topic, payload):
                sent_ids.append(r_id)
            else:
                break

        if sent_ids:
            self._buffer.delete_batch(sent_ids)
            logger.info(f"Flushed {len(sent_ids)} buffered telemetry records to MQTT broker.")

    def _publish_edge_health(self):
        health_payload = {
            "gatewayId": GatewayConfig.MQTT_CLIENT_ID,
            "serialPorts": self._serial_ports,
            "bridgesActive": sum(1 for b in self._bridges if b.is_connected()),
            "cpuPercent": psutil.cpu_percent(),
            "ramPercent": psutil.virtual_memory().percent,
            "pendingBufferedRecords": self._buffer.get_pending_count(),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        self._mqtt.publish_telemetry(GatewayConfig.TOPIC_EDGE_HEALTH, health_payload)

def main():
    service = EdgeGatewayService()

    def sig_handler(sig, frame):
        service.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    service.start()

if __name__ == "__main__":
    main()
