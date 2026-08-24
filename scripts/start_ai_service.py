"""
Hydroponics Platform — AgroEye AI Service & Dashboard Launcher
Runs the FastAPI server on port 8000 (YOLO11n-cls + FAISS RAG + Groq LLM + Dashboard)
"""

import os
import sys
import subprocess

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def main():
    print("\n" + "=" * 65)
    print("  🌿 LAUNCHING AGROEYE AI MICROSERVICE & DASHBOARD (PORT 8000)")
    print("=" * 65)
    print("  Dashboard UI:     http://localhost:8000/")
    print("  API Docs:         http://localhost:8000/docs")
    print("  YOLO Vision:      POST /api/v1/vision/classify")
    print("  Multimodal RAG:   POST /api/v1/recommendation/generate")
    print("=" * 65 + "\n")

    cmd = [
        sys.executable, "-m", "uvicorn",
        "ai.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ]

    try:
        subprocess.run(cmd, cwd=ROOT_DIR)
    except KeyboardInterrupt:
        print("\nStopping AgroEye AI Service...")

if __name__ == "__main__":
    main()
