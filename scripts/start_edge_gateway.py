#!/usr/bin/env python3
"""
Launcher for the Hydroponics Edge Gateway Service.
"""
import sys
import os

# Add edge/gateway to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "edge", "gateway")))

from main import main

if __name__ == "__main__":
    main()
