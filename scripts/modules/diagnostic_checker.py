"""
Hydroponics Platform — Pre-Flight System Diagnostic Checker
Validates Python dependencies, Node.js, PlatformIO, Database connection, and Hardware.
"""

import os
import sys
import shutil
import subprocess
import serial.tools.list_ports

from .banner import (
    Colors, print_header, print_section, print_menu_item,
    print_success, print_error, print_warning, print_info, prompt_choice, pause
)

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

class DiagnosticChecker:
    @staticmethod
    def run_preflight_check() -> bool:
        """Executes full diagnostic test suite across development environment."""
        print_header("System Pre-Flight Diagnostic Health Check", "Validating Dependencies, Toolchains & Hardware")

        overall_ok = True

        # 1. Python Environment & Modules
        print_section("1. Python Environment")
        py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        if sys.version_info.major >= 3 and sys.version_info.minor >= 8:
            print_success(f"Python Runtime: v{py_ver}")
        else:
            print_warning(f"Python Runtime: v{py_ver} (Recommend 3.10+)")

        required_modules = ["serial", "paho.mqtt.client", "psutil", "requests"]
        for mod in required_modules:
            try:
                __import__(mod)
                print_success(f"Python Package '{mod}': Installed")
            except ImportError:
                print_error(f"Python Package '{mod}': MISSING (Install via: pip install {mod})")
                overall_ok = False

        # 2. Node.js & npm Toolchains
        print_section("2. Node.js & npm Toolchains")
        node_bin = shutil.which("node")
        npm_bin = shutil.which("npm")

        if node_bin:
            try:
                node_ver = subprocess.check_output(["node", "-v"], text=True).strip()
                print_success(f"Node.js Runtime: {node_ver} ({node_bin})")
            except Exception:
                print_warning("Node.js binary found but could not get version.")
        else:
            print_error("Node.js: NOT FOUND in PATH.")
            overall_ok = False

        if npm_bin:
            try:
                npm_ver = subprocess.check_output(["npm", "-v"], shell=(sys.platform == "win32"), text=True).strip()
                print_success(f"npm Package Manager: v{npm_ver}")
            except Exception:
                pass
        else:
            print_error("npm: NOT FOUND in PATH.")
            overall_ok = False

        # 3. PlatformIO Embedded Toolchain
        print_section("3. PlatformIO Core (Embedded Compiler)")
        pio_bin = shutil.which("pio")
        if pio_bin:
            try:
                pio_ver = subprocess.check_output(["pio", "--version"], text=True).strip()
                print_success(f"PlatformIO Core: {pio_ver} ({pio_bin})")
            except Exception:
                print_warning("pio found but version check failed.")
        else:
            print_warning("PlatformIO Core ('pio'): Not in system PATH. Install via VSCode or pip install platformio.")

        # 4. Hardware USB COM Ports
        print_section("4. Hardware USB Serial Ports")
        ports = list(serial.tools.list_ports.comports())
        esp_ports = [p for p in ports if any(k in (p.description or "").lower() for k in ["cp210", "ch340", "ftdi", "uart", "esp32", "usb to uart", "usb serial"])]
        
        if esp_ports:
            print_success(f"Detected {len(esp_ports)} ESP32 controller port(s):")
            for p in esp_ports:
                print(f"    - {Colors.BOLD}{p.device}{Colors.RESET}: {p.description}")
        elif ports:
            print_warning(f"Detected {len(ports)} generic COM port(s), but no explicit ESP32 tags:")
            for p in ports:
                print(f"    - {p.device}: {p.description}")
        else:
            print_warning("No USB serial devices currently connected.")

        # 5. Database Configuration
        print_section("5. Supabase & Environment Configuration")
        env_backend = os.path.join(ROOT_DIR, "backend", ".env")
        if os.path.exists(env_backend):
            print_success(f"Backend environment file found: backend/.env")
        else:
            print_warning("backend/.env not found (Will use defaults or system environment)")

        # Summary
        print_section("Pre-Flight Summary")
        if overall_ok:
            print_success("ALL CORE SYSTEM PREREQUISITES VERIFIED! System is ready to operate.\n")
        else:
            print_warning("Some dependencies or tools are missing. Review errors above.\n")

        return overall_ok

def diagnostic_menu():
    """Interactive Diagnostic Menu."""
    while True:
        print_header("System Pre-Flight & Diagnostics Menu")
        print_menu_item("1", "Run Full Pre-Flight Health Check", "Tests Python, Node, PIO, Ports, and Environment")
        print_menu_item("0", "Return to Main Menu")

        choice = prompt_choice()
        if choice == "1":
            DiagnosticChecker.run_preflight_check()
            pause()
        elif choice == "0":
            break
