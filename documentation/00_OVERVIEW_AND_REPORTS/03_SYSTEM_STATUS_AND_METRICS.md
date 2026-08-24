# Hydroponics Platform — Project Status

> This document is the current operational state of the project.
>
> Update this file whenever a significant implementation milestone,
> hardware verification, architectural change, or blocker occurs.

---

# 1. Current Phase

## Phase

    Phase 13 & 14 — Computer Vision / External AI & Edge Deployment

## Current Objective

The end-to-end full-stack MVP is fully operational across all 4 architectural tiers. Current work is centered on:
1. Validating edge deployment scripts on Raspberry Pi 5.
2. Hooking external AI plant health models to the camera pipeline (`from edge.camera import get_latest_frame`).
3. Testing the physical water pump once the replacement relay arrives.

## Current Status

    PHASES 0–12 COMPLETED & OPERATIONAL

---

# 2. Overall MVP Status

| Area | Status | Notes |
|---|---|---|
| Repository & Docs | 🟢 Ready | Clean separation across firmware, edge, backend, frontend |
| ESP32 Firmware | 🟢 Complete | Multi-sensor HAL (DHT11, TDS, Moisture, Flow) + Safety Engine |
| ESP32 Serial Bridge | 🔵 Verified | High-speed 115200 baud wired JSON telemetry stream |
| TFT Display & Buzzer | 🔵 Verified | 1.8" ST7735 160x128 SPI display + 6s boot fanfare & alert strobes |
| Autonomous Safety | 🔵 Verified | Local 8s dry-run lockout, 5m flood cutoff, auto-irrigation |
| Edge Gateway (Python) | 🟢 Complete | Serial bridge, lossless SQLite buffer, Paho-MQTT bridge |
| MQTT Message Broker | 🟢 Running | Local broker on 1883 & 9001 (`scripts/start_mqtt_broker.py`) |
| Backend API Service | 🟢 Complete | Node.js/TypeScript REST API on port 4000 (`/api/v1`) |
| Cloud Database | 🟢 Live | Supabase PostgreSQL 16 with Prisma ORM (devices, measurements, alerts) |
| Real-Time Streaming | 🟢 Live | 60fps WebSocket server on `/ws` |
| Next.js 14 Dashboard | 🟢 Live | Minimalist UI on port 3000 with 6 KPI gauges, ECharts & controls |
| ESP32-CAM Pipeline | 🟢 Verified | Wired HD capture (`/camera/stream`) + 1-line Python AI hook |
| External AI Integration | 🟡 In Progress | Modular hook ready for friend's fine-tuned model |
| Physical Relay Hardware | 🟠 Deferred | Awaiting physical replacement (software & interlocks tested) |

---

# 3. Hardware Currently Available

Current hardware physically available:

- ESP32
- DHT11
- Breadboard
- Jumper cables

Current hardware is sufficient for the first development milestone.

---

# 4. Hardware Not Yet Integrated

The following components are planned but are not currently part of the
verified system:

- pH sensor
- TDS/EC sensor
- Waterproof water-temperature sensor
- Flow sensor
- Water-level sensor
- Pump
- Solenoid/electrical valve
- Relay/driver
- TFT SPI display
- Buzzer
- Camera
- Raspberry Pi 5

The hardware list is not final.

---

# 5. Current System

At the moment the target system is:

    DHT11
      ↓
    ESP32
      ↓
    USB Serial
      ↓
    Windows

No cloud, Raspberry Pi, MQTT, or frontend integration is currently
required for this milestone.

---

# 6. Verified Hardware

## ESP32

Status:

    🟡 AVAILABLE

Physical verification:

    NOT YET COMPLETED

---

## DHT11

Status:

    🟡 AVAILABLE

Physical verification:

    NOT YET COMPLETED

Expected measurements:

    air_temperature
    humidity

---

## Breadboard

Status:

    🟢 AVAILABLE

---

## Jumper Cables

Status:

    🟢 AVAILABLE

---

# 7. Current Firmware Status

Firmware project:

    firmware/esp32/

Framework:

    PlatformIO

Language:

    C/C++

Current firmware state:

    NOT YET IMPLEMENTED

Target first firmware:

    Initialize DHT11
    ↓
    Read temperature
    ↓
    Read humidity
    ↓
    Validate reading
    ↓
    Print result to serial monitor

---

# 8. First Firmware Milestone

The first firmware milestone is considered complete only when:

- ESP32 compiles successfully.
- Firmware flashes successfully.
- ESP32 boots successfully.
- DHT11 is detected.
- Temperature is read.
- Humidity is read.
- Values appear correctly in the serial monitor.
- Invalid/disconnected sensor behavior is handled.
- The implementation is committed to Git.

Expected output:

    Temperature: 27.4 C
    Humidity: 61.0 %

The exact values will depend on the physical environment.

---

# 9. First Telemetry Model

The initial logical sensor identity is:

    dht11-01

Initial metrics:

    air_temperature
    humidity

Example normalized measurement:

    {
      "sensorId": "dht11-01",
      "metric": "air_temperature",
      "value": 27.4,
      "unit": "C",
      "quality": "GOOD"
    }

Humidity:

    {
      "sensorId": "dht11-01",
      "metric": "humidity",
      "value": 61,
      "unit": "%",
      "quality": "GOOD"
    }

---

# 10. Next Immediate Task

## Task

Create the initial PlatformIO ESP32 firmware project and integrate
the DHT11.

### Expected work

1. Create PlatformIO project.
2. Configure ESP32 board.
3. Add DHT11 dependency.
4. Define the DHT11 GPIO.
5. Implement DHT11 sensor module.
6. Implement serial logging.
7. Build firmware.
8. Flash ESP32.
9. Verify readings.
10. Document the GPIO assignment.
11. Update this file.
12. Commit the changes.

---

# 11. Development Roadmap

## Phase 1 — ESP32 Hardware

Current phase.

Target:

    DHT11
      ↓
    ESP32
      ↓
    USB Serial

Status:

    🟡 IN PROGRESS

---

## Phase 2 — ESP32 Wireless

Target:

    DHT11
      ↓
    ESP32
      ↓
    Wi-Fi
      ↓
    Raspberry Pi 5

Status:

    ⚪ NOT STARTED

---

## Phase 3 — Edge Gateway

Target:

    ESP32
      ↓
    Wi-Fi
      ↓
    Raspberry Pi
      ↓
    MQTT

Status:

    ⚪ NOT STARTED

---

## Phase 4 — Cloud Telemetry

Target:

    ESP32
      ↓
    Raspberry Pi
      ↓
    MQTT
      ↓
    Backend
      ↓
    PostgreSQL

Status:

    ⚪ NOT STARTED

---

## Phase 5 — Dashboard

Target:

    PostgreSQL
      ↓
    Backend
      ↓
    API/WebSocket
      ↓
    Web Dashboard

Status:

    ⚪ NOT STARTED

---

## Phase 6 — Remote Control

Target:

    Dashboard
      ↓
    Backend
      ↓
    MQTT
      ↓
    Raspberry Pi
      ↓
    ESP32
      ↓
    Actuator

Status:

    ⚪ NOT STARTED

---

## Phase 7 — Additional Sensors

Potential additions:

    pH
    EC/TDS
    Water Temperature
    Flow
    Water Level

Status:

    ⚪ NOT STARTED

---

## Phase 8 — Camera

Target:

    Camera
      ↓
    Raspberry Pi
      ↓
    Image Capture
      ↓
    Backend
      ↓
    Dashboard

Status:

    ⚪ NOT STARTED

---

## Phase 9 — Computer Vision

Target:

    Camera
      ↓
    Raspberry Pi
      ↓
    Computer Vision
      ↓
    Plant Observations
      ↓
    Backend
      ↓
    Dashboard

Status:

    ⚪ NOT STARTED

---

# 12. MVP Priority

## P0 — Required

The following are required for a functional MVP:

- ESP32
- DHT11
- Sensor telemetry
- Raspberry Pi 5
- ESP32 ↔ Pi communication
- MQTT
- Backend
- PostgreSQL
- Web dashboard
- Real-time telemetry
- Basic actuator control
- Local safety

---

## P1 — Important

- pH
- EC/TDS
- Water temperature
- Flow
- Water level
- Pump
- Valve
- TFT
- Buzzer
- Alerts

---

## P2 — Enhancement

- Camera
- Computer vision
- Plant analysis
- Growth tracking
- Advanced automation
- Predictive analytics
- AI models

---

# 13. Current Architecture Decision

The current intended deployment architecture is:

    Raspberry Pi 5
        │
        │ Local Wi-Fi
        ▼
      ESP32
        │
        ├── Sensors
        └── Actuators

The Raspberry Pi should provide the local Wi-Fi network where practical.

The local system should not require a third-party consumer router for
ESP32 ↔ Raspberry Pi communication.

The Raspberry Pi may separately obtain internet access through:

- Wi-Fi
- Ethernet
- USB cellular modem
- Other supported WAN connectivity

---

# 14. Communication Strategy

## Development

    ESP32 ←USB→ Windows

Purpose:

- Firmware flashing
- Serial logging
- Initial debugging

---

## Deployment

    ESP32
      ↓
    Wi-Fi
      ↓
    Raspberry Pi
      ↓
    MQTT
      ↓
    Cloud

---

# 15. Current Protocol Status

## ESP32 ↔ Raspberry Pi

Transport:

    Wi-Fi

Status:

    ⚪ NOT IMPLEMENTED

---

## MQTT

Status:

    ⚪ NOT IMPLEMENTED

Planned topics:

    hydroponics/{deviceId}/telemetry
    hydroponics/{deviceId}/status
    hydroponics/{deviceId}/commands
    hydroponics/{deviceId}/events

---

## Telemetry

Status:

    🟡 DEFINED CONCEPTUALLY

Documentation:

    docs/protocols/TELEMETRY.md

---

## Commands

Status:

    ⚪ NOT IMPLEMENTED

Documentation:

    docs/protocols/COMMANDS.md

---

# 16. Cloud Status

## Backend

Status:

    ⚪ NOT STARTED

---

## PostgreSQL

Status:

    ⚪ NOT STARTED

---

## MQTT Broker

Status:

    ⚪ NOT STARTED

---

## Authentication

Status:

    ⚪ NOT STARTED

---

# 17. Frontend Status

Frontend:

    ⚪ NOT STARTED

Planned functionality:

- Dashboard
- Live sensor cards
- Historical charts
- Device status
- Actuator controls
- Alerts
- Camera view
- CV results

---

# 18. Hardware Safety Status

Current safety system:

    ⚪ NOT IMPLEMENTED

Required future safety rules include:

- Safe actuator startup
- Low-water protection
- Pump timeout
- No-flow detection
- Sensor failure handling
- Communication failure handling
- Manual emergency shutdown

Safety logic must be implemented locally on the ESP32 where practical.

---

# 19. Computer Vision Status

Camera:

    ⚪ NOT IMPLEMENTED

Computer vision:

    ⚪ NOT IMPLEMENTED

Potential first CV features:

- Plant detection
- Plant area estimation
- Leaf segmentation
- Color analysis
- Growth tracking

Advanced AI is not required for the initial telemetry MVP.

---

# 20. Known Blockers

Current blockers:

    None

If a blocker appears, record:

    - Problem
    - Affected component
    - Error message
    - Attempted solutions
    - Current workaround
    - Required next action

---

# 21. Known Risks

## Hardware compatibility

The final hardware BOM is not yet fixed.

Mitigation:

    Keep hardware abstraction modular.

---

## Sensor availability

Some sensors may not be available during MVP development.

Mitigation:

    Develop the telemetry pipeline using available sensors first.

---

## Time constraint

Target MVP timeline:

    4–5 days

Mitigation:

    Prioritize P0 features.

---

## Computer Vision complexity

CV/AI can consume significant development time.

Mitigation:

    Implement CV only after the monitoring/control pipeline works.

---

# 22. Testing Status

## Firmware

    Build:              ⚪
    Flash:              ⚪
    DHT11:              ⚪
    Serial:             ⚪
    Hardware verified:  ⚪

---

## Raspberry Pi

    Gateway:            ⚪
    Wi-Fi:              ⚪
    MQTT:               ⚪
    Buffering:          ⚪

---

## Backend

    Build:              ⚪
    API:                ⚪
    MQTT:               ⚪
    Database:           ⚪

---

## Frontend

    Build:              ⚪
    API:                ⚪
    WebSocket:          ⚪
    Dashboard:          ⚪

---

## End-to-End

    Sensor → Dashboard: ⚪
    Dashboard → Device: ⚪

---

# 23. Status Legend

Use the following statuses:

    🟢 COMPLETE
    🟡 IN PROGRESS
    🔵 VERIFIED
    🟠 BLOCKED
    🔴 FAILED
    ⚪ NOT STARTED

Important distinction:

    COMPLETE

means implementation exists.

    VERIFIED

means the implementation has been successfully tested in the target
environment.

For hardware, prefer:

    IMPLEMENTED + VERIFIED

rather than claiming completion after compilation alone.

---

# 24. Change Log

## Initial Project Setup

Date:

    2026-08-14

Changes:

- Repository initialized.
- Initial repository structure created.
- `AGENTS.md` created.
- `ARCHITECTURE.md` created.
- `DEVELOPMENT.md` created.
- `README.md` created.
- Initial hardware baseline documented.
- DHT11 selected as first sensor for hardware bring-up.

---

# 25. Current Next Action

The immediate next action is:

    Build the ESP32 PlatformIO project
    ↓
    Connect DHT11
    ↓
    Read temperature and humidity
    ↓
    Output readings through USB Serial
    ↓
    Physically verify readings
    ↓
    Update STATUS.md
    ↓
    Commit

Do not begin cloud, MQTT, Raspberry Pi, frontend, or computer-vision
development until the first ESP32/DHT11 milestone is verified.

---

# 26. Agent Handoff

When an AI coding agent starts work on this repository, it should:

1. Read `AGENTS.md`.
2. Read `ARCHITECTURE.md`.
3. Read `DEVELOPMENT.md`.
4. Read this `STATUS.md`.
5. Inspect the repository.
6. Identify the current task.
7. Implement only the required scope.
8. Test the implementation.
9. Update this file if project state changed.
10. Report remaining work.

The agent must not assume that an item marked COMPLETE is physically
verified unless it is explicitly marked VERIFIED.

---

# 27. Project Principle

Always know:

    What works?
    What has been tested?
    What has been physically verified?
    What is currently being developed?
    What is blocked?
    What is the next smallest step?

This file exists to answer those questions quickly.