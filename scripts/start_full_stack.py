#!/usr/bin/env python3
"""
Hydroponics Platform — Full-Stack Launcher
Starts all 4 tiers simultaneously:
  1. Local MQTT Message Broker (Port 1883 & 9001)
  2. Edge Gateway Service (Serial Bridge on COM6)
  3. Cloud Backend Service (Port 4000 & Supabase Ingestion)
  4. Next.js 14 Web Dashboard (Port 3000)
"""

import subprocess
import sys
import os
import time
import signal

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
backend_dir = os.path.join(root_dir, "backend")
frontend_dir = os.path.join(root_dir, "frontend")

processes = []

def cleanup(sig=None, frame=None):
    print("\n\n🛑 [Full-Stack] Shutting down all platform services...")
    for p, name in reversed(processes):
        try:
            print(f"  -> Stopping {name}...")
            p.terminate()
            p.wait(timeout=2)
        except Exception:
            try:
                p.kill()
            except Exception:
                pass
    print("✅ All services stopped safely. Goodbye!\n")
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

def main():
    print("\n" + "=" * 70)
    print("  🌿 HYDROPONICS IOT PLATFORM — FULL-STACK SYSTEM LAUNCHER")
    print("=" * 70)
    print("  Starting all 4 architectural tiers...")
    print("  - MQTT Message Broker:  0.0.0.0:1883 (TCP) & 9001 (WS)")
    print("  - Edge Gateway Service: Wired Serial Bridge (COM6)")
    print("  - Cloud Backend API:    http://localhost:4000 & Supabase DB")
    print("  - Web Dashboard UI:     http://localhost:3000 (Next.js 14)")
    print("=" * 70 + "\n")

    # 1. Start MQTT Broker
    p_broker = subprocess.Popen([sys.executable, "scripts/start_mqtt_broker.py"], cwd=root_dir)
    processes.append((p_broker, "MQTT Broker"))
    time.sleep(1.0)

    # 2. Start Backend API & Ingestion Service
    p_backend = subprocess.Popen(["npm", "run", "dev"], cwd=backend_dir, shell=True)
    processes.append((p_backend, "Backend Service"))
    time.sleep(2.0)

    # 3. Start Edge Gateway Service
    p_gateway = subprocess.Popen([sys.executable, "scripts/start_edge_gateway.py"], cwd=root_dir)
    processes.append((p_gateway, "Edge Gateway"))
    time.sleep(1.0)

    # 4. Start Next.js Frontend Dashboard
    p_frontend = subprocess.Popen(["npm", "run", "dev"], cwd=frontend_dir, shell=True)
    processes.append((p_frontend, "Next.js Dashboard"))

    print("\n" + "=" * 70)
    print("  ✨ FULL STACK IS LIVE!")
    print("  👉 Open Web Dashboard in your browser: http://localhost:3000")
    print("  👉 Press Ctrl+C at any time to stop all services.")
    print("=" * 70 + "\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup()

if __name__ == "__main__":
    main()
