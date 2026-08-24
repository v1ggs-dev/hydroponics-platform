"""
Hydroponics Platform — Firmware & Hardware Manager
Compiles, flashes, scans COM ports, and provides interactive serial consoles.
"""

import os
import sys
import time
import subprocess
import threading
from typing import List, Optional
import serial
import serial.tools.list_ports

from .banner import (
    Colors, print_header, print_section, print_menu_item,
    print_success, print_error, print_warning, print_info, prompt_choice, pause
)

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

TARGETS = {
    "env": {
        "name": "Node 1: Environment & Actuation (esp32-env)",
        "path": os.path.join(ROOT_DIR, "firmware", "esp32_env"),
        "description": "DHT11, Flow Sensor, Relay, Buzzer, Display #1"
    },
    "chem": {
        "name": "Node 2: Water Chemistry & Roots (esp32-chem)",
        "path": os.path.join(ROOT_DIR, "firmware", "esp32_chem"),
        "description": "pH Sensor, TDS Sensor, Moisture Sensor, Display #2"
    },
    "cam": {
        "name": "Vision Node: ESP32-CAM (esp32-cam)",
        "path": os.path.join(ROOT_DIR, "firmware", "esp32_cam"),
        "description": "OV2640 2MP Camera, Web Server & High-Res Capture"
    }
}

class FirmwareManager:
    @staticmethod
    def scan_ports() -> List[serial.tools.list_ports_common.ListPortInfo]:
        """Lists all detected COM ports with detailed hardware descriptors."""
        ports = list(serial.tools.list_ports.comports())
        print_section("Hardware Serial Port Scanner")
        if not ports:
            print_warning("No active USB serial / COM ports detected on the system.")
            return []

        print(f"  {Colors.BOLD}{'PORT':<10} {'DESCRIPTION':<35} {'HARDWARE ID':<25}{Colors.RESET}")
        print(f"  {'-'*10} {'-'*35} {'-'*25}")
        for p in ports:
            desc = p.description or "Unknown Device"
            hwid = p.hwid or ""
            is_esp = any(k in desc.lower() for k in ["cp210", "ch340", "ftdi", "uart", "esp32", "usb to uart", "usb serial"])
            color = Colors.BRIGHT_GREEN if is_esp else Colors.WHITE
            star = " * (ESP32)" if is_esp else ""
            print(f"  {color}{p.device:<10} {desc[:34]:<35} {hwid[:24]:<25}{star}{Colors.RESET}")
        print()
        return ports

    @staticmethod
    def compile_target(target_key: str) -> bool:
        """Compiles specified PlatformIO firmware project."""
        if target_key not in TARGETS:
            print_error(f"Unknown firmware target: {target_key}")
            return False

        target = TARGETS[target_key]
        print_header(f"Compiling {target['name']}", target['description'])
        print_info(f"Directory: {target['path']}")

        cmd = ["pio", "run", "-d", target['path']]
        try:
            res = subprocess.run(cmd)
            if res.returncode == 0:
                print_success(f"Compilation for {target_key} SUCCEEDED!")
                return True
            else:
                print_error(f"Compilation for {target_key} FAILED with exit code {res.returncode}.")
                return False
        except FileNotFoundError:
            print_error("PlatformIO Core ('pio') is not found in PATH. Please install or add to PATH.")
            return False

    @staticmethod
    def compile_all() -> bool:
        """Compiles all firmware targets sequentially."""
        print_header("Compiling All Firmware Targets")
        all_ok = True
        for k in ["env", "chem", "cam"]:
            print_section(f"Compiling Target: {k}")
            if not FirmwareManager.compile_target(k):
                all_ok = False
        if all_ok:
            print_success("ALL FIRMWARE TARGETS COMPILED SUCCESSFULLY!")
        else:
            print_error("One or more firmware targets failed compilation.")
        return all_ok

    @staticmethod
    def flash_target(target_key: str, port: Optional[str] = None) -> bool:
        """Flashes specified firmware target to ESP32."""
        if target_key not in TARGETS:
            print_error(f"Unknown firmware target: {target_key}")
            return False

        target = TARGETS[target_key]
        print_header(f"Flashing {target['name']}", target['description'])

        if not port:
            ports = FirmwareManager.scan_ports()
            if not ports:
                print_error("Cannot flash: No serial ports detected.")
                return False
            port = prompt_choice("Enter COM Port to flash", default=ports[0].device)

        print_info(f"Target: {target_key} | Port: {port}")
        cmd = ["pio", "run", "-d", target['path'], "-t", "upload", "--upload-port", port]
        try:
            res = subprocess.run(cmd)
            if res.returncode == 0:
                print_success(f"Successfully flashed {target_key} to {port}!")
                return True
            else:
                print_error(f"Flashing {target_key} to {port} failed.")
                return False
        except FileNotFoundError:
            print_error("PlatformIO Core ('pio') is not found in PATH.")
            return False

    @staticmethod
    def interactive_serial_monitor(port: Optional[str] = None, baud: int = 115200):
        """Interactive serial console with real-time command shortcuts."""
        if not port:
            ports = FirmwareManager.scan_ports()
            if not ports:
                print_error("No serial ports found.")
                return
            port = prompt_choice("Select COM Port for Monitor", default=ports[0].device)

        print_header(f"Live Interactive Serial Console ({port} @ {baud})")
        print_info("Shortcuts: [1] Pump ON | [0] Pump OFF | [t] Toggle | [r] Reset Fault | [a] Auto | [q] Quit\n")

        try:
            ser = serial.Serial(port, baud, timeout=0.1)
        except Exception as e:
            print_error(f"Could not open {port}: {e}")
            return

        running = True

        def read_loop():
            while running:
                try:
                    if ser.in_waiting > 0:
                        line = ser.readline().decode("utf-8", errors="replace").strip()
                        if line:
                            if "[TELEMETRY_JSON]" in line:
                                print(f"{Colors.BRIGHT_CYAN}{line}{Colors.RESET}")
                            elif "[CHEMISTRY]" in line:
                                print(f"{Colors.BRIGHT_MAGENTA}{line}{Colors.RESET}")
                            elif "[PUMP]" in line or "[SAFETY]" in line:
                                print(f"{Colors.BRIGHT_YELLOW}{line}{Colors.RESET}")
                            elif "[SYSTEM]" in line:
                                print(f"{Colors.BRIGHT_GREEN}{line}{Colors.RESET}")
                            else:
                                print(line)
                    time.sleep(0.01)
                except Exception:
                    break

        t = threading.Thread(target=read_loop, daemon=True)
        t.start()

        try:
            while True:
                user_input = input().strip()
                if user_input.lower() == "q":
                    break
                if user_input:
                    ser.write((user_input + "\r\n").encode("utf-8"))
                    ser.flush()
        except (KeyboardInterrupt, EOFError):
            pass
        finally:
            running = False
            ser.close()
            print_info(f"Closed serial connection to {port}.")

def firmware_menu():
    """Interactive Firmware & Hardware Menu."""
    while True:
        print_header("Firmware & Hardware Management Menu")
        print_menu_item("1", "Scan & Inspect USB Serial Ports", "Detect ESP32, ESP32-CAM, CH340, CP2102")
        print_menu_item("2", "Compile Node 1 Firmware (esp32_env)", "Climate, Flow, Relay, Buzzer, Display 1")
        print_menu_item("3", "Compile Node 2 Firmware (esp32_chem)", "pH Sensor, TDS, Moisture, Display 2")
        print_menu_item("4", "Compile Vision Node (esp32_cam)", "OV2640 2MP Camera Streaming")
        print_menu_item("5", "Compile ALL Firmware Targets", "Compile env, chem, and cam in sequence")
        print_menu_item("6", "Flash Node 1 (esp32_env)", "Upload to selected COM port")
        print_menu_item("7", "Flash Node 2 (esp32_chem)", "Upload to selected COM port")
        print_menu_item("8", "Flash Vision Node (esp32_cam)", "Upload to selected COM port")
        print_menu_item("9", "Interactive Serial Monitor & Control", "Live telemetry stream with command keyboard")
        print_menu_item("0", "Return to Main Menu")

        choice = prompt_choice()
        if choice == "1":
            FirmwareManager.scan_ports()
            pause()
        elif choice == "2":
            FirmwareManager.compile_target("env")
            pause()
        elif choice == "3":
            FirmwareManager.compile_target("chem")
            pause()
        elif choice == "4":
            FirmwareManager.compile_target("cam")
            pause()
        elif choice == "5":
            FirmwareManager.compile_all()
            pause()
        elif choice == "6":
            FirmwareManager.flash_target("env")
            pause()
        elif choice == "7":
            FirmwareManager.flash_target("chem")
            pause()
        elif choice == "8":
            FirmwareManager.flash_target("cam")
            pause()
        elif choice == "9":
            FirmwareManager.interactive_serial_monitor()
            pause()
        elif choice == "0":
            break
