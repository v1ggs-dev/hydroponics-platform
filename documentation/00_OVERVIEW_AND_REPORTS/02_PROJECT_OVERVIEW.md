# Hydroponics Platform

A modular IoT-based hydroponics monitoring, control, automation, and
computer-vision platform.

The system combines an ESP32-based hardware controller, Raspberry Pi 5
edge computing, a remotely hosted cloud platform, and a professional
web dashboard.

---

## 1. Project Overview

The Hydroponics Platform is designed to monitor and control a
hydroponic growing environment in real time.

The system is designed to support:

- Environmental monitoring
- Water/nutrient monitoring
- Pump control
- Valve control
- Flow monitoring
- Water-level monitoring
- Real-time alerts
- Historical measurements
- Camera monitoring
- Computer-vision-based plant analysis
- Remote control
- Local automation
- Future AI-based optimization

The initial hardware list is a baseline and is expected to evolve.

The software architecture therefore intentionally avoids tightly
coupling the platform to specific sensors or actuators.

---

# 2. High-Level Architecture

The system consists of four primary layers:

    ┌────────────────────────────────────────────┐
    │                 WEB CLIENT                 │
    │                                            │
    │          Next.js Web Dashboard             │
    └──────────────────────┬─────────────────────┘
                           │
                      HTTPS / WS
                           │
                           ▼
    ┌────────────────────────────────────────────┐
    │                CLOUD PLATFORM              │
    │                                            │
    │ Backend API                                │
    │ PostgreSQL                                 │
    │ MQTT                                       │
    │ Authentication                             │
    │ Telemetry                                  │
    │ Commands                                   │
    │ Alerts                                     │
    └──────────────────────┬─────────────────────┘
                           │
                        Internet
                           │
                           ▼
    ┌────────────────────────────────────────────┐
    │               RASPBERRY PI 5               │
    │                                            │
    │ Edge Gateway                               │
    │ Local Wi-Fi Network                        │
    │ MQTT                                       │
    │ Camera                                     │
    │ Computer Vision                            │
    │ Local Automation                           │
    │ Local Buffering                             │
    └──────────────────────┬─────────────────────┘
                           │
                         Wi-Fi
                           │
                           ▼
    ┌────────────────────────────────────────────┐
    │                    ESP32                   │
    │                                            │
    │ Sensor Acquisition                         │
    │ Actuator Control                           │
    │ Local Safety                               │
    │ TFT Display                                │
    │ Buzzer                                     │
    └──────────────────────┬─────────────────────┘
                           │
                ┌──────────┴──────────┐
                │                     │
                ▼                     ▼
             SENSORS              ACTUATORS
                │                     │
          ┌─────┼─────┐          ┌────┼─────┐
          │     │     │          │    │     │
          pH    EC    Temp       Pump Valve Relay

---

## 3. Master Documentation Index

- 🔌 **[Complete Hardware Wiring Guide](docs/hardware/COMPLETE_WIRING_GUIDE.md)**: Exhaustive pin-by-pin schematic and breadboard connections.
- 📌 **[ESP32 Authoritative Pinout](docs/hardware/PINOUT.md)**: Hardware pin assignments and bus reservations.
- 📋 **[Master Project Checklist](CHECKLIST.md)**: Phase-by-phase implementation progress.
- 📊 **[System Status & Verification](STATUS.md)**: Live verification status of all components.
- 📡 **[Telemetry Protocol](docs/protocols/TELEMETRY.md)**: Canonical JSON telemetry schema.
- 🔐 **[Security Architecture](docs/architecture/SECURITY.md)**: Authentication, tokens, and authorization.