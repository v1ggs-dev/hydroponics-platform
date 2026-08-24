# 🌿 Hydroponics Platform — Manual Service Startup Guide

This document contains the **direct, native terminal commands** to build, flash, and run every service of the Hydroponics Platform manually in separate terminals **without using any manager or wrapper scripts**.

---

## 📋 Architectural Startup Order

Services **must** be started in this chronological order:

```text
[1. MQTT Broker :1883] ──> [2. Edge Gateway (Serial)] ──> [3. Node.js Backend :4000] ──> [4. AI Service :8000] ──> [5. React UI :3000]
```

---

## ⚡ Step 0: Embedded Firmware Flashing (PlatformIO)

Make sure both ESP32 controllers are plugged in via USB. Open a terminal in `d:\projects\hydroponics-platform`:

### 1. Flash Node 1 — Environment & Hydraulics (`esp32_env` on `COM6`)
```powershell
pio run -d firmware/esp32_env -t upload --upload-port COM6
```

### 2. Flash Node 2 — Water Chemistry & Root Zone (`esp32_chem` on `COM7`)
```powershell
pio run -d firmware/esp32_chem -t upload --upload-port COM7
```

*(Both ST7735 color displays will light up immediately with their live telemetry cockpits).*

---

## 🖥️ Step 1: Terminal 1 — Start MQTT Message Broker (Port 1883)

The message broker must be running first so the Edge Gateway and Backend can communicate.

```powershell
cd D:\projects\hydroponics-platform
python scripts/start_mqtt_broker.py
```

* **TCP MQTT Port:** `1883`
* **WebSocket Port:** `9001`
* **Expected Output:**
  ```text
  [OK] HYDROPONICS MQTT BROKER RUNNING (Port 1883 & WebSocket 9001)
  READY FOR INCOMING TELEMETRY
  ```

---

## 🖥️ Step 2: Terminal 2 — Start Multi-Node Edge Gateway

Bridges the physical ESP32 USB serial streams to the local MQTT broker with offline SQLite buffering.

```powershell
cd D:\projects\hydroponics-platform\edge\gateway
python main.py
```

* **Serial Ports Scanned:** `COM6` & `COM7` (Baud: `115200`)
* **MQTT Topics Published:**
  - `hydroponics/esp32-env/telemetry`
  - `hydroponics/esp32-chem/telemetry`
* **Expected Output:**
  ```text
  [INFO] Serial Bridge: COM6 (Active)
  [INFO] Serial Bridge: COM7 (Active)
  [INFO] Connected to MQTT broker at 127.0.0.1:1883
  ```

> 💡 *Note: If physical ESP32 hardware is unplugged, you can run the simulator in this terminal instead:*
> ```powershell
> cd D:\projects\hydroponics-platform
> python scripts/modules/simulator.py
> ```

---

## 🖥️ Step 3: Terminal 3 — Start Cloud Backend API Server (Port 4000)

Runs the Node.js Express server, Supabase PostgreSQL database connection, and 60fps real-time WebSocket broadcaster.

```powershell
cd D:\projects\hydroponics-platform\backend
npm run dev
```

* **REST API Base:** `http://localhost:4000/api/v1`
* **WebSocket Server:** `ws://localhost:4000/ws`
* **Health Endpoint:** `http://localhost:4000/api/v1/health`
* **Expected Output:**
  ```text
  🚀 HYDROPONICS BACKEND RUNNING ON http://localhost:4000
  ✅ [MQTT Service] Connected to MQTT broker!
  📥 [MQTT Service] Subscribed to telemetry, status & events topics.
  ```

---

## 🖥️ Step 4: Terminal 4 — Start AgroEye AI Microservice (Port 8000)

Runs the FastAPI Python server hosting the **YOLO11n-cls tomato pathology model**, **FAISS vector database**, and **Groq Llama 3.3 70B agronomist**.

```powershell
cd D:\projects\hydroponics-platform
python -m uvicorn ai.main:app --host 0.0.0.0 --port 8000 --reload
```

* **Swagger API Docs:** `http://localhost:8000/docs`
* **YOLO Vision API:** `POST http://localhost:8000/api/v1/vision/classify`
* **Multimodal RAG API:** `POST http://localhost:8000/api/v1/recommendation/generate`
* **Expected Output:**
  ```text
  INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
  INFO:     Application startup complete.
  ```

---

## 🖥️ Step 5: Terminal 5 — Start React 18 / Next.js 14 Dashboard (Port 3000)

Runs the user web interface with sliding views, live telemetry cards, VPD gauges, pump controls, and AI leaf diagnostics.

```powershell
cd D:\projects\hydroponics-platform\frontend
npm run dev
```

* **Dashboard Web App:** `http://localhost:3000`
* **Expected Output:**
  ```text
  ▲ Next.js 14.2.35
  - Local: http://localhost:3000
  ✓ Ready in 1.8s
  ```

---

## 🌐 Browser URLs & Port Reference

| Service | Port | Local URL | Purpose |
|---|---|---|---|
| 🌿 **React Web Dashboard** | `3000` | [http://localhost:3000](http://localhost:3000) | Live telemetry, VPD gauges, AI plant scanner, pump controls |
| ☁️ **Cloud Backend API** | `4000` | [http://localhost:4000/api/v1/health](http://localhost:4000/api/v1/health) | REST API, WebSocket stream, Supabase PostgreSQL link |
| 🤖 **AgroEye AI Service** | `8000` | [http://localhost:8000/docs](http://localhost:8000/docs) | FastAPI interactive Swagger documentation & inference |
| 🗄️ **Prisma Database Studio** | `5555` | [http://localhost:5555](http://localhost:5555) | Web GUI to view/edit database tables in Supabase |
| 📡 **Mosquitto MQTT Broker** | `1883` | `tcp://127.0.0.1:1883` | Raw binary MQTT pub/sub message transport |

---

## 🛠️ Additional Database & Tooling Commands

### Open Prisma Database Studio (Web GUI)
```powershell
cd D:\projects\hydroponics-platform\backend
npx prisma studio --port 5555
```

### Push Database Schema Changes to Supabase
```powershell
cd D:\projects\hydroponics-platform\backend
npx prisma db push
```

### Serial Monitor with Actuation Keyboard Shortcuts (`1`, `0`, `r`, `a`)
```powershell
python manager.py monitor -p COM6
```

---

## 🛑 How to Clean Up All Ports
If any process is lingering in the background, you can kill all platform ports (`1883`, `3000`, `4000`, `5555`, `8000`) in one command:
```powershell
python manager.py clean
```
