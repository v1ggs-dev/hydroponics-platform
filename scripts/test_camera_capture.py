#!/usr/bin/env python3
"""
Test utility for the Hydroponics Wired ESP32-CAM Ingestion Pipeline.
"""

import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from edge.camera import capture_snapshot, get_latest_frame, get_camera_status

def main():
    print("\n" + "=" * 65)
    print("  [CAMERA] HYDROPONICS CAMERA INGESTION & AI INTERFACE TEST")
    print("=" * 65)

    port = sys.argv[1] if len(sys.argv) > 1 else None
    if port:
        print(f"Connecting to ESP32-CAM on port: {port}...")
    else:
        print("No serial port specified. Testing local archive and AI interface...")

    # Trigger capture
    img_path = capture_snapshot(port=port)
    print(f"[OK] Image Snapshot Path: {img_path}")

    # Test AI 1-line interface
    frame = get_latest_frame(as_numpy=True)
    if frame is not None:
        shape_str = str(frame.shape) if hasattr(frame, "shape") else "PIL Image"
        print(f"[AI] Interface `get_latest_frame()`: SUCCESS -> Shape: {shape_str}")
    else:
        print("[INFO] AI Interface returned empty placeholder.")

    # Status summary
    status = get_camera_status()
    print("\nCamera Status Summary:")
    for k, v in status.items():
        print(f"  - {k}: {v}")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    main()
