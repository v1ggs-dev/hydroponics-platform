# Hydroponics Platform — Full Technical Report & Architecture Specification
**Document ID:** `REPORT1708`  
**Date:** August 17, 2026  
**System Version:** v0.1.0-MVP  
**Repository:** `hydroponics-platform`  
**Target Environments:** ESP32 (Firmware), Windows / Raspberry Pi 5 (Edge), Node.js / Supabase (Cloud), Next.js 14 (Web)

---

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [High-Level Architecture & Multi-Tier Topology](#2-high-level-architecture--multi-tier-topology)
3. [Data Flow Diagrams](#3-data-flow-diagrams)
   - 3.1 [Telemetry Flow (Sense to Dashboard)](#31-telemetry-flow)
   - 3.2 [Control Flow (Remote Actuation & Safety)](#32-control-flow)
   - 3.3 [Vision & Camera Ingestion Pipeline](#33-vision--camera-ingestion-pipeline)
4. [Tier 1: ESP32 Hardware & Firmware Layer](#4-tier-1-esp32-hardware--firmware-layer)
   - 4.1 [Complete Pinout & Wiring Specification](#41-complete-pinout--wiring-specification)
   - 4.2 [Sensor Acquisition & Calibration](#42-sensor-acquisition--calibration)
   - 4.3 [Local Autonomous Safety Interlocks](#43-local-autonomous-safety-interlocks)
   - 4.4 [TFT SPI Color Display (ST7735 160x128) & Audio](#44-tft-spi-color-display--audio)
5. [Tier 2: Edge Computing & Gateway Layer (Raspberry Pi 5 / PC)](#5-tier-2-edge-computing--gateway-layer)
   - 5.1 [High-Speed Serial Bridge (115200 Baud)](#51-high-speed-serial-bridge)
   - 5.2 [Lossless SQLite Offline Telemetry Buffer](#52-lossless-sqlite-offline-telemetry-buffer)
   - 5.3 [Paho-MQTT Bridge & Topic Architecture](#53-paho-mqtt-bridge--topic-architecture)
6. [Tier 3: Cloud Backend & Database Tier](#6-tier-3-cloud-backend--database-tier)
   - 6.1 [Supabase PostgreSQL 16 & Prisma ORM Schema](#61-supabase-postgresql-16--prisma-orm-schema)
   - 6.2 [Node.js / TypeScript REST API (`/api/v1`)](#62-nodejs--typescript-rest-api)
   - 6.3 [60fps Real-Time WebSocket Streaming Server (`/ws`)](#63-60fps-real-time-websocket-streaming-server)
   - 6.4 [Real-Time MJPEG Video Streaming Endpoint](#64-real-time-mjpeg-video-streaming-endpoint)
7. [Tier 4: Next.js 14 Minimalist Web Dashboard](#7-tier-4-nextjs-14-minimalist-web-dashboard)
   - 7.1 [Design Aesthetics & UI Tokens](#71-design-aesthetics--ui-tokens)
   - 7.2 [Live KPI Telemetry Grid (6 Metrics)](#72-live-kpi-telemetry-grid)
   - 7.3 [Interactive ECharts Time-Series Visualizer](#73-interactive-echarts-time-series-visualizer)
   - 7.4 [Actuator Control Panel & Alarms Log](#74-actuator-control-panel--alarms-log)
   - 7.5 [Live Plant Video Stream Player](#75-live-plant-video-stream-player)
8. [Tier 5: Camera Ingestion & External AI Model Interface](#8-tier-5-camera-ingestion--external-ai-model-interface)
   - 8.1 [ESP32-CAM Firmware & OV2640 Driver](#81-esp32-cam-firmware--ov2640-driver)
   - 8.2 [1-Line Python Integration Hook for AI/ML](#82-1-line-python-integration-hook-for-aiml)
9. [Operational Runbook & Command Reference](#9-operational-runbook--command-reference)
   - 9.1 [Flashing Firmware](#91-flashing-firmware)
   - 9.2 [Starting Services Individually](#92-starting-services-individually)
   - 9.3 [All-In-One Full-Stack Launcher](#93-all-in-one-full-stack-launcher)
   - 9.4 [API Endpoint Catalog & Test Commands](#94-api-endpoint-catalog--test-commands)
10. [Future Roadmap & Next Milestones](#10-future-roadmap--next-milestones)

---

## 1. Executive Summary

The **Hydroponics Monitoring, Control, Automation, and Computer-Vision Platform** is an enterprise-grade, modular IoT platform designed for precision vertical farming and nutrient film technique (NFT) hydroponics systems.

The platform executes a strict separation of concerns across physical hardware controllers, edge compute nodes, cloud persistence, and reactive user interfaces:
- **Physical Safety First**: The physical controller (ESP32) operates autonomous safety rules (dry-run cutoff, flood prevention, auto-irrigation) independent of cloud connectivity.
- **Wired Zero-Latency Edge Link**: Physical sensors communicate with the Edge Gateway via high-speed wired USB serial (115200 baud), avoiding local Wi-Fi latency, packet dropouts, and display brownouts.
- **Cloud-Native Persistence**: Telemetry is automatically synced to a cloud-hosted **Supabase PostgreSQL 16** cluster with Prisma ORM.
- **Sub-Second Real-Time Monitoring**: A Node.js TypeScript API server streams live sensor metrics at 60fps via WebSockets to a Next.js 14 dashboard.
- **Modular AI/CV Ready**: A dedicated wired ESP32-CAM streams live video and exposes a 1-line Python interface (`get_latest_frame()`) for external computer vision and machine learning models.

---

## 2. High-Level Architecture & Multi-Tier Topology

```text
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                                SYSTEM ARCHITECTURE TOPOLOGY                               │
└───────────────────────────────────────────────────────────────────────────────────────────┘

 [ ESP32 Main Controller ]              [ ESP32-CAM Vision Node ]
   • DHT11 Temp/Humidity                  • OV2640 Sensor (800x600 HD)
   • Analog TDS Probe                     • USB-MB Base Shield
   • Substrate Moisture Sensor
   • YF-S201 Flow Sensor (Pulse)
   • 1.8" ST7735 TFT SPI Display
   • Buzzer Fanfare & LED Alerts
   • Active-LOW Relay / Pump Driver
               │                                      │
               │ (Wired USB Serial @ 115200)          │ (Wired USB Serial @ 115200)
               ▼                                      ▼
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                   EDGE COMPUTING NODE (Raspberry Pi 5 / Windows PC)                       │
│                                                                                           │
│  [ Serial Bridge & Telemetry Parser ]    [ Continuous Camera Streamer ]                   │
│    • Canonical JSON Validation             • High-Speed Frame Ingestion                   │
│    • UTC ISO 8601 Timestamping             • Auto-Archive to snapshots/latest.jpg         │
│                                                                                           │
│  [ Lossless SQLite FIFO Buffer ]         [ ★ AI Model Integration Hook ]                  │
│    • edge_telemetry_buffer.db              • from edge.camera import get_latest_frame     │
│    • Offline fallback queue                • Decodes to (600, 800, 3) RGB NumPy Array     │
│                                                                                           │
│  [ Mosquitto MQTT Broker ] (0.0.0.0:1883 TCP & 9001 WS)                                   │
│    • Topics: hydroponics/{deviceId}/telemetry, commands, status, events                   │
└───────────────────────────────────────────────────────────────────────────────────────────┘
               │                                      │
               │ (MQTT Telemetry / Commands)          │ (MJPEG Video Stream Framepipe)
               ▼                                      ▼
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                           CLOUD BACKEND SERVICE (Port 4000)                               │
│                                                                                           │
│  [ MQTT Ingestion Worker ] ──────────────────► [ Supabase Cloud PostgreSQL 16 ]           │
│    • Batch-inserts normalized measurements       • Tables: devices, measurements,         │
│    • Updates device online heartbeats                      commands, alerts               │
│                                                                                           │
│  [ REST API Layer (/api/v1) ]                [ Realtime Streamers ]                       │
│    • GET  /telemetry/latest & history          • WebSocket Server (ws://localhost:4000/ws)│
│    • POST /commands (Actuator Dispatch)        • MJPEG Video Server (/api/v1/camera/stream)│
└───────────────────────────────────────────────────────────────────────────────────────────┘
               ▲                                      ▲
               │ (REST API & WebSockets)              │ (Live MJPEG Stream)
               ▼                                      ▼
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                     WEB APPLICATION DASHBOARD (Next.js 14 - Port 3000)                    │
│                                                                                           │
│  • Top Navigation with Live Connectivity Telemetry (ESP32, Supabase, WebSocket)          │
│  • 6 Real-Time Metric KPI Cards with Thermal/EC/Moisture Status Badges                   │
│  • Interactive 24-Hour ECharts Time-Series Visualizer (1h, 6h, 24h, 7d ranges)           │
│  • Live Plant Camera Stream Player (REC • 800x600 HD)                                     │
│  • Actuator Remote Control Center (Pump Override, Auto-Watering, Safety Reset)            │
│  • Live System Alarms & Health Activity Stream                                            │
└───────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Flow Diagrams

### 3.1 Telemetry Flow
```text
Sensor Pin Read (ADC / Pulse / 1-Wire)
  ↓
ESP32 Normalization & Safety Interlock Validation
  ↓
ST7735 TFT Screen Rendering & Serial JSON Formatting
  ↓
Wired USB Serial (115200 Baud)
  ↓
Edge Gateway Serial Reader (Python pyserial)
  ↓
SQLite Offline FIFO Buffering (if MQTT disconnected)
  ↓
MQTT Broker (hydroponics/esp32-01/telemetry)
  ↓
Cloud Backend MQTT Consumer (Node.js/TypeScript)
  ↓
Supabase Cloud PostgreSQL 16 (measurements table)
  ↓
WebSocket Server Broadcast (ws://localhost:4000/ws)
  ↓
Next.js 14 Web Dashboard (useTelemetry hook -> 60fps UI update)
```

### 3.2 Control Flow
```text
User Clicks "TURN ON" on Web Dashboard (Port 3000)
  ↓
POST http://localhost:4000/api/v1/commands {"action":"SET_STATE","value":"ON"}
  ↓
Backend logs Command in Supabase (status="PENDING")
  ↓
Backend publishes to MQTT topic: hydroponics/esp32-01/commands
  ↓
Edge Gateway receives MQTT command -> Forwards via Serial to COM6: {"cmd":"PUMP_ON"}
  ↓
ESP32 Firmware Receives Command:
  ├── Check 1: Is dry-run safety lockout active? (If yes -> Reject)
  ├── Check 2: Set GPIO 26 LOW (Relay Energized)
  ├── Check 3: Start 8s Flow Monitor Timer & 5m Max Runtime Watchdog
  └── Check 4: Update TFT display to show "PUMP: ON"
  ↓
ESP32 Telemetry Packet reports actual hardware state ("pump":"ON")
  ↓
Backend updates Command in Supabase (status="EXECUTED")
  ↓
Web Dashboard reflects confirmed pump state.
```

### 3.3 Vision & Camera Ingestion Pipeline
```text
ESP32-CAM (AI-Thinker OV2640) on COM9
  ↓
Python Stream Service (scripts/start_camera_stream.py) sends 'CAPTURE\n'
  ↓
ESP32-CAM grabs 800x600 JPEG into PSRAM -> Sends ---FRAME_START:<len>--- + bytes
  ↓
Python Stream Service writes frame atomically to edge/camera/snapshots/latest.jpg
  ↓
  ├── Path A: Backend exposes /api/v1/camera/stream (MJPEG 7fps) -> Next.js Web Player
  └── Path B: AI Engineer calls from edge.camera import get_latest_frame -> NumPy Array -> PyTorch/YOLO
```

---

## 4. Tier 1: ESP32 Hardware & Firmware Layer

### 4.1 Complete Pinout & Wiring Specification

| Component | ESP32 Pin | Signal Type | Electrical Notes |
|---|---|---|---|
| **DHT11 Air Temp & Humidity** | `GPIO 4` | Digital Single-Wire | Pull-up 10kΩ to 3.3V. Measures Ambient Temp (0–50°C) & RH (20–90%). |
| **Analog TDS Nutrient Sensor** | `GPIO 34` | Analog Input (ADC1_CH6)| 0–3.3V range. Submerged probe with temperature-compensated PPM conversion. |
| **Soil Moisture Sensor** | `GPIO 35` | Analog Input (ADC1_CH7)| 0–3.3V range. Calibrated dry ($3100\text{ raw}$) to wet ($1200\text{ raw}$) percentage. |
| **YF-S201 Water Flow Sensor** | `GPIO 13` | Digital Pulse Interrupt | Hall-effect sensor. Hardware interrupt `FALLING`. Pulse factor: $7.5\text{ pulses/sec} = 1\text{ L/min}$. |
| **1-Channel 5V Relay (Pump)** | `GPIO 26` | Digital Output | Active-LOW relay trigger. Controls 9V/12V DC water pump with flyback diode isolation. |
| **Piezo Buzzer Alert Driver** | `GPIO 25` | Digital Output / PWM | Driven via BC547 NPN transistor with 1kΩ base resistor. Generates audio fanfare & alarms. |
| **System Status LED** | `GPIO 2` | Digital Output | Onboard blue LED. Rapid strobe on dry-run safety fault. |
| **ST7735 TFT SPI: SCK (Clock)** | `GPIO 18` | Hardware SPI (VSPI) | High-speed clock line. |
| **ST7735 TFT SPI: SDA (MOSI)** | `GPIO 23` | Hardware SPI (VSPI) | Master-Out-Slave-In data line. |
| **ST7735 TFT SPI: A0 (DC)** | `GPIO 16` | Digital Output | Data/Command selector. |
| **ST7735 TFT SPI: RESET** | `GPIO 17` | Digital Output | Active-LOW hardware reset pin. |
| **ST7735 TFT SPI: CS (Select)** | `GPIO 5` | Hardware SPI (VSPI) | Chip select line. |
| **ST7735 TFT SPI: LED (Backlight)**| `3.3V` | Power (Backlight) | 3.3V rail. |
| **ST7735 TFT SPI: VCC / GND** | `5V` / `GND` | Power Supply | 5V VIN and common ground rail. |

---

### 4.2 Sensor Acquisition & Calibration

#### 1. Air Temperature & Humidity (DHT11)
- Initialized in non-blocking polling mode with a minimum read interval of $2000\text{ ms}$.
- Metric keys: `air_temperature` (°C) and `humidity` (% RH).

#### 2. Nutrient TDS (Total Dissolved Solids)
- ADC sample smoothing over 10 consecutive reads.
- Voltage conversion:
  $$V_{\text{adc}} = \frac{\text{raw}}{4095.0} \times 3.3$$
- Temperature-compensated TDS formula:
  $$\text{Compensation Coefficient} = 1.0 + 0.02 \times (T_{\text{air}} - 25.0)$$
  $$V_{\text{comp}} = \frac{V_{\text{adc}}}{\text{Compensation Coefficient}}$$
  $$\text{TDS (ppm)} = (133.42 \cdot V_{\text{comp}}^3 - 255.86 \cdot V_{\text{comp}}^2 + 857.39 \cdot V_{\text{comp}}) \times 0.5$$

#### 3. Substrate Moisture (%)
- 12-bit ADC acquisition on GPIO 35.
- Calibration mapping:
  $$\text{Raw}_{\text{dry}} = 3100, \quad \text{Raw}_{\text{wet}} = 1200$$
  $$\text{Moisture (\%)} = \text{constrain}\left( \frac{\text{Raw}_{\text{dry}} - \text{Raw}}{\text{Raw}_{\text{dry}} - \text{Raw}_{\text{wet}}} \times 100.0, \, 0.0, \, 100.0 \right)$$

#### 4. Flow Rate & Volume Accumulator (YF-S201)
- Hardware pulse counting on GPIO 13 via IRAM ISR:
  $$\text{Flow Rate (L/min)} = \frac{\text{Pulse Count}}{7.5 \times \Delta t_{\text{seconds}}}$$
  $$\text{Volume Incremented (Liters)} = \frac{\text{Pulse Count}}{450.0}$$

---

### 4.3 Local Autonomous Safety Interlocks

The ESP32 firmware executes real-time hardware safety logic on a 50ms tick loop:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                      ESP32 LOCAL SAFETY STATE MACHINE                       │
└─────────────────────────────────────────────────────────────────────────────┘

    [ PUMP ON Command Received ]
               │
               ▼
    [ Check Lockout Status ]
      ├── If Dry-Run Lockout = ACTIVE ──► REJECT COMMAND (Alarm Buzzer)
      └── If Lockout = CLEAR ───────────► ENERGIZE RELAY (GPIO 26 LOW)
               │
               ▼
    [ 8-Second Dry-Run Protection Timer ]
      ├── Water Flow Detected (>0.1 L/min) ──► RESET Timer, Normal Operation
      └── No Flow Detected within 8.0s:
               ├── 1. DE-ENERGIZE RELAY IMMEDIATELY (GPIO 26 HIGH)
               ├── 2. SET dryRunLockout = TRUE
               ├── 3. TRIGGER Audible Buzzer Alarm & Rapid LED Strobe
               └── 4. TRANSMIT Critical Fault Event over Serial
               │
               ▼
    [ 5-Minute Continuous Flood Prevention Watchdog ]
      └── If continuous runtime exceeds 300s ──► AUTO-SHUTOFF PUMP
```

---

### 4.4 TFT SPI Color Display & Audio

- **Hardware**: 1.8-inch ST7735 TFT ($160\times 128$ resolution, 16-bit RGB565).
- **Startup Fanfare**: 6-second boot splash with system title, version banner, and C-Major ascending audio fanfare.
- **Live 2x2 Dashboard Layout**:
  - **Top-Left (Coral)**: Air Temperature (°C)
  - **Top-Right (Sky Blue)**: Relative Humidity (%)
  - **Bottom-Left (Emerald)**: Nutrient TDS (ppm)
  - **Bottom-Right (Amber)**: Substrate Moisture (%)
  - **Footer Bar**: Pump State (`[PUMP: OFF]` in Emerald / `[PUMP: ON]` in Amber / `[LOCKOUT]` in Rose).
- **Brownout Prevention**: Wi-Fi RF scanning is disabled (`#define ENABLE_WIFI false`) in wired mode to ensure clean 3.3V rail power, completely eliminating display artifacts.

---

## 5. Tier 2: Edge Computing & Gateway Layer

### 5.1 High-Speed Serial Bridge
- Located in [`edge/gateway/serial_bridge.py`](file:///d:/projects/hydroponics-platform/edge/gateway/serial_bridge.py).
- Auto-detects serial ports cross-platform (`COM6` on Windows / `/dev/ttyUSB0` on Linux).
- Non-blocking threaded read loop with automatic reconnection on disconnect.
- Validates canonical JSON schemas and enriches packets with UTC ISO 8601 timestamps.

### 5.2 Lossless SQLite Offline Telemetry Buffer
- Located in [`edge/gateway/storage_buffer.py`](file:///d:/projects/hydroponics-platform/edge/gateway/storage_buffer.py).
- Database file: `edge/gateway/edge_telemetry_buffer.db`.
- When MQTT broker or internet connection drops:
  - Telemetry packets are appended to the local SQLite FIFO queue.
  - On reconnect, records are flushed in chronological batches of 50 to the cloud without dropping data.

### 5.3 Paho-MQTT Bridge & Topic Architecture
- Located in [`edge/gateway/mqtt_bridge.py`](file:///d:/projects/hydroponics-platform/edge/gateway/mqtt_bridge.py).
- Standard topic hierarchy:

| Topic | Direction | Payload Description |
|---|---|---|
| `hydroponics/{deviceId}/telemetry` | Publish | Normalized 6-metric telemetry array with UTC timestamps. |
| `hydroponics/{deviceId}/status` | Publish | Device heartbeat & Last Will and Testament (`ONLINE` / `OFFLINE`). |
| `hydroponics/{deviceId}/events` | Publish | Urgent alarms (e.g. `DRY_RUN_FAULT`, `LOW_MOISTURE`). |
| `hydroponics/{deviceId}/commands` | Subscribe | Inbound remote actuator commands from Cloud Backend. |
| `hydroponics/edge/health` | Publish | Gateway CPU %, RAM %, and serial link quality. |

---

## 6. Tier 3: Cloud Backend & Database Tier

### 6.1 Supabase PostgreSQL 16 & Prisma ORM Schema

The database schema is defined in [`backend/prisma/schema.prisma`](file:///d:/projects/hydroponics-platform/backend/prisma/schema.prisma) and synced to Supabase Cloud PostgreSQL:

```prisma
datasource db {
  provider  = "postgresql"
  url       = env("DATABASE_URL")
  directUrl = env("DIRECT_URL")
}

generator client {
  provider = "prisma-client-js"
}

model Device {
  id              String         @id // e.g. "esp32-01"
  name            String
  type            String         @default("controller")
  firmwareVersion String?
  status          String         @default("ONLINE")
  lastSeenAt      DateTime       @default(now())
  createdAt       DateTime       @default(now())
  updatedAt       DateTime       @updatedAt
  measurements    Measurement[]
  commands        Command[]
  alerts          Alert[]

  @@map("devices")
}

model Measurement {
  id              BigInt         @id @default(autoincrement())
  deviceId        String
  sensorId        String         // "dht11-01", "tds-01", "moisture-01", "flow-01"
  metric          String         // "air_temperature", "humidity", "tds", "substrate_moisture", "flow_rate", "water_volume"
  value           Float
  unit            String         // "C", "%", "ppm", "L/min", "L"
  quality         String         @default("GOOD")
  timestamp       DateTime       @default(now())
  createdAt       DateTime       @default(now())

  device          Device         @relation(fields: [deviceId], references: [id], onDelete: Cascade)

  @@index([deviceId, metric, timestamp(sort: Desc)])
  @@index([timestamp(sort: Desc)])
  @@map("measurements")
}

model Command {
  id              String         @id // e.g. "cmd-172389123"
  deviceId        String
  actuatorId      String         // "pump-01"
  action          String         // "SET_STATE", "TOGGLE", "RESET_FAULT"
  value           String?        // "ON", "OFF"
  status          String         @default("PENDING")
  createdAt       DateTime       @default(now())
  executedAt      DateTime?

  device          Device         @relation(fields: [deviceId], references: [id], onDelete: Cascade)

  @@map("commands")
}

model Alert {
  id              BigInt         @id @default(autoincrement())
  deviceId        String
  type            String         // "DRY_RUN_FAULT", "LOW_MOISTURE"
  severity        String         @default("WARNING")
  message         String
  resolved        Boolean        @default(false)
  createdAt       DateTime       @default(now())
  resolvedAt      DateTime?

  device          Device         @relation(fields: [deviceId], references: [id], onDelete: Cascade)

  @@index([deviceId, resolved])
  @@map("alerts")
}
```

---

### 6.2 Node.js / TypeScript REST API (`/api/v1`)

- Located in [`backend/src/`](file:///d:/projects/hydroponics-platform/backend/src).
- Endpoints:
  - `GET /api/v1/health` &rarr; Returns service uptime, database health (`CONNECTED (Supabase PostgreSQL)`).
  - `GET /api/v1/devices` &rarr; Lists all registered ESP32 units with live status.
  - `GET /api/v1/telemetry/latest` &rarr; Returns the latest snapshot for all 6 sensor metrics.
  - `GET /api/v1/telemetry/history` &rarr; Time-series queries with interval filtering (`1h`, `6h`, `24h`, `7d`, `30d`).
  - `POST /api/v1/commands` &rarr; Dispatches remote actuator commands over MQTT.
  - `GET /api/v1/alerts` &rarr; Lists active/historical hardware alarms.
  - `PATCH /api/v1/alerts/:id/resolve` &rarr; Marks alarm as resolved.
  - `GET /api/v1/camera/latest` &rarr; Serves the latest high-res plant JPEG.
  - `GET /api/v1/camera/stream` &rarr; Real-time MJPEG live video stream.
  - `GET /api/v1/camera/status` &rarr; Returns camera capture metadata.

---

### 6.3 60fps Real-Time WebSocket Streaming Server (`/ws`)

- Express HTTP server upgraded with `ws` WebSocketServer on `/ws`.
- Broadcasts JSON events on MQTT message arrival:
  - `telemetry` &rarr; live sensor numbers.
  - `device_status` &rarr; online/offline transitions.
  - `alert` &rarr; instant hardware warnings.

---

### 6.4 Real-Time MJPEG Video Streaming Endpoint

- Stream URL: `http://localhost:4000/api/v1/camera/stream`
- Content Type: `multipart/x-mixed-replace; boundary=frame`
- Streams frames at ~7 FPS with zero browser plugins or WebRTC complexity required.

---

## 7. Tier 4: Next.js 14 Minimalist Web Dashboard

### 7.1 Design Aesthetics & UI Tokens
- **Theme**: Minimalist dark industrial design.
- **Palette**: Slate and zinc backgrounds (`#090A0F`, `#11131A`), refined borders (`#232838`), semantic accents (Coral `#F87171`, Sky Blue `#38BDF8`, Emerald `#34D399`, Amber `#FBBF24`, Cyan `#60A5FA`).
- **Typography**: Inter for UI labels, JetBrains Mono for precision tabular sensor figures.

### 7.2 Live KPI Telemetry Grid
Displays 6 responsive cards:
1. **Air Temperature**: Precision °C with thermal status ("Optimal 20–26°C").
2. **Relative Humidity**: % RH with humidity band indicator.
3. **Nutrient Concentration (TDS)**: ppm with EC range status.
4. **Substrate Moisture**: % with soil saturation warnings ("LOW / DRY", "OPTIMAL").
5. **Water Flow Rate**: L/min with active pumping flow indicator.
6. **Total Dispensed Volume**: Cumulative liters.

### 7.3 Interactive ECharts Time-Series Visualizer
- Multi-series line charts with smooth area gradients and dynamic tooltips.
- Time range filters: `1h`, `6h`, `24h`, `7d`.
- Metric view tabs: `All Overview`, `Environment`, `Nutrients & Moisture`, `Flow`.

### 7.4 Actuator Control Panel & Alarms Log
- **Water Pump Override Switch**: Instant ON/OFF toggle with state feedback.
- **Smart Auto-Irrigation Switch**: Autonomous trigger when substrate moisture $<25\%$.
- **Clear Safety Faults Button**: Resets dry-run lockouts.
- **Alarms Activity Log**: Chronological alert feed with one-click resolution.

### 7.5 Live Plant Video Stream Player
- Real-time video player consuming `/api/v1/camera/stream`.
- Features `REC • 800x600 HD` live indicator, Pause/Resume toggle, and reload action.

---

## 8. Tier 5: Camera Ingestion & External AI Model Interface

### 8.1 ESP32-CAM Firmware & OV2640 Driver
- Located in [`firmware/esp32_cam/`](file:///d:/projects/hydroponics-platform/firmware/esp32_cam).
- Configured for AI-Thinker ESP32-CAM with PSRAM enabled.
- Captures SVGA ($800\times 600$) or UXGA ($1600\times 1200$) JPEG frames into PSRAM.
- Streams frame envelope over Wired USB Serial (115200 baud) on `CAPTURE\n` trigger:
  $$\text{Envelope: } \texttt{---FRAME\_START:<length>---} + \text{raw JPEG bytes} + \texttt{---FRAME\_END---}$$

---

### 8.2 1-Line Python Integration Hook for AI/ML

Your external AI developer or friend can plug any PyTorch, TensorFlow, YOLO, or OpenCV model into the live camera stream with **one line of code**:

```python
from edge.camera import get_latest_frame, capture_snapshot

# 1. Grab the latest live plant frame as a standard NumPy array:
#    Format: RGB, Shape: (600, 800, 3), dtype: uint8
image_array = get_latest_frame(as_numpy=True)

# 2. Pass directly to AI model:
predictions = my_fine_tuned_ai_model.predict(image_array)
print("AI Predictions:", predictions)

# 3. Or trigger a fresh on-demand snapshot:
photo_path = capture_snapshot()
```

---

## 9. Operational Runbook & Command Reference

### 9.1 Flashing Firmware

#### Main ESP32 Sensor Controller (COM6)
```powershell
pio run -d firmware/esp32 --target upload --upload-port COM6
```

#### ESP32-CAM Vision Node (COM9)
```powershell
pio run -d firmware/esp32_cam --target upload --upload-port COM9
```

---

### 9.2 Starting Services Individually

Open separate PowerShell terminals:

#### Terminal 1: Start MQTT Message Broker
```powershell
python scripts/start_mqtt_broker.py
```

#### Terminal 2: Start Edge Gateway (Serial to MQTT)
```powershell
python scripts/start_edge_gateway.py
```

#### Terminal 3: Start Cloud Backend API & Supabase Ingestion
```powershell
python scripts/start_backend.py
```

#### Terminal 4: Start Next.js Web Dashboard
```powershell
python scripts/start_frontend.py
```

#### Terminal 5: Start Live Camera Stream (COM9)
```powershell
python scripts/start_camera_stream.py COM9
```

---

### 9.3 All-In-One Full-Stack Launcher

To start the entire platform with one single command:

```powershell
python scripts/start_full_stack.py
```
*(Automatically manages MQTT Broker, Backend API, Edge Gateway, and Next.js Web Dashboard with graceful shutdown on `Ctrl+C`).*

---

### 9.4 API Endpoint Catalog & Test Commands

#### 1. System & Database Health
```powershell
curl http://localhost:4000/api/v1/health
```

#### 2. Latest 6-Metric Telemetry
```powershell
curl http://localhost:4000/api/v1/telemetry/latest?deviceId=esp32-01
```

#### 3. 24-Hour Time-Series Historical Records
```powershell
curl "http://localhost:4000/api/v1/telemetry/history?deviceId=esp32-01&range=24h"
```

#### 4. Dispatch Remote Pump Control Command
```powershell
curl -X POST http://localhost:4000/api/v1/commands `
  -H "Content-Type: application/json" `
  -d '{"deviceId":"esp32-01","actuatorId":"pump-01","action":"SET_STATE","value":"ON"}'
```

#### 5. View Real-Time Video Stream
Open in browser:
```text
http://localhost:4000/api/v1/camera/stream
```

---

## 10. Future Roadmap & Next Milestones

1. **Raspberry Pi 5 Standalone Deployment**:
   - Write systemd service definitions (`hydro-gateway.service`, `hydro-stream.service`) so the Edge Gateway boots automatically on power-up.
2. **Physical Relay Module Plug-In**:
   - Connect the replacement 5V relay module to GPIO 26 to test physical water circulation with the flow meter.
3. **AI Vision Model Deployment**:
   - Hook your friend's fine-tuned model into `from edge.camera import get_latest_frame` to compute green leaf canopy percentage, growth velocity, and detect nutrient chlorosis.
4. **Cloud Production Deployment**:
   - Deploy the Next.js frontend to **Vercel** and the backend to **Render / Railway / Cloudflare**, allowing mobile access from anywhere in the world.

---
*End of Report `REPORT1708.md` — Generated for Hydroponics Platform.*
