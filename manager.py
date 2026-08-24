#!/usr/bin/env python3
"""
Hydroponics Platform — Root CLI Master Manager Entrypoint
Delegates execution to scripts/manager.py
"""

import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))

from manager import parse_cli_args

if __name__ == "__main__":
    parse_cli_args()
