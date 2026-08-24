"""
Hydroponics Platform — Full-Stack Service Orchestrator
Manages launching, monitoring, and providing live interactive controls for background services.
"""

import os
import sys
import time
import signal
import subprocess
import webbrowser
import requests
import psutil
from typing import List, Dict, Optional

from .banner import (
    Colors, print_header, print_section, print_menu_item,
    print_success, print_error, print_warning, print_info, prompt_choice, pause
)

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

class ServiceDefinition:
    def __init__(self, name: str, cmd: List[str], cwd: str, port: Optional[int] = None, color: str = Colors.WHITE):
        self.name = name
        self.cmd = cmd
        self.cwd = cwd
        self.port = port
        self.color = color
        self.process: Optional[subprocess.Popen] = None

class StackManager:
    def __init__(self):
        self.services: Dict[str, ServiceDefinition] = {
            "broker": ServiceDefinition(
                name="MQTT Message Broker",
                cmd=[sys.executable, os.path.join(ROOT_DIR, "scripts", "start_mqtt_broker.py")],
                cwd=ROOT_DIR,
                port=1883,
                color=Colors.BRIGHT_MAGENTA
            ),
            "gateway": ServiceDefinition(
                name="Multi-Node Edge Gateway",
                cmd=[sys.executable, os.path.join(ROOT_DIR, "scripts", "start_edge_gateway.py")],
                cwd=ROOT_DIR,
                color=Colors.BRIGHT_CYAN
            ),
            "simulator": ServiceDefinition(
                name="Telemetry Hardware Simulator",
                cmd=[sys.executable, os.path.join(ROOT_DIR, "scripts", "modules", "simulator.py")],
                cwd=ROOT_DIR,
                color=Colors.BRIGHT_CYAN
            ),
            "backend": ServiceDefinition(
                name="Cloud Backend & API Server",
                cmd=[sys.executable, os.path.join(ROOT_DIR, "scripts", "start_backend.py")],
                cwd=ROOT_DIR,
                port=4000,
                color=Colors.BRIGHT_GREEN
            ),
            "ai": ServiceDefinition(
                name="AgroEye AI Microservice & Dashboard",
                cmd=[sys.executable, os.path.join(ROOT_DIR, "scripts", "start_ai_service.py")],
                cwd=ROOT_DIR,
                port=8000,
                color=Colors.BRIGHT_CYAN
            ),
            "frontend": ServiceDefinition(
                name="Next.js Web Dashboard",
                cmd=[sys.executable, os.path.join(ROOT_DIR, "scripts", "start_frontend.py")],
                cwd=ROOT_DIR,
                port=3000,
                color=Colors.BRIGHT_BLUE
            ),
            "camera": ServiceDefinition(
                name="ESP32-CAM Video Stream",
                cmd=[sys.executable, os.path.join(ROOT_DIR, "scripts", "start_camera_stream.py")],
                cwd=ROOT_DIR,
                port=8080,
                color=Colors.BRIGHT_YELLOW
            ),
        }

        self.pump_state = False
        self.auto_mode = True

    @staticmethod
    def kill_process_on_port(port: int) -> bool:
        """Kills any process listening on the specified network port."""
        killed = False
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                for conn in proc.connections(kind="inet"):
                    if conn.laddr and conn.laddr.port == port:
                        print_warning(f"Port {port} in use by PID {proc.pid} ({proc.name()}). Terminating...")
                        proc.terminate()
                        try:
                            proc.wait(timeout=2.0)
                        except psutil.TimeoutExpired:
                            proc.kill()
                        killed = True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return killed

    def clean_all_ports(self):
        """Frees all project-related ports."""
        print_section("Cleaning Up Network Ports")
        ports = [1883, 3000, 4000, 5555, 8000, 8080]
        cleaned = 0
        for p in ports:
            if self.kill_process_on_port(p):
                cleaned += 1
                print_success(f"Port {p} successfully freed.")
            else:
                print_info(f"Port {p} is clear.")
        if cleaned == 0:
            print_success("All standard platform ports are clear!")

    def start_service(self, key: str, blocking: bool = True):
        """Starts an individual service."""
        if key not in self.services:
            print_error(f"Unknown service: {key}")
            return

        svc = self.services[key]
        if svc.port:
            self.kill_process_on_port(svc.port)

        print_header(f"Starting {svc.name}")
        try:
            p = subprocess.Popen(svc.cmd, cwd=svc.cwd)
            svc.process = p
            print_success(f"{svc.name} is running (PID: {p.pid})")
            if blocking:
                p.wait()
        except KeyboardInterrupt:
            print_warning(f"\nStopping {svc.name}...")
            if svc.process:
                svc.process.terminate()
                svc.process.wait()
            print_success(f"{svc.name} stopped.")

    def _dispatch_command(self, action: str, value: Optional[str] = None):
        """Dispatches an actuator command via backend API."""
        try:
            payload = {
                "deviceId": "esp32-env",
                "actuatorId": "pump-01",
                "action": action,
            }
            if value is not None:
                payload["value"] = value

            res = requests.post("http://localhost:4000/api/v1/commands", json=payload, timeout=3.0)
            if res.status_code == 200:
                print_success(f"Command dispatched: {action} {value or ''} -> esp32-env (Status 200 OK)")
            else:
                print_warning(f"Backend response: {res.status_code} - {res.text}")
        except Exception as e:
            print_error(f"Failed to dispatch command: {e}")

    def _show_telemetry_snapshot(self):
        """Fetches and displays live telemetry snapshot in the terminal."""
        try:
            res = requests.get("http://localhost:4000/api/v1/telemetry/latest?deviceId=all", timeout=3.0)
            if res.status_code == 200:
                data = res.json().get("data", {})
                if not data:
                    print_warning("No sensor telemetry received yet. Waiting for ESP32...")
                    return

                temp = data.get("air_temperature", {}).get("value", "--")
                hum = data.get("humidity", {}).get("value", "--")
                flow = data.get("flow_rate", {}).get("value", "--")
                vol = data.get("water_volume", {}).get("value", "--")
                ph = data.get("ph", {}).get("value", "--")
                tds = data.get("tds", {}).get("value", "--")
                moist = data.get("substrate_moisture", {}).get("value", "--")

                print(f"\n{Colors.BRIGHT_CYAN}+---------------------------------------------------------------+{Colors.RESET}")
                print(f"{Colors.BRIGHT_CYAN}|                LIVE SENSOR TELEMETRY SNAPSHOT                 |{Colors.RESET}")
                print(f"{Colors.BRIGHT_CYAN}+-------------------------------+-------------------------------+{Colors.RESET}")
                print(f"  {Colors.BOLD}Node 1 (Environment):{Colors.RESET}         |   {Colors.BOLD}Node 2 (Water Chemistry):{Colors.RESET}")
                print(f"  Air Temp:    {Colors.BRIGHT_GREEN}{temp} °C{Colors.RESET}          |   pH Level:    {Colors.BRIGHT_MAGENTA}{ph} pH{Colors.RESET}")
                print(f"  Humidity:    {Colors.BRIGHT_GREEN}{hum} %{Colors.RESET}           |   TDS/EC:      {Colors.BRIGHT_BLUE}{tds} ppm{Colors.RESET}")
                print(f"  Water Flow:  {Colors.BRIGHT_GREEN}{flow} L/min{Colors.RESET}      |   Moisture:    {Colors.BRIGHT_YELLOW}{moist} %{Colors.RESET}")
                print(f"  Total Vol:   {Colors.BRIGHT_GREEN}{vol} L{Colors.RESET}          |")
                print(f"{Colors.BRIGHT_CYAN}+-------------------------------+-------------------------------+{Colors.RESET}\n")
            else:
                print_warning(f"Could not reach backend on port 4000 (HTTP {res.status_code})")
        except Exception as e:
            print_error(f"Error reading telemetry snapshot: {e}")

    def _trigger_ai_leaf_scan(self):
        """Triggers AI leaf pathology diagnosis via AgroEye AI service."""
        print_info("Capturing latest camera snapshot for AI Pathology analysis...")
        snapshot_path = os.path.join(ROOT_DIR, "edge", "camera", "snapshots", "latest.jpg")
        
        if not os.path.exists(snapshot_path):
            print_warning("No optical camera snapshot found at edge/camera/snapshots/latest.jpg")
            print_info("You can also run leaf scans directly on the web dashboard using your webcam!")
            return

        try:
            with open(snapshot_path, "rb") as f:
                res = requests.post("http://localhost:8000/api/v1/recommendation/generate", files={"file": f}, timeout=10.0)
            if res.status_code == 200:
                result = res.json()
                vision = result.get("vision", {})
                rec = result.get("recommendation", {})
                print_success(f"Diagnosis: {vision.get('predicted_class', 'Unknown')} ({(vision.get('confidence', 0)*100):.1f}% confidence)")
                print(f"  {Colors.BOLD}Priority:{Colors.RESET} {rec.get('priority', 'Normal').upper()}")
                print(f"  {Colors.BOLD}Summary:{Colors.RESET}  {rec.get('summary', '')}")
            else:
                print_warning(f"AI Service response: {res.status_code} - {res.text}")
        except Exception as e:
            print_error(f"Failed to communicate with AI Service: {e}")

    def start_full_stack(self):
        """Orchestrates launching the entire platform stack in standalone mode with interactive controls."""
        print_header("Hydroponics Platform — Standalone Full Stack", "Broker, Gateway, Backend, AgroEye AI & Next.js React UI")
        
        # 1. Clean ports
        for key in ["broker", "backend", "ai", "frontend", "camera"]:
            if self.services[key].port:
                self.kill_process_on_port(self.services[key].port)

        active_processes: List[subprocess.Popen] = []

        def cleanup_stack(sig=None, frame=None):
            print(f"\n{Colors.BRIGHT_YELLOW}Shutting down entire platform stack and freeing ports...{Colors.RESET}")
            for p in active_processes:
                if p.poll() is None:
                    try:
                        p.terminate()
                    except Exception:
                        pass
            time.sleep(1.0)
            for p in active_processes:
                if p.poll() is None:
                    try:
                        p.kill()
                    except Exception:
                        pass
            print_success("All platform services terminated cleanly.")
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup_stack)
        signal.signal(signal.SIGTERM, cleanup_stack)

        try:
            # Step 1: Mosquitto MQTT Broker
            print_info("1/5 Launching Mosquitto MQTT Broker on port 1883...")
            p_broker = subprocess.Popen(self.services["broker"].cmd, cwd=self.services["broker"].cwd)
            active_processes.append(p_broker)
            time.sleep(1.0)

            # Step 2: Edge Gateway
            print_info("2/5 Launching Multi-Node Serial Edge Gateway (COM6 / COM7)...")
            p_gw = subprocess.Popen(self.services["gateway"].cmd, cwd=self.services["gateway"].cwd)
            active_processes.append(p_gw)
            time.sleep(1.0)

            # Step 3: Cloud Backend API
            print_info("3/5 Launching Cloud Backend & API on http://localhost:4000...")
            p_backend = subprocess.Popen(self.services["backend"].cmd, cwd=self.services["backend"].cwd)
            active_processes.append(p_backend)
            time.sleep(2.0)

            # Step 4: AgroEye AI Microservice & Dashboard
            print_info("4/5 Launching AgroEye AI Service & Dashboard on http://localhost:8000...")
            p_ai = subprocess.Popen(self.services["ai"].cmd, cwd=self.services["ai"].cwd)
            active_processes.append(p_ai)
            time.sleep(2.0)

            # Step 5: Next.js 14 React Dashboard
            print_info("5/5 Launching React 18 / Next.js 14 Dashboard on http://localhost:3000...")
            p_fe = subprocess.Popen(self.services["frontend"].cmd, cwd=self.services["frontend"].cwd)
            active_processes.append(p_fe)
            time.sleep(2.0)

            # Interactive Live Control Loop
            while True:
                print(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}========================================================================{Colors.RESET}")
                print(f"{Colors.BRIGHT_GREEN}{Colors.BOLD}  🚀 HYDROPONICS PLATFORM ACTIVE & RUNNING{Colors.RESET}")
                print(f"  🌿 {Colors.BOLD}React Dashboard (Port 3000):{Colors.RESET}   http://localhost:3000/")
                print(f"  🤖 {Colors.BOLD}AgroEye AI Service (Port 8000):{Colors.RESET} http://localhost:8000/")
                print(f"  ☁️  {Colors.BOLD}Backend API Docs (Port 4000):{Colors.RESET}   http://localhost:4000/api/v1/health")
                print(f"{Colors.BRIGHT_GREEN}{Colors.BOLD}========================================================================{Colors.RESET}")
                print(f"  {Colors.BOLD}LIVE OPERATOR CONTROLS:{Colors.RESET}")
                print(f"  [{Colors.BRIGHT_CYAN}1{Colors.RESET}] / [{Colors.BRIGHT_CYAN}p{Colors.RESET}]  Toggle Water Pump Relay (State: {Colors.BRIGHT_GREEN if self.pump_state else Colors.WHITE}{'ON' if self.pump_state else 'OFF'}{Colors.RESET})")
                print(f"  [{Colors.BRIGHT_CYAN}2{Colors.RESET}] / [{Colors.BRIGHT_CYAN}a{Colors.RESET}]  Toggle Autonomous Smart Irrigation (Mode: {Colors.BRIGHT_GREEN if self.auto_mode else Colors.WHITE}{'AUTO' if self.auto_mode else 'MANUAL'}{Colors.RESET})")
                print(f"  [{Colors.BRIGHT_CYAN}3{Colors.RESET}] / [{Colors.BRIGHT_CYAN}r{Colors.RESET}]  Reset Safety Interlock & Clear Faults")
                print(f"  [{Colors.BRIGHT_CYAN}4{Colors.RESET}] / [{Colors.BRIGHT_CYAN}c{Colors.RESET}]  Trigger AI Plant Pathology Scan (YOLO + Groq LLM)")
                print(f"  [{Colors.BRIGHT_CYAN}5{Colors.RESET}] / [{Colors.BRIGHT_CYAN}s{Colors.RESET}]  View Live Telemetry Snapshot & Sensor Metrics")
                print(f"  [{Colors.BRIGHT_CYAN}6{Colors.RESET}] / [{Colors.BRIGHT_CYAN}d{Colors.RESET}]  Open React Web Dashboard in Default Browser")
                print(f"  [{Colors.BRIGHT_CYAN}7{Colors.RESET}]        Open AgroEye AI Docs in Default Browser")
                print(f"  [{Colors.BRIGHT_CYAN}0{Colors.RESET}] / [{Colors.BRIGHT_CYAN}q{Colors.RESET}]  Gracefully Terminate All Background Services")
                print(f"{Colors.BRIGHT_GREEN}{Colors.BOLD}========================================================================{Colors.RESET}")
                
                try:
                    cmd = input(f"{Colors.BOLD}Enter option [1-7, 0/q]: {Colors.RESET}").strip().lower()
                except (EOFError, KeyboardInterrupt):
                    cleanup_stack()
                    break

                if cmd in ["1", "p"]:
                    self.pump_state = not self.pump_state
                    next_val = "ON" if self.pump_state else "OFF"
                    self._dispatch_command("SET_STATE", next_val)

                elif cmd in ["2", "a"]:
                    self.auto_mode = not self.auto_mode
                    next_val = "AUTO_ON" if self.auto_mode else "AUTO_OFF"
                    self._dispatch_command(next_val)

                elif cmd in ["3", "r"]:
                    self._dispatch_command("RESET_FAULT")

                elif cmd in ["4", "c"]:
                    self._trigger_ai_leaf_scan()

                elif cmd in ["5", "s"]:
                    self._show_telemetry_snapshot()

                elif cmd in ["6", "d"]:
                    print_info("Opening React Dashboard http://localhost:3000 in your browser...")
                    webbrowser.open("http://localhost:3000")

                elif cmd in ["7"]:
                    print_info("Opening AgroEye AI Docs http://localhost:8000/docs in your browser...")
                    webbrowser.open("http://localhost:8000/docs")

                elif cmd in ["0", "q", "exit"]:
                    cleanup_stack()
                    break
                else:
                    print_warning("Invalid input. Please enter 0-7, or p/a/r/c/s/d/q.")

        except KeyboardInterrupt:
            cleanup_stack()

def stack_menu():
    """Interactive Stack Orchestration Menu."""
    sm = StackManager()
    while True:
        print_header("Full-Stack Orchestration Menu")
        print_menu_item("1", "Start Full Platform Stack (With Live Controls)", "Broker + Gateway + Backend + AI + Dashboard")
        print_menu_item("2", "Start AgroEye AI & Dashboard", "Port 8000 (YOLO11, RAG, Groq & Web UI)")
        print_menu_item("3", "Start Node.js Backend API Server", "Port 4000 (Express, WebSocket, Supabase)")
        print_menu_item("4", "Start Multi-Node Edge Gateway Only", "USB Multi-Serial to MQTT Bridge")
        print_menu_item("5", "Start Next.js Web Dashboard", "Port 3000 (Modern UI & ECharts)")
        print_menu_item("6", "Start Local Mosquitto Broker", "Port 1883 (MQTT)")
        print_menu_item("7", "Start ESP32-CAM Video Gateway", "Port 8080 (Live Frame Proxy)")
        print_menu_item("8", "Kill All Running Services & Clean Ports", "Free ports 1883, 3000, 4000, 5555, 8000, 8080")
        print_menu_item("0", "Return to Main Menu")

        choice = prompt_choice()
        if choice == "1":
            sm.start_full_stack()
        elif choice == "2":
            sm.start_service("ai")
        elif choice == "3":
            sm.start_service("backend")
        elif choice == "4":
            sm.start_service("gateway")
        elif choice == "5":
            sm.start_service("frontend")
        elif choice == "6":
            sm.start_service("broker")
        elif choice == "7":
            sm.start_service("camera")
        elif choice == "8":
            sm.clean_all_ports()
            pause()
        elif choice == "0":
            break
