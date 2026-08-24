"""
Hydroponics Platform — MQTT Edge Bridge
Publishes normalized telemetry and dispatches remote commands over MQTT.
"""

import json
import logging
import time
from typing import Callable, Optional, Dict, Any
import paho.mqtt.client as mqtt

logger = logging.getLogger("MQTTBridge")

class MQTTBridge:
    def __init__(self,
                 host: str,
                 port: int = 1883,
                 client_id: str = "hydro-edge-gateway",
                 username: str = "",
                 password: str = "",
                 on_command_callback: Optional[Callable[[Dict[str, Any]], None]] = None):
        self._host = host
        self._port = port
        self._client_id = client_id
        self._username = username
        self._password = password
        self._command_callback = on_command_callback

        self._client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=self._client_id)
        if self._username:
            self._client.username_pw_set(self._username, self._password)

        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message

        # Set Last Will and Testament
        lwt_payload = json.dumps({"gatewayId": self._client_id, "status": "OFFLINE", "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        self._client.will_set("hydroponics/edge/status", lwt_payload, qos=1, retain=True)

        self._connected = False

    def start(self):
        try:
            logger.info(f"Connecting to MQTT broker at {self._host}:{self._port}...")
            self._client.connect(self._host, self._port, keepalive=60)
            self._client.loop_start()
        except Exception as e:
            logger.error(f"MQTT connection initiation failed: {e}")

    def stop(self):
        self.publish_status("OFFLINE")
        self._client.loop_stop()
        self._client.disconnect()
        logger.info("MQTT Bridge stopped.")

    def is_connected(self) -> bool:
        return self._connected

    def publish_telemetry(self, topic: str, data: Dict[str, Any]) -> bool:
        if not self._connected:
            return False
        try:
            payload = json.dumps(data)
            res = self._client.publish(topic, payload, qos=1)
            return res.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            logger.error(f"Failed to publish telemetry to {topic}: {e}")
            return False

    def publish_status(self, status: str):
        if not self._connected:
            return
        payload = json.dumps({
            "gatewayId": self._client_id,
            "status": status,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        })
        self._client.publish("hydroponics/edge/status", payload, qos=1, retain=True)

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self._connected = True
            logger.info(f"Connected to MQTT broker at {self._host}:{self._port}!")
            self.publish_status("ONLINE")
            # Subscribe to all commands for all devices
            self._client.subscribe("hydroponics/+/commands", qos=1)
            logger.info("Subscribed to 'hydroponics/+/commands'")
        else:
            self._connected = False
            logger.warning(f"MQTT connection returned code {rc}")

    def _on_disconnect(self, client, userdata, flags, rc, properties=None):
        self._connected = False
        logger.warning(f"Disconnected from MQTT broker (rc={rc})")

    def _on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode("utf-8", errors="replace")
        logger.info(f"Received MQTT command on '{topic}': {payload}")

        if self._command_callback:
            try:
                data = json.loads(payload)
                self._command_callback(data)
            except Exception as e:
                logger.error(f"Failed to parse inbound command JSON: {e}")
