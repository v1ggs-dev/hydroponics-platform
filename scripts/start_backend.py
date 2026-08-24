#!/usr/bin/env python3
"""
Launcher for the Hydroponics Cloud Backend & Supabase Ingestion Service.
"""
import subprocess
import sys
import os

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))

def main():
    print("🚀 Starting Hydroponics Backend Service (Node.js/TypeScript)...")
    try:
        # Run npm run dev in backend directory
        subprocess.run(["npm", "run", "dev"], cwd=backend_dir, shell=True, check=True)
    except KeyboardInterrupt:
        print("\n[Backend] Stopped.")
    except Exception as e:
        print(f"[Backend Error]: {e}")

if __name__ == "__main__":
    main()
