"""
Hydroponics Platform — Hardware-Free Telemetry Simulator
Generates realistic, fluctuating multi-node sensor telemetry (esp32-env & esp32-chem)
and streams over MQTT without needing physical ESP32 boards.
Allows full end-to-end UI design, WebSocket testing, and pump control verification.
"""

import os
import sys
import time
import math
import random
import json
import paho.mqtt.client as mqtt

from .banner import (
    Colors, print_header, print_section, print_menu_item,
    print_success, print_error, print_warning, print_info, prompt_choice, pause
)

class TelemetrySimulator:
    def __init__(self, host: str = "localhost", port: int = 1883):
        self.host = host
        self.port = port
        self.running = False
        self.pump_on = False
        self.total_volume = 12.4
        self.tick = 0
        self.profile = "OPTIMAL" # OPTIMAL, HEAT_STRESS, ACIDIC_PH, LOW_WATER

    def start_simulation(self):
        print_header("Hardware-Free Telemetry Simulator", "Live Multi-Node Virtual Hydroponics Farm")
        print(f"  {Colors.BOLD}Simulation Profile:{Colors.RESET} {Colors.BRIGHT_GREEN}{self.profile}{Colors.RESET}")
        print(f"  {Colors.BOLD}Target MQTT Broker:{Colors.RESET} {self.host}:{self.port}")
        print(f"  {Colors.DIM}Streams realistic dynamic sensor telemetry for esp32-env and esp32-chem.{Colors.RESET}")
        print(f"  {Colors.BRIGHT_YELLOW}Press [Ctrl+C] to stop simulator.{Colors.RESET}\n")

        client = mqtt.Client(client_id="hydro-hardware-simulator")

        def on_connect(c, userdata, flags, rc):
            if rc == 0:
                print_success("Simulator connected to MQTT broker! Listening for remote UI commands...")
                c.subscribe("hydroponics/+/commands")
            else:
                print_error(f"Failed to connect to broker. Code: {rc}")

        def on_message(c, userdata, msg):
            try:
                payload = json.loads(msg.payload.decode("utf-8"))
                action = payload.get("action", "").upper()
                value = str(payload.get("value", "")).upper()
                print(f"  {Colors.BRIGHT_YELLOW}⚡ [REMOTE COMMAND FROM UI]{Colors.RESET} {action}: {value}")

                if action in ["SET_STATE", "PUMP"]:
                    if value in ["ON", "1", "TRUE"]:
                        self.pump_on = True
                        print_success("Virtual Submersible Pump switched: ON")
                    elif value in ["OFF", "0", "FALSE"]:
                        self.pump_on = False
                        print_warning("Virtual Submersible Pump switched: OFF")
                elif action == "TOGGLE":
                    self.pump_on = not self.pump_on
                    print_info(f"Virtual Pump toggled to: {'ON' if self.pump_on else 'OFF'}")
            except Exception as e:
                print_error(f"Error parsing command: {e}")

        client.on_connect = on_connect
        client.on_message = on_message

        try:
            client.connect(self.host, self.port, keepalive=60)
            client.loop_start()
            self.running = True

            while self.running:
                self.tick += 1
                t = self.tick * 0.1

                # Calculate smooth realistic sensor values
                if self.profile == "OPTIMAL":
                    temp_c = 23.5 + 1.2 * math.sin(t * 0.2) + random.uniform(-0.1, 0.1)
                    humidity = 68.0 + 3.5 * math.cos(t * 0.15) + random.uniform(-0.3, 0.3)
                    ph_val = 6.15 + 0.15 * math.sin(t * 0.08) + random.uniform(-0.02, 0.02)
                    tds_ppm = 560.0 + 15.0 * math.cos(t * 0.05) + random.uniform(-2.0, 2.0)
                    moist_pct = 58.0 + 2.0 * math.sin(t * 0.1) + random.uniform(-0.2, 0.2)

                elif self.profile == "HEAT_STRESS":
                    temp_c = 34.8 + random.uniform(-0.3, 0.4)
                    humidity = 42.0 + random.uniform(-0.5, 0.5)
                    ph_val = 6.4 + random.uniform(-0.05, 0.05)
                    tds_ppm = 620.0 + random.uniform(-3.0, 3.0)
                    moist_pct = 32.0 + random.uniform(-0.5, 0.5)

                elif self.profile == "ACIDIC_PH":
                    temp_c = 24.0 + random.uniform(-0.1, 0.1)
                    humidity = 65.0 + random.uniform(-0.2, 0.2)
                    ph_val = 4.85 + random.uniform(-0.04, 0.04) # Trigger acidic alert
                    tds_ppm = 780.0 + random.uniform(-2.0, 2.0)
                    moist_pct = 62.0 + random.uniform(-0.3, 0.3)

                # Flow dynamics
                if self.pump_on:
                    flow_lpm = 2.45 + random.uniform(-0.08, 0.08)
                    self.total_volume += (flow_lpm / 60.0) * 2.0 # 2-second interval integration
                else:
                    flow_lpm = 0.0

                # 1. Build and publish Node 1 Telemetry (esp32-env)
                env_payload = {
                    "deviceId": "esp32-env",
                    "sequence": self.tick,
                    "uptimeSeconds": self.tick * 2,
                    "freeHeap": 284500,
                    "pump": "ON" if self.pump_on else "OFF",
                    "autoWater": True,
                    "dryRunLockout": False,
                    "measurements": [
                        {"sensorId": "dht11-01", "metric": "air_temperature", "value": round(temp_c, 1), "unit": "C", "quality": "GOOD"},
                        {"sensorId": "dht11-01", "metric": "humidity", "value": round(humidity, 1), "unit": "%", "quality": "GOOD"},
                        {"sensorId": "flow-01", "metric": "flow_rate", "value": round(flow_lpm, 2), "unit": "L/min", "quality": "GOOD"},
                        {"sensorId": "flow-01", "metric": "water_volume", "value": round(self.total_volume, 2), "unit": "L", "quality": "GOOD"}
                    ]
                }
                client.publish("hydroponics/esp32-env/telemetry", json.dumps(env_payload))

                # 2. Build and publish Node 2 Telemetry (esp32-chem)
                chem_payload = {
                    "deviceId": "esp32-chem",
                    "sequence": self.tick,
                    "uptimeSeconds": self.tick * 2,
                    "freeHeap": 289100,
                    "measurements": [
                        {"sensorId": "ph-01", "metric": "ph", "value": round(ph_val, 2), "unit": "pH", "quality": "GOOD"},
                        {"sensorId": "tds-01", "metric": "tds", "value": round(tds_ppm, 0), "unit": "ppm", "quality": "GOOD"},
                        {"sensorId": "moisture-01", "metric": "substrate_moisture", "value": round(moist_pct, 1), "unit": "%", "quality": "GOOD"}
                    ]
                }
                client.publish("hydroponics/esp32-chem/telemetry", json.dumps(chem_payload))

                # Console log
                pump_str = f"{Colors.BRIGHT_GREEN}PUMP: ON{Colors.RESET}" if self.pump_on else f"{Colors.DIM}PUMP: OFF{Colors.RESET}"
                print(f"[{time.strftime('%H:%M:%S')}] Temp: {temp_c:.1f}°C | Hum: {humidity:.1f}% | pH: {ph_val:.2f} | TDS: {tds_ppm:.0f} ppm | Flow: {flow_lpm:.2f} L/m | {pump_str}")

                time.sleep(2.0)

        except KeyboardInterrupt:
            print_warning("\nStopping Telemetry Simulator...")
        finally:
            client.loop_stop()
            client.disconnect()
            print_success("Simulator stopped.")

def simulator_menu():
    """Interactive Simulator Menu."""
    sim = TelemetrySimulator()
    while True:
        print_header("Hardware-Free Telemetry Simulator", "Test & Rework UI Without Physical Hardware")
        print_menu_item("1", "Start Optimal Growth Simulation", "Normal fluctuations: 23°C, 68%, pH 6.2, 560 ppm")
        print_menu_item("2", "Start Heat Stress Simulation", "High temp: 35°C, Low moisture: 32% (Tests alarms)")
        print_menu_item("3", "Start Acidic pH Simulation", "Low pH: 4.85 pH (Tests fuchsia/acidic warning card)")
        print_menu_item("0", "Return to Main Menu")

        choice = prompt_choice()
        if choice == "1":
            sim.profile = "OPTIMAL"
            sim.start_simulation()
            pause()
        elif choice == "2":
            sim.profile = "HEAT_STRESS"
            sim.start_simulation()
            pause()
        elif choice == "3":
            sim.profile = "ACIDIC_PH"
            sim.start_simulation()
            pause()
        elif choice == "0":
            break
