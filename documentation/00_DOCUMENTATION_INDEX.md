# Hydroponics Platform — Master Documentation Index

Welcome to the centralized documentation repository for the Hydroponics Monitoring, Control, and Computer-Vision Platform.

All technical documentation, architecture specifications, wiring guides, protocols, and runbooks are organized within this directory.

---

## 📁 Documentation Structure

```text
documentation/
├── 00_DOCUMENTATION_INDEX.md
│
├── 00_OVERVIEW_AND_REPORTS/
│   ├── 01_FULL_TECHNICAL_REPORT_1708.md          # Comprehensive full-stack platform report
│   ├── 02_PROJECT_OVERVIEW.md                    # Core project introduction, quickstart & manager.py
│   ├── 03_SYSTEM_STATUS_AND_METRICS.md           # Live milestone tracking & 7 KPI metric state
│   ├── 04_IMPLEMENTATION_CHECKLIST.md            # Phase-by-phase implementation checklist
│   ├── 05_AI_AGENT_INSTRUCTIONS.md               # Strict architecture guidelines & rules
│   └── 06_DEVELOPMENT_ENVIRONMENT_GUIDE.md       # Windows / Linux developer environment setup
│
├── 01_ARCHITECTURE/
│   ├── 01_SYSTEM_ARCHITECTURE.md                 # High-level 4-tier Dual-ESP32 architecture definition
│   ├── 02_SYSTEM_SUBSYSTEMS_SPEC.md              # Detailed subsystem boundaries & contracts
│   ├── 03_DATA_FLOW_PIPELINES.md                 # Sense, Transport, Store & Visualize pipelines
│   ├── 04_ARCHITECTURE_DECISIONS_ADR.md          # Architecture Decision Records (ADRs)
│   ├── 05_SECURITY_AND_SAFETY_ARCHITECTURE.md    # Fail-safe state machines & access security
│   ├── 06_POWER_DISTRIBUTION_SPEC.md             # Multi-rail 5V/3.3V/12V electrical layout
│   └── 07_OPERATIONAL_RUNBOOK.md                 # Production deployment & emergency runbook
│
├── 02_HARDWARE_AND_WIRING/
│   ├── 01_HARDWARE_BOM_SPECIFICATION.md          # Dual-ESP32, Dual-Display & pH sensor Bill of Materials
│   ├── 02_ESP32_PINOUT_REFERENCE.md              # Authoritative Dual-ESP32 GPIO pinout tables
│   ├── 03_COMPLETE_WIRING_GUIDE.md               # Step-by-step breadboard & terminal wiring
│   ├── 04_ELECTRICAL_SCHEMATIC_AND_RELAYS.md     # Transistor drivers, relays & flyback diodes
│   └── 05_CUSTOM_PCB_DESIGN_SPECIFICATION.md     # Complete All-in-One Custom PCB Engineering Spec
│
└── 03_COMMUNICATION_PROTOCOLS/
    ├── 01_TELEMETRY_SCHEMA_SPEC.md               # Canonical Dual-Node sensor JSON schemas (inc. pH)
    ├── 02_MQTT_TOPICS_AND_MESSAGES_SPEC.md       # MQTT topic hierarchy & QoS rules
    ├── 03_REST_AND_WEBSOCKET_API_SPEC.md         # Express REST & 60fps WebSocket endpoints
    └── 04_ACTUATOR_COMMANDS_SPEC.md              # Remote control dispatch schemas
```

---

## 🚀 Quick Execution & Navigation

### 1. Unified Master Manager (`manager.py`):
- Run the interactive master manager:
  ```powershell
  python manager.py
  ```
- Or run 1-click stack commands:
  ```powershell
  python manager.py check         # Pre-flight environment diagnostic
  python manager.py stack start   # Full platform start
  python manager.py calibrate ph  # pH Sensor 2-point calibration wizard
  ```

### 2. Hardware Wiring & Sensors:
- Check **[`02_HARDWARE_AND_WIRING/02_ESP32_PINOUT_REFERENCE.md`](02_HARDWARE_AND_WIRING/02_ESP32_PINOUT_REFERENCE.md)** for exact GPIO connections.
- Check **[`02_HARDWARE_AND_WIRING/01_HARDWARE_BOM_SPECIFICATION.md`](02_HARDWARE_AND_WIRING/01_HARDWARE_BOM_SPECIFICATION.md)** for the complete component list.

### 3. Software & Protocols:
- Check **[`03_COMMUNICATION_PROTOCOLS/01_TELEMETRY_SCHEMA_SPEC.md`](03_COMMUNICATION_PROTOCOLS/01_TELEMETRY_SCHEMA_SPEC.md)** for JSON telemetry envelopes.
- Check **[`03_COMMUNICATION_PROTOCOLS/02_MQTT_TOPICS_AND_MESSAGES_SPEC.md`](03_COMMUNICATION_PROTOCOLS/02_MQTT_TOPICS_AND_MESSAGES_SPEC.md)** for MQTT topics.
