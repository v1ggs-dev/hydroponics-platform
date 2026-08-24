#!/usr/bin/env python3
"""
Launcher for the Hydroponics Next.js 14 Web Application Dashboard.
"""
import subprocess
import sys
import os

frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

def main():
    print("🚀 Starting Hydroponics Web Dashboard (Next.js 14)...")
    try:
        subprocess.run(["npm", "run", "dev"], cwd=frontend_dir, shell=True, check=True)
    except KeyboardInterrupt:
        print("\n[Frontend] Stopped.")
    except Exception as e:
        print(f"[Frontend Error]: {e}")

if __name__ == "__main__":
    main()
