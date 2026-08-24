# Hydroponics Platform — Phase-by-Phase Implementation Checklist

> **Authoritative Tracking Document**  
> Use this checklist to track granular progress across all tiers (Firmware, Edge, Backend, Database, Frontend, Hardware, Security, and Computer Vision).  
> Legend: `[ ]` Not Started &bull; `[/]` In Progress &bull; `[x]` Completed &bull; `[!]` Blocked

---

## 📊 Phase Progress Overview

| Phase | Description | Tier | Status | Target Timeline |
|---|---|---|---|---|
| **Phase 0** | Workspace, Repo Prep & Local Infra | Infra / Docs | `[x]` | Day 1 |
| **Phase 1** | ESP32 + DHT11 Hardware Bring-Up | Firmware (P0) | `[x]` | Day 1 |
| **Phase 2** | MQTT Message Broker & Network Transport | Messaging (P1) | `[x]` | Day 2 |
| **Phase 3** | Raspberry Pi 5 Edge Gateway & Local Buffer | Edge (P2) | `[x]` | Day 2 |
| **Phase 4** | MQTT Telemetry & Lifecycle Management | Messaging (P3) | `[x]` | Day 2 |
| **Phase 5** | Cloud Backend Application Architecture | Backend (P4) | `[x]` | Day 3 |
| **Phase 6** | PostgreSQL Persistence & Prisma Migrations (Supabase) | Database (P4) | `[x]` | Day 3 |
| **Phase 7** | Web Dashboard UI (Next.js 14 + Tailwind) | Frontend (P5) | `[x]` | Day 4 |
| **Phase 8** | Real-Time WebSocket Telemetry & Sync | Full-Stack (P5) | `[x]` | Day 4 |
| **Phase 9** | Local UI: TFT SPI Display & Buzzer Audio | Hardware/Firmware (P6-P7) | `[x]` | Day 5 |
| **Phase 10** | Multi-Sensor Expansion (pH, EC, Flow, Level) | Hardware/Firmware (P8) | `[x]` | Post-MVP / Day 5 |
| **Phase 11** | Actuator Control & Local Safety Interlocks | Full-Stack (P9) | `[x]` | Day 5 |
| **Phase 12** | Camera Capture Pipeline (ESP32-CAM Wired) | Edge/Camera (P10) | `[x]` | Post-MVP |
| **Phase 13** | Computer Vision & External AI Interface | Edge/CV (P11) | `[/]` | Post-MVP |
| **Phase 14** | Predictive AI & Automation Engine | Cloud/AI (P12) | `[ ]` | Post-MVP |
| **Phase 15** | Security Hardening, Observability & Runbook | Production | `[ ]` | Final Polish |

---

## Phase 0: Workspace, Repository Preparation & Local Infrastructure
- [x] Clean up documentation inconsistencies:
  - [x] Strip raw template header from [`docs/protocols/API.md`](docs/protocols/API.md).
  - [x] Extract security architecture from [`docs/architecture/DECISIONS.md`](docs/architecture/DECISIONS.md) into [`docs/architecture/SECURITY.md`](docs/architecture/SECURITY.md).
  - [x] Reformat [`docs/architecture/DECISIONS.md`](docs/architecture/DECISIONS.md) as an Architecture Decision Record (ADR) repository.
- [x] Create root environment configuration:
  - [x] Create `.env.example` documenting all MQTT, PostgreSQL, WebSocket, and API variables.
- [x] Setup Docker infrastructure:
  - [x] Create `infrastructure/docker-compose.yml` with:
    - [x] Eclipse Mosquitto MQTT broker (`1883`, `9001`).
    - [x] PostgreSQL 16 database with persistent volume (`5432`).
  - [x] Create `infrastructure/mosquitto/mosquitto.conf` with anonymous dev access enabled.
  - [x] Start Docker containers and verify ports are listening.

---

## Phase 1: ESP32 + DHT11 Hardware Bring-Up (Immediate P0)
- [x] Setup PlatformIO project:
  - [x] Create `firmware/esp32/platformio.ini` targeting `board = esp32dev`, `framework = arduino`.
  - [x] Configure baud rate to `115200` and add dependencies (`DHT sensor library for ESPx` / `Adafruit DHT`).
- [x] Firmware Hardware Abstraction:
  - [x] Create `firmware/esp32/src/config/pins.h` (`#define PIN_DHT11_DATA 4`, `PIN_TDS_ADC 34`).
  - [x] Create `firmware/esp32/src/config/config.h` (polling interval, device ID `esp32-01`).
  - [x] Implement `firmware/esp32/src/sensors/sensor_interface.h` (base class for normalized measurements).
  - [x] Implement `firmware/esp32/src/sensors/dht11_sensor.h/cpp`:
    - [x] Non-blocking reading logic.
    - [x] Validation check (prevent `NaN` / out-of-range publishing).
    - [x] Metric normalization (`air_temperature`, `humidity`).
- [x] Serial Telemetry Output:
  - [x] Implement `firmware/esp32/src/telemetry/telemetry_formatter.h/cpp` generating canonical JSON.
  - [x] Implement `firmware/esp32/src/main.cpp` loop.
- [x] Verification & Testing:
  - [x] Build firmware cleanly with PlatformIO (`pio run`).
  - [x] Connect ESP32 via USB and identify COM port (`COM6`).
  - [x] Flash firmware (`pio run --target upload`).
  - [x] Open Serial Monitor (`pio device monitor`) and physically verify valid temperature & humidity readings.
  - [x] Update [`STATUS.md`](STATUS.md) to record verified DHT11 & TDS sensor readings.

---

## Phase 2: ESP32 Wi-Fi & Network Resilience
- [ ] Wi-Fi Module Implementation:
  - [ ] Create `firmware/esp32/src/network/wifi_manager.h/cpp`.
  - [ ] Implement non-blocking state machine for connection, disconnection, and auto-reconnect.
  - [ ] Implement exponential backoff to avoid thrashing during access point downtime.
  - [ ] Add LED status indicator codes (slow blink = connecting, solid = connected, fast blink = error).
- [ ] Resilience Testing:
  - [ ] Test Wi-Fi disconnect and automatic reconnection without blocking sensor sampling loops.

---

## Phase 3: Raspberry Pi 5 Edge Gateway & Local Buffering
- [ ] Edge Gateway Setup:
  - [ ] Create `edge/gateway/requirements.txt` (`paho-mqtt`, `pydantic`, `aiohttp`, `sqlite3`).
  - [ ] Create `edge/gateway/config.py` for local broker and cloud broker settings.
- [ ] Telemetry Forwarder & Offline Buffer:
  - [ ] Implement `edge/gateway/buffer_store.py` (SQLite FIFO queue for offline storage).
  - [ ] Implement `edge/gateway/mqtt_bridge.py` to forward packets from local ESP32 network to Cloud.
  - [ ] Implement `edge/gateway/main.py` entrypoint.
- [ ] Testing:
  - [ ] Simulate network disconnect: verify local gateway buffers messages in SQLite and flushes upon reconnection.

---

## Phase 4: MQTT Messaging & Lifecycle Management
- [ ] ESP32 MQTT Client:
  - [ ] Create `firmware/esp32/src/network/mqtt_client.h/cpp` using `PubSubClient`.
  - [ ] Configure Last Will & Testament (LWT) on `hydroponics/esp32-01/status` (`{"status":"OFFLINE"}`).
  - [ ] Publish online presence on connect (`{"status":"ONLINE", "ip":"...", "firmware":"0.1.0"}`).
- [ ] Telemetry Publishing:
  - [ ] Stream periodic telemetry to `hydroponics/esp32-01/telemetry` at configured intervals (e.g. 5s/10s).
- [ ] Command Subscription:
  - [ ] Subscribe to `hydroponics/esp32-01/commands` and parse incoming control packets.
- [ ] Testing:
  - [ ] Use `mosquitto_sub` or MQTT Explorer to verify JSON payloads on all project topics.

---

## Phase 5: Cloud Backend Application Architecture
- [ ] Project Scaffolding:
  - [ ] Initialize NestJS / TypeScript application in `backend/`.
  - [ ] Configure `backend/tsconfig.json`, `backend/package.json`, and ESLint.
- [ ] Domain Modules Structure:
  - [ ] `AuthModule`: JWT auth, password hashing, user guards.
  - [ ] `DevicesModule`: Device registry, status monitoring, heartbeat tracking.
  - [ ] `TelemetryModule`: Ingestion pipeline, latest measurement cache, historical queries.
  - [ ] `CommandsModule`: Actuator command dispatch, timeout tracking, state management.
  - [ ] `AlertsModule`: System event thresholds, alert generation, notification dispatch.
  - [ ] `MqttModule`: Core MQTT client subscriber/publisher service.
  - [ ] `EventsModule`: WebSocket gateway for real-time dashboard broadcasting.
- [ ] Validation & Error Handling:
  - [ ] Implement global HTTP exception filters and DTO validation with `class-validator`.

---

## Phase 6: PostgreSQL Persistence & Prisma Migrations
- [ ] Prisma Database Modeling:
  - [ ] Configure `backend/prisma/schema.prisma`:
    - [ ] `User` (id, email, passwordHash, role, createdAt)
    - [ ] `Device` (id, name, status, firmwareVersion, lastSeenAt)
    - [ ] `Sensor` (id, deviceId, type, status, metadata)
    - [ ] `Actuator` (id, deviceId, type, state, lastChangedAt)
    - [ ] `Measurement` (id, deviceId, sensorId, metric, value, unit, quality, timestamp)
    - [ ] `Command` (id, deviceId, actuatorId, action, parameters, status, requestedAt, executedAt)
    - [ ] `Alert` (id, deviceId, severity, message, timestamp, resolved)
  - [ ] Add composite indexes on `(deviceId, metric, timestamp DESC)` for fast historical queries.
- [ ] Migrations & Seeding:
  - [ ] Generate and run Prisma migrations (`npx prisma migrate dev --name init`).
  - [ ] Create seed script registering default `esp32-01`, sensors (`dht11-01`), and actuators (`pump-01`, `valve-01`).

---

## Phase 7: Web Dashboard UI (Next.js + Tailwind CSS)
- [ ] Frontend Scaffolding:
  - [ ] Initialize Next.js 14 App Router project in `frontend/`.
  - [ ] Configure Tailwind CSS with scientific/agricultural design tokens (slate, emerald, cyan).
  - [ ] Install Lucide React icons, clsx, tailwind-merge, and shadcn/ui primitives.
- [ ] Dashboard Layout & Components:
  - [ ] Top navbar with system title, device connectivity badge (`ONLINE`/`OFFLINE`), and clock.
  - [ ] Real-time Metric Cards:
    - [ ] Air Temperature Card (`°C` with min/max indicator).
    - [ ] Humidity Card (`%` with comfort range indicator).
    - [ ] pH Card (placeholder / ready for sensor).
    - [ ] TDS / EC Card (placeholder / ready for sensor).
  - [ ] Actuator Control Panel:
    - [ ] Pump toggle switch with state confirmation feedback.
    - [ ] Valve toggle switch.
    - [ ] Emergency Stop button.
  - [ ] Historical Charts:
    - [ ] Interactive ECharts component showing temperature and humidity trends over 1h, 24h, 7d.
  - [ ] Active Alerts drawer/list with severity color coding.

---

## Phase 8: Real-Time WebSocket Telemetry & Synchronization
- [ ] WebSocket Server Gateway:
  - [ ] Implement NestJS `EventsGateway` (`/ws`) broadcasting incoming MQTT telemetry to connected browser clients.
- [ ] Frontend Real-time Hook:
  - [ ] Implement `frontend/src/hooks/use-websocket.ts` with auto-reconnect, ping/pong, and typed event listeners.
- [ ] Integration Verification:
  - [ ] Verify frontend metric cards update in real time when ESP32 publishes without page refresh.

---

## Phase 9: Local UI: TFT SPI Display & Buzzer Audio
- [x] TFT Display Driver (ESP32):
  - [x] Create `firmware/esp32/src/display/tft_display.h/cpp` with Adafruit GFX / ST7789 / ST7735 support.
  - [x] Render high-contrast live dashboard: Air Temp, Humidity, Water TDS, Uptime.
- [x] Buzzer & Multi-Modal Alert Engine:
  - [x] Create `firmware/esp32/src/alerts/alert_manager.h/cpp` with BC547 NPN driver on GPIO 25.
  - [x] Implement synchronized audio chirps, LED strobe, and TFT alert banner for boot, low moisture, heat stress, and TDS out-of-bounds.

---

## Phase 10: Multi-Sensor Expansion (pH, TDS/EC, Moisture, Flow, Water Level)
- [x] TDS Sensor (`tds-01`):
  - [x] Implement `firmware/esp32/src/sensors/tds_sensor.h/cpp` with median filtering and temperature compensation on GPIO 34.
  - [x] Integrate with canonical JSON telemetry (`tds` metric in `ppm`).
- [x] Moisture Sensor (`moisture-01`):
  - [x] Implement `firmware/esp32/src/sensors/moisture_sensor.h/cpp` with analog sampling and 0-100% calibration on GPIO 35.
  - [x] Integrate with canonical JSON telemetry (`substrate_moisture` metric in `%`).
- [ ] pH Sensor (`ph-01`):
  - [ ] Skipped for initial bring-up (sensor hardware currently unavailable).
- [x] Analog & Environmental Expansion:
  - [x] Implement TDS sensor driver (`firmware/esp32/src/sensors/tds_sensor.h/cpp`) with temperature compensation.
  - [x] Implement Soil/Substrate Moisture sensor driver (`firmware/esp32/src/sensors/moisture_sensor.h/cpp`).
  - [x] Implement YF-S201 Water Flow Sensor driver (`firmware/esp32/src/sensors/flow_sensor.h/cpp`) with hardware pulse interrupts.

---

## Phase 11: Actuators & Closed-Loop Safety (Physical Milestone P1)

- [x] Relay Driver:
  - [x] Create `firmware/esp32/src/actuators/relay_actuator.h/cpp` (Active-LOW configurable).
  - [x] Support Pump and Valve actuators with state verification.
  - [x] Safe startup initialization (defaulting immediately to OFF).
- [x] Closed-Loop Safety & Interlocks:
  - [x] Create `firmware/esp32/src/safety/safety_manager.h/cpp`.
  - [x] Implement Pump Dry-Run Protection (Pump ON + 0.0 L/min flow > 8s -> AUTO-OFF).
  - [x] Implement Max Continuous Runtime Cutoff (300s limit).
  - [x] Implement Smart Auto-Irrigation logic (Moisture < 25% ON, >= 75% OFF).
  - [x] Live Interactive Serial CLI: `PUMP ON`, `PUMP OFF`, `PUMP TOGGLE`, `AUTO WATER ON/OFF`, `RESET FAULT`.
- [ ] Full Control Loop Verification:
  - [ ] Test command from Web Dashboard -> Backend -> MQTT -> ESP32 -> Relay -> Status -> Dashboard.

---

## Phase 12: Camera Capture Pipeline
- [ ] Raspberry Pi Camera Service:
  - [ ] Implement `edge/camera/capture_service.py` using `libcamera` / OpenCV.
  - [ ] Capture periodic high-resolution still frames (e.g. every 15–30 mins).
  - [ ] Expose HTTP endpoint or upload image to backend object storage.
  - [ ] Publish image capture event to `hydroponics/esp32-01/events`.

---

## Phase 13: Computer Vision & Plant Health Analysis
- [ ] Plant Health Analysis Module:
  - [ ] Implement `edge/cv/plant_analyzer.py` using OpenCV.
  - [ ] Extract plant canopy coverage area (segmentation mask).
  - [ ] Compute Excess Green Index (ExG) and color histograms for yellowing/necrosis detection.
  - [ ] Publish normalized CV metrics (`plant_canopy_coverage`, `green_index`) to telemetry stream.

---

## Phase 14: Predictive AI & Automation Engine
- [ ] Cloud Analytics:
  - [ ] Implement moving-average rate-of-change analytics for nutrient depletion.
  - [ ] Generate smart notification rules for pH drift and water refill reminders.

---

## Phase 15: Production Hardening, Security & Verification
- [ ] Transport Security:
  - [ ] Enable TLS for MQTT (`8883`) with server certificates.
  - [ ] Enable HTTPS / WSS for Web Dashboard and API endpoints.
- [ ] Reliability & Watchdogs:
  - [ ] Enable ESP32 Task Watchdog Timer (`esp_task_wdt`) to prevent firmware lockups.
  - [ ] Add systemd service unit files with `Restart=always` on Raspberry Pi 5.
- [ ] Operational Runbook Verification:
  - [ ] Execute power cycle test: verify safe startup of all actuators and automatic network recovery.
  - [ ] Finalize end-to-end integration documentation in [`STATUS.md`](STATUS.md).
