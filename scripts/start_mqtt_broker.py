#!/usr/bin/env python3
"""
Hydroponics Platform — Native Embedded MQTT Broker (Port 1883 & 9001)
Runs a high-performance local MQTT broker without requiring Docker.
"""

import sys
import io

# Ensure UTF-8 output encoding on Windows terminals
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import asyncio
import logging
from amqtt.broker import Broker

config = {
    'listeners': {
        'default': {
            'type': 'tcp',
            'bind': '0.0.0.0:1883',
        },
        'ws': {
            'type': 'ws',
            'bind': '0.0.0.0:9001',
        },
    },
    'sys_interval': 10,
    'auth': {
        'allow-anonymous': True,
        'plugins': ['auth_anonymous'],
    },
}

async def start_broker():
    broker = Broker(config)
    await broker.start()
    print("\n" + "=" * 65)
    print("  [OK] HYDROPONICS MQTT BROKER RUNNING (Port 1883 & WebSocket 9001)")
    print("=" * 65)
    print("  Local Broker IP: 0.0.0.0 (All interfaces)")
    print("  TCP MQTT Port:   1883 (ESP32 / Backend)")
    print("  WebSocket Port:  9001 (Web Dashboard)")
    print("  Status:          READY FOR INCOMING TELEMETRY")
    print("=" * 65 + "\n")
    sys.stdout.flush()
    
    # Keep broker running
    while True:
        await asyncio.sleep(1)

def main():
    # Set logging
    formatter = "[%(asctime)s] %(name)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.WARNING, format=formatter)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(start_broker())
    except KeyboardInterrupt:
        print("\n[MQTT Broker] Shutting down...")
    finally:
        loop.close()

if __name__ == '__main__':
    main()
