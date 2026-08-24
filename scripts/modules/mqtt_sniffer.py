"""
Hydroponics Platform — Live MQTT Sniffer & Stream Inspector
Subscribes to hydroponics/# and renders parsed, color-coded telemetry and status packets.
"""

import os
import sys
import json
import time
import paho.mqtt.client as mqtt

from .banner import (
    Colors, print_header, print_section, print_menu_item,
    print_success, print_error, print_warning, print_info, prompt_choice, pause
)

class MQTTSniffer:
    @staticmethod
    def run_sniffer(host: str = "localhost", port: int = 1883, topic: str = "hydroponics/#"):
        """Subscribes and streams MQTT messages."""
        print_header("Live MQTT Topic Sniffer", f"Broker: {host}:{port} | Topic: {topic}")
        print_info("Press [Ctrl+C] to stop sniffing.\n")

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print_success(f"Connected to MQTT Broker! Subscribed to '{topic}'.")
                client.subscribe(topic)
            else:
                print_error(f"Failed to connect to MQTT broker. Code: {rc}")

        def on_message(client, userdata, msg):
            payload_str = msg.payload.decode("utf-8", errors="replace")
            topic_str = msg.topic

            # Colorize based on topic
            if "telemetry" in topic_str:
                topic_color = Colors.BRIGHT_CYAN
            elif "status" in topic_str:
                topic_color = Colors.BRIGHT_GREEN
            elif "commands" in topic_str:
                topic_color = Colors.BRIGHT_YELLOW
            elif "events" in topic_str:
                topic_color = Colors.BRIGHT_RED
            else:
                topic_color = Colors.WHITE

            try:
                data = json.loads(payload_str)
                formatted_json = json.dumps(data, indent=2)
                print(f"{Colors.BOLD}{topic_color}📥 [{time.strftime('%H:%M:%S')}] {topic_str}{Colors.RESET}")
                print(f"{Colors.DIM}{formatted_json}{Colors.RESET}\n")
            except Exception:
                print(f"{Colors.BOLD}{topic_color}📥 [{time.strftime('%H:%M:%S')}] {topic_str}:{Colors.RESET} {payload_str}")

        client = mqtt.Client(client_id="hydro-mqtt-sniffer")
        client.on_connect = on_connect
        client.on_message = on_message

        try:
            client.connect(host, port, keepalive=60)
            client.loop_forever()
        except KeyboardInterrupt:
            print_warning("\nStopping MQTT Sniffer...")
            client.disconnect()
            print_success("Sniffer disconnected.")
        except Exception as e:
            print_error(f"MQTT Error: {e}")

def sniffer_menu():
    """Interactive Sniffer Menu."""
    while True:
        print_header("MQTT Sniffer Menu")
        print_menu_item("1", "Sniff Local Broker (localhost:1883)", "Listen to all hydroponics/# topics")
        print_menu_item("0", "Return to Main Menu")

        choice = prompt_choice()
        if choice == "1":
            MQTTSniffer.run_sniffer()
            pause()
        elif choice == "0":
            break
