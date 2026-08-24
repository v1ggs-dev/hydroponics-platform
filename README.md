# Hydroponics Platform

An end-to-end, modular IoT platform for automated hydroponics monitoring, environmental sensing, local hardware safety, computer vision, and real-time cloud control.

---

## 📚 Master Documentation Repository

All system architecture specifications, hardware schematics, wiring pinouts, communication protocols, and technical reports have been consolidated into the **[`documentation/`](documentation/)** directory:

👉 **[Open Master Documentation Index](documentation/00_DOCUMENTATION_INDEX.md)**

---

## 📁 Documentation Structure

```text
documentation/
├── 00_DOCUMENTATION_INDEX.md
│
├── 00_OVERVIEW_AND_REPORTS/
│   ├── 01_FULL_TECHNICAL_REPORT_1708.md          # Complete technical architecture report
│   ├── 02_PROJECT_OVERVIEW.md                    # Core project introduction
│   ├── 03_SYSTEM_STATUS_AND_METRICS.md           # Live milestone tracking & operational state
│   ├── 04_IMPLEMENTATION_CHECKLIST.md            # Phase-by-phase implementation checklist
│   ├── 05_AI_AGENT_INSTRUCTIONS.md               # Architecture guidelines & rules
│   └── 06_DEVELOPMENT_ENVIRONMENT_GUIDE.md       # Windows / Linux developer setup
│
├── 01_ARCHITECTURE/
│   ├── 01_SYSTEM_ARCHITECTURE.md                 # 4-tier architecture overview
│   ├── 02_SYSTEM_SUBSYSTEMS_SPEC.md              # Subsystem boundaries & contracts
│   ├── 03_DATA_FLOW_PIPELINES.md                 # Sense, Transport, Store & Visualize
│   ├── 04_ARCHITECTURE_DECISIONS_ADR.md          # Architecture Decision Records
│   ├── 05_SECURITY_AND_SAFETY_ARCHITECTURE.md    # Safety state machines & access control
│   ├── 06_POWER_DISTRIBUTION_SPEC.md             # Power rails & electrical specs
│   └── 07_OPERATIONAL_RUNBOOK.md                 # Production deployment & emergency runbook
│
├── 02_HARDWARE_AND_WIRING/
│   ├── 01_HARDWARE_BOM_SPECIFICATION.md          # Bill of Materials & sensors
│   ├── 02_ESP32_PINOUT_REFERENCE.md              # Authoritative GPIO pinout table
│   ├── 03_COMPLETE_WIRING_GUIDE.md               # Step-by-step breadboard & terminal wiring
│   └── 04_ELECTRICAL_SCHEMATIC_AND_RELAYS.md     # Transistor drivers, relays & flyback diodes
│
└── 03_COMMUNICATION_PROTOCOLS/
    ├── 01_TELEMETRY_SCHEMA_SPEC.md               # Canonical sensor JSON schema
    ├── 02_MQTT_TOPICS_AND_MESSAGES_SPEC.md       # MQTT topic hierarchy & QoS rules
    ├── 03_REST_AND_WEBSOCKET_API_SPEC.md         # Express REST & 60fps WebSocket endpoints
    └── 04_ACTUATOR_COMMANDS_SPEC.md              # Remote control dispatch schemas
```

---

## 🚀 Quickstart: Launching the Full Stack

To start the entire platform with one single command:

```powershell
python scripts/start_full_stack.py
```

This launches:
1. **MQTT Message Broker** (Port 1883 & 9001)
2. **Cloud Backend & Supabase Ingestion** (Port 4000)
3. **Edge Gateway Serial Bridge** (COM6)
4. **Next.js 14 Web Dashboard** (Port 3000)

👉 Open Web Dashboard in your browser: **[http://localhost:3000](http://localhost:3000)**