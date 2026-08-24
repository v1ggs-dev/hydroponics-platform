#!/usr/bin/env python3
"""
Hydroponics Platform — Unified CLI Master Manager Script
The all-in-one command-line interface for running full-stack services, flashing firmware,
monitoring serial streams, calibrating sensors, and managing Supabase database tools.
"""

import os
import sys
import argparse
import subprocess

# Add scripts directory to path for submodules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.banner import (
    Colors, clear_screen, print_header, print_section, print_menu_item,
    print_success, print_error, print_warning, print_info, prompt_choice, pause
)
from modules.stack_manager import StackManager, stack_menu
from modules.firmware_manager import FirmwareManager, firmware_menu
from modules.calibration_wizard import CalibrationWizard, calibration_menu
from modules.db_manager import DatabaseManager, db_menu
from modules.diagnostic_checker import DiagnosticChecker, diagnostic_menu
from modules.mqtt_sniffer import MQTTSniffer, sniffer_menu
from modules.simulator import TelemetrySimulator, simulator_menu

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def zip_notion_docs():
    """Compresses documentation files into notion_documentation.zip."""
    print_header("Re-packaging Notion Documentation ZIP")
    zip_path = os.path.join(ROOT_DIR, "notion_documentation.zip")
    notion_dir = os.path.join(ROOT_DIR, "notion")
    doc_dir = os.path.join(ROOT_DIR, "documentation")

    source_dir = notion_dir if os.path.exists(notion_dir) else doc_dir

    import shutil
    try:
        shutil.make_archive(
            base_name=os.path.join(ROOT_DIR, "notion_documentation"),
            format="zip",
            root_dir=source_dir
        )
        print_success(f"Created {zip_path} successfully!")
    except Exception as e:
        print_error(f"Failed to create zip: {e}")
    pause()

def main_interactive_menu():
    """Main Interactive TUI Menu Loop."""
    sm = StackManager()

    while True:
        clear_screen()
        print_header("Hydroponics Platform — Master Manager", "Dual-ESP32, Dual-Display & Water Chemistry System")

        print(f"  {Colors.BOLD}{Colors.BRIGHT_WHITE}SYSTEM ORCHESTRATION & RUNTIMES{Colors.RESET}")
        print_menu_item("1", "🚀 Full-Stack Service Orchestrator", "Start/Stop Broker, Gateway, Backend, Frontend")
        print_menu_item("2", "🎮 Hardware-Free Virtual Simulator", "Test & Rework UI with dynamic live telemetry")
        print_menu_item("3", "⚡ Firmware & Hardware Suite", "Compile & Flash Node 1 (ENV), Node 2 (CHEM), Vision (CAM)")
        print_menu_item("4", "🧪 Sensor Calibration Wizards", "Interactive 2-Point pH & TDS Calibration")
        print_menu_item("5", "🗄️ Database & Supabase Tools", "Prisma DB Push, Studio UI (Port 5555)")
        print_menu_item("6", "📥 Live MQTT Topic Sniffer", "Stream & inspect live hydroponics/# messages")
        print_menu_item("7", "🔍 Pre-Flight Diagnostic Checker", "Validate Python, Node.js, PlatformIO & Ports")
        print_menu_item("8", "📦 Re-package Notion Docs ZIP", "Build fresh notion_documentation.zip")
        print_menu_item("9", "🧹 Clean Up All Network Ports", "Kill orphaned processes on 1883, 3000, 4000, 5555")
        print_menu_item("0", "Exit Manager", "Quit application")

        choice = prompt_choice()

        if choice == "1":
            stack_menu()
        elif choice == "2":
            simulator_menu()
        elif choice == "3":
            firmware_menu()
        elif choice == "4":
            calibration_menu()
        elif choice == "5":
            db_menu()
        elif choice == "6":
            sniffer_menu()
        elif choice == "7":
            diagnostic_menu()
        elif choice == "8":
            zip_notion_docs()
        elif choice == "9":
            sm.clean_all_ports()
            pause()
        elif choice == "0":
            print(f"\n{Colors.BRIGHT_GREEN}Exiting Hydroponics Manager. Happy growing! 🌿{Colors.RESET}\n")
            sys.exit(0)

def parse_cli_args():
    """Handles direct CLI command execution."""
    parser = argparse.ArgumentParser(
        description="Hydroponics Platform — Unified CLI Master Manager",
        epilog="Run without arguments to enter the interactive menu."
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # 1. Stack commands
    stack_parser = subparsers.add_parser("stack", help="Full stack orchestration")
    stack_parser.add_argument("action", choices=["start", "stop", "clean"], help="Action to perform")

    # 2. Firmware compile
    compile_parser = subparsers.add_parser("compile", help="Compile embedded firmware")
    compile_parser.add_argument("target", choices=["env", "chem", "cam", "all"], help="Firmware target to compile")

    # 3. Firmware flash
    flash_parser = subparsers.add_parser("flash", help="Flash embedded firmware")
    flash_parser.add_argument("target", choices=["env", "chem", "cam"], help="Firmware target to flash")
    flash_parser.add_argument("--port", "-p", help="Serial COM port (e.g. COM6)")

    # 4. Serial monitor
    mon_parser = subparsers.add_parser("monitor", help="Interactive serial monitor")
    mon_parser.add_argument("--port", "-p", help="Serial COM port")

    # 5. Calibration
    cal_parser = subparsers.add_parser("calibrate", help="Sensor calibration wizard")
    cal_parser.add_argument("sensor", choices=["ph", "tds"], help="Sensor to calibrate")

    # 6. Database
    db_parser = subparsers.add_parser("db", help="Database management")
    db_parser.add_argument("action", choices=["push", "studio", "generate"], help="Database action")

    # 7. Diagnostic
    subparsers.add_parser("check", help="Run pre-flight diagnostics")

    # 8. Sniffer
    subparsers.add_parser("sniff", help="Live MQTT sniffer")

    # 9. Ports clean
    subparsers.add_parser("clean", help="Kill processes on platform network ports")

    # 10. Simulator
    sim_parser = subparsers.add_parser("simulate", help="Hardware-free telemetry simulator")
    sim_parser.add_argument("--profile", "-p", choices=["optimal", "heat", "acidic"], default="optimal", help="Simulation profile")

    # 11. AI Microservice & Dashboard
    ai_parser = subparsers.add_parser("ai", help="AgroEye AI Microservice & Dashboard")
    ai_parser.add_argument("action", choices=["start", "stop"], help="Action to perform (start, stop)")

    args = parser.parse_args()

    if not args.command:
        main_interactive_menu()
        return

    # Execute direct CLI subcommands
    sm = StackManager()

    if args.command == "stack":
        if args.action == "start":
            sm.start_full_stack()
        elif args.action in ["stop", "clean"]:
            sm.clean_all_ports()

    elif args.command == "ai":
        if args.action == "start":
            sm.start_service("ai")
        elif args.action == "stop":
            sm.kill_process_on_port(8000)

    elif args.command == "compile":
        if args.target == "all":
            FirmwareManager.compile_all()
        else:
            FirmwareManager.compile_target(args.target)

    elif args.command == "flash":
        FirmwareManager.flash_target(args.target, port=args.port)

    elif args.command == "monitor":
        FirmwareManager.interactive_serial_monitor(port=args.port)

    elif args.command == "calibrate":
        if args.sensor == "ph":
            CalibrationWizard.run_ph_calibration_wizard()
        elif args.sensor == "tds":
            CalibrationWizard.run_tds_calibration_wizard()

    elif args.command == "db":
        if args.action == "push":
            DatabaseManager.push_schema()
        elif args.action == "studio":
            DatabaseManager.launch_studio()
        elif args.action == "generate":
            DatabaseManager.generate_client()

    elif args.command == "check":
        DiagnosticChecker.run_preflight_check()

    elif args.command == "sniff":
        MQTTSniffer.run_sniffer()

    elif args.command == "clean":
        sm.clean_all_ports()

    elif args.command == "simulate":
        sim = TelemetrySimulator()
        if args.profile == "heat":
            sim.profile = "HEAT_STRESS"
        elif args.profile == "acidic":
            sim.profile = "ACIDIC_PH"
        else:
            sim.profile = "OPTIMAL"
        sim.start_simulation()

if __name__ == "__main__":
    parse_cli_args()
