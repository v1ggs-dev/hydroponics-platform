#!/usr/bin/env python3
"""
Hydroponics Platform — Interactive Serial Console & Pump Controller
Allows interactive control of the ESP32 relay and live monitoring.
"""

import sys
import time
import threading
import serial
import serial.tools.list_ports

DEFAULT_PORT = "COM6"
DEFAULT_BAUD = 115200

def list_available_ports():
    ports = list(serial.tools.list_ports.comports())
    valid_ports = []
    print("\n[Available Serial Ports]:")
    for p in ports:
        if "CP210" in p.description or "CH340" in p.description or "USB" in p.description:
            valid_ports.append(p.device)
            print(f"  -> {p.device}: {p.description}")
        else:
            print(f"     {p.device}: {p.description}")
    return valid_ports

def reader_thread(ser, stop_event):
    while not stop_event.is_set():
        try:
            if ser.in_waiting:
                line = ser.readline().decode("utf-8", errors="replace").strip()
                if line:
                    if line.startswith("[TELEMETRY_JSON]"):
                        # Dim verbose raw JSON for cleaner display
                        print(f"\r\033[90m{line}\033[0m\nESP32 > ", end="", flush=True)
                    elif line.startswith("[SYSTEM]") or line.startswith("[PUMP]") or line.startswith("[SAFETY]") or line.startswith("[CMD"):
                        # Highlight status and command execution lines
                        print(f"\r\033[92m{line}\033[0m\nESP32 > ", end="", flush=True)
                    else:
                        print(f"\r{line}\nESP32 > ", end="", flush=True)
            else:
                time.sleep(0.02)
        except Exception as e:
            if not stop_event.is_set():
                print(f"\n[Reader Error]: {e}")
            break

def main():
    available = list_available_ports()

    if len(sys.argv) > 1:
        port = sys.argv[1]
    else:
        if DEFAULT_PORT in available:
            port = DEFAULT_PORT
        elif available:
            port = available[0]
        else:
            port = DEFAULT_PORT

    print(f"\n[Connecting] Opening Main ESP32 Controller on \033[96m{port}\033[0m at {DEFAULT_BAUD} baud...")
    print(f"*(Tip: Run 'python scripts/serial_console.py COM8' or 'COM6' to switch boards)*\n")

    try:
        ser = serial.Serial(port, DEFAULT_BAUD, timeout=0.1)
    except Exception as e:
        print(f"[Error] Failed to open {port}: {e}")
        return

    time.sleep(0.5)

    print("=" * 60)
    print("  🌿 HYDROPONICS ESP32 INTERACTIVE SERIAL CONTROLLER")
    print("=" * 60)
    print("  Commands:")
    print("    [1] or 'on'      -> Turn DC Pump ON")
    print("    [0] or 'off'     -> Turn DC Pump OFF")
    print("    [t] or 'toggle'  -> Toggle Pump State")
    print("    [a] or 'auto'    -> Enable Smart Auto-Irrigation")
    print("    [d]              -> Disable Auto-Irrigation")
    print("    [r] or 'reset'   -> Clear Safety Fault Lockout")
    print("    [q] or 'exit'    -> Exit Console")
    print("=" * 60 + "\n")

    stop_event = threading.Event()
    t = threading.Thread(target=reader_thread, args=(ser, stop_event), daemon=True)
    t.start()

    try:
        while True:
            try:
                user_input = input("ESP32 > ").strip()
            except (EOFError, KeyboardInterrupt):
                break

            if not user_input:
                continue

            lowered = user_input.lower()
            if lowered in ["q", "exit", "quit"]:
                break

            # Map convenience aliases
            cmd_to_send = user_input
            if lowered == "on":
                cmd_to_send = "1"
            elif lowered == "off":
                cmd_to_send = "0"
            elif lowered == "toggle":
                cmd_to_send = "t"
            elif lowered == "auto":
                cmd_to_send = "a"
            elif lowered == "reset":
                cmd_to_send = "r"

            # Send to ESP32
            ser.write((cmd_to_send + "\r\n").encode("utf-8"))
            ser.flush()
            time.sleep(0.1)

    finally:
        stop_event.set()
        ser.close()
        print("\n[Disconnected] Serial port closed. Goodbye!\n")

if __name__ == "__main__":
    main()
