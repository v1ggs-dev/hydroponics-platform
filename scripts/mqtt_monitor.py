#!/usr/bin/env python3
"""
Hydroponics Platform — Live Wireless MQTT Telemetry Monitor & Remote CLI
Subscribes to hydroponics/# and publishes remote commands over MQTT.
"""

import sys
import json
import time
import threading
import paho.mqtt.client as mqtt

DEFAULT_BROKER_HOST = "localhost"
DEFAULT_BROKER_PORT = 1883
TOPIC_TELEMETRY = "hydroponics/esp32-01/telemetry"
TOPIC_STATUS    = "hydroponics/esp32-01/status"
TOPIC_COMMANDS  = "hydroponics/esp32-01/commands"
TOPIC_EVENTS    = "hydroponics/esp32-01/events"

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"\033[92m[MQTT] Connected successfully to broker at {client._host}:{client._port}!\033[0m")
        client.subscribe("hydroponics/#")
        print("[MQTT] Subscribed to all 'hydroponics/#' topics.\n")
    else:
        print(f"\033[91m[MQTT] Connection failed with code {rc}\033[0m")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode("utf-8", errors="replace")

    try:
        data = json.loads(payload)
        formatted_json = json.dumps(data, indent=2)
    except Exception:
        data = None
        formatted_json = payload

    if topic.endswith("/telemetry"):
        # Format human-readable summary line
        if data and "measurements" in data:
            metrics_summary = []
            for m in data.get("measurements", []):
                metric = m.get("metric", "")
                val = m.get("value")
                unit = m.get("unit", "")
                if val is not None:
                    metrics_summary.append(f"{metric}: {val} {unit}")
            
            uptime = data.get("uptimeSeconds", 0)
            msg_id = data.get("messageId", "")
            print(f"\r\033[96m[WIRELESS TELEMETRY]\033[0m ({msg_id} | Uptime: {uptime}s)")
            print(f"  \033[93m├── {' | '.join(metrics_summary)}\033[0m")
            print(f"  \033[90m└── Raw JSON: {payload}\033[0m\nMQTT > ", end="", flush=True)
        else:
            print(f"\r\033[96m[{topic}]\033[0m {payload}\nMQTT > ", end="", flush=True)

    elif topic.endswith("/status"):
        print(f"\r\033[95m[DEVICE STATUS]\033[0m {payload}\nMQTT > ", end="", flush=True)
    elif topic.endswith("/events"):
        print(f"\r\033[91m[URGENT ALARM EVENT]\033[0m {payload}\nMQTT > ", end="", flush=True)
    else:
        print(f"\r\033[94m[{topic}]\033[0m {payload}\nMQTT > ", end="", flush=True)

def main():
    broker = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BROKER_HOST
    port = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_BROKER_PORT

    print("\n" + "=" * 65)
    print("  📡 HYDROPONICS WIRELESS MQTT MONITOR & REMOTE CONTROLLER")
    print("=" * 65)
    print(f"  Connecting to broker at: {broker}:{port}")
    print("  Interactive Commands:")
    print("    [1] or 'on'     -> Publish Remote Command: PUMP ON")
    print("    [0] or 'off'    -> Publish Remote Command: PUMP OFF")
    print("    [t] or 'toggle' -> Publish Remote Command: PUMP TOGGLE")
    print("    [r] or 'reset'  -> Publish Remote Command: RESET FAULT")
    print("    [q] or 'exit'   -> Exit Monitor")
    print("=" * 65 + "\n")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="hydro_cli_monitor")
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(broker, port, 60)
    except Exception as e:
        print(f"\033[91m[Error] Could not connect to MQTT broker at {broker}:{port}: {e}\033[0m")
        print("*(Make sure the broker is running: run 'python scripts/start_mqtt_broker.py')*")
        return

    client.loop_start()

    time.sleep(0.5)

    cmd_seq = 0

    try:
        while True:
            try:
                user_input = input("MQTT > ").strip()
            except (EOFError, KeyboardInterrupt):
                break

            if not user_input:
                continue

            lowered = user_input.lower()
            if lowered in ["q", "exit", "quit"]:
                break

            cmd_seq += 1
            cmd_payload = None

            if lowered in ["1", "on", "pump on"]:
                cmd_payload = {
                    "commandId": f"cmd-{cmd_seq}",
                    "deviceId": "esp32-01",
                    "actuatorId": "pump-01",
                    "action": "SET_STATE",
                    "value": "ON",
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                }
            elif lowered in ["0", "off", "pump off"]:
                cmd_payload = {
                    "commandId": f"cmd-{cmd_seq}",
                    "deviceId": "esp32-01",
                    "actuatorId": "pump-01",
                    "action": "SET_STATE",
                    "value": "OFF",
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                }
            elif lowered in ["t", "toggle", "pump toggle"]:
                cmd_payload = {
                    "commandId": f"cmd-{cmd_seq}",
                    "deviceId": "esp32-01",
                    "actuatorId": "pump-01",
                    "action": "TOGGLE",
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                }
            elif lowered in ["r", "reset", "reset fault"]:
                cmd_payload = {
                    "commandId": f"cmd-{cmd_seq}",
                    "deviceId": "esp32-01",
                    "action": "RESET_FAULT",
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                }
            else:
                print(f"[Unknown] Type 1 (ON), 0 (OFF), t (TOGGLE), or r (RESET)")
                continue

            if cmd_payload:
                json_str = json.dumps(cmd_payload)
                client.publish(TOPIC_COMMANDS, json_str, qos=1)
                print(f"\033[92m[PUBLISHED COMMAND] -> {TOPIC_COMMANDS}: {json_str}\033[0m")
                time.sleep(0.1)

    finally:
        client.loop_stop()
        client.disconnect()
        print("\n[MQTT Monitor] Disconnected. Goodbye!\n")

if __name__ == "__main__":
    main()
