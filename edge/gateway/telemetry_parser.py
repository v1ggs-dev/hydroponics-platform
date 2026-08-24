"""
Hydroponics Platform — Telemetry & Packet Parser
Parses, validates, and enriches raw ESP32 serial output into canonical messages.
"""

import json
import logging
import time
from typing import Optional, Dict, Any, Tuple

logger = logging.getLogger("TelemetryParser")

class TelemetryParser:
    PREFIX_TELEMETRY = "[TELEMETRY_JSON] "
    PREFIX_HEARTBEAT = "[HEARTBEAT_JSON] "

    @classmethod
    def parse_line(cls, raw_line: str) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Parses a single line from the ESP32 serial stream.
        Returns (packet_type, parsed_dict) or (None, None) if not a JSON payload.
        """
        line = raw_line.strip()
        if not line:
            return None, None

        # 1. Telemetry Payload
        if line.startswith(cls.PREFIX_TELEMETRY):
            json_str = line[len(cls.PREFIX_TELEMETRY):].strip()
            parsed = cls._parse_and_validate_telemetry(json_str)
            if parsed:
                return "telemetry", parsed

        # 2. Heartbeat Payload
        elif line.startswith(cls.PREFIX_HEARTBEAT):
            json_str = line[len(cls.PREFIX_HEARTBEAT):].strip()
            parsed = cls._parse_json(json_str)
            if parsed:
                return "heartbeat", parsed

        # 3. Handle raw JSON line without prefix (fallback)
        elif line.startswith("{") and line.endswith("}"):
            parsed = cls._parse_json(line)
            if parsed:
                msg_type = parsed.get("type", "telemetry")
                return msg_type, parsed

        return None, None

    @classmethod
    def _parse_and_validate_telemetry(cls, json_str: str) -> Optional[Dict[str, Any]]:
        """Validates canonical telemetry envelope structure."""
        data = cls._parse_json(json_str)
        if not data:
            return None

        # Verify mandatory fields conforming to docs/protocols/TELEMETRY.md
        if "deviceId" not in data or "measurements" not in data:
            logger.warning(f"Telemetry payload missing required fields: {json_str}")
            return None

        # Ensure UTC timestamp is added at edge ingestion layer
        if "receivedAt" not in data:
            data["receivedAt"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        return data

    @classmethod
    def _parse_json(cls, json_str: str) -> Optional[Dict[str, Any]]:
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON payload: {e} | Content: {json_str}")
            return None
