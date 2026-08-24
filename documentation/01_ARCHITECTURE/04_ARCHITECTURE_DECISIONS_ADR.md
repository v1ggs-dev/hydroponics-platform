# Hydroponics Platform — Architecture Decision Records (ADR)

> This document tracks the significant architectural, protocol, hardware, and structural decisions made for the Hydroponics Platform.

---

## Record Index

- [ADR-001: Separation of Local Safety and Cloud Control](#adr-001-separation-of-local-safety-and-cloud-control)
- [ADR-002: Modular Telemetry and Command Normalization](#adr-002-modular-telemetry-and-command-normalization)
- [ADR-003: Transport Protocol Selection (MQTT + WebSocket)](#adr-003-transport-protocol-selection-mqtt--websocket)
- [ADR-004: Technology Stack Direction (PlatformIO, NestJS, Next.js, PostgreSQL)](#adr-004-technology-stack-direction)
- [ADR-005: Staged Vertical Slice Implementation Strategy](#adr-005-staged-vertical-slice-implementation-strategy)

---

### ADR-001: Separation of Local Safety and Cloud Control
- **Status**: Accepted
- **Context**: The hydroponics platform operates high-power actuators (pumps, solenoid valves) that can cause catastrophic physical damage (dry-running pump burnout, reservoir flooding) if left running improperly. Network connections and cloud services are prone to latency and outages.
- **Decision**: The ESP32 firmware is established as the sole authoritative hardware safety controller. Cloud services may only request state changes. The ESP32 evaluates all commands against local safety rules (water level threshold, max runtime timeout) before actuation.
- **Consequences**: Cloud outages do not compromise system safety. Remote commands return asynchronous 202 Accepted status and must be verified via actual state reports.

---

### ADR-002: Modular Telemetry and Command Normalization
- **Status**: Accepted
- **Context**: Baseline hardware (DHT11, analog pH/TDS) will change over time. Different sensor models and actuator drivers must be swappable without rewriting backend schemas or web dashboards.
- **Decision**: All measurements use a normalized data model containing `sensorId`, `metric`, `value`, `unit`, `quality`, and `timestamp`. Actuators are addressed by logical IDs (e.g. `pump-01`, `valve-01`). GPIO pin numbers and ADC channels are strictly confined to firmware configuration.
- **Consequences**: Adding new sensors requires no database schema modifications or frontend protocol redesigns.

---

### ADR-003: Transport Protocol Selection (MQTT + WebSocket)
- **Status**: Accepted
- **Context**: Embedded controllers require low-overhead binary/text transport, while web browsers require low-latency bi-directional updates.
- **Decision**: MQTT over TCP/TLS is used for ESP32 &bull; Edge &bull; Cloud Backend communication. WebSockets are used for Backend &bull; Web Dashboard live updates. Web clients never communicate directly with MQTT brokers or microcontrollers.
- **Consequences**: Strict boundary enforcement; frontend operates securely over standard web protocols while IoT hardware leverages lightweight pub/sub with Last Will and Testament (LWT).

---

### ADR-004: Technology Stack Direction
- **Status**: Accepted
- **Context**: Rapid 4–5 day MVP turnaround requires mature, modular, typed frameworks with first-class tooling.
- **Decision**:
  - **Firmware**: PlatformIO with C/C++ (Arduino framework on ESP32).
  - **Edge Gateway**: Python 3 with `paho-mqtt` and SQLite offline buffer.
  - **Cloud Backend**: Node.js LTS with NestJS (TypeScript), Prisma ORM, and PostgreSQL.
  - **Web Dashboard**: Next.js 14 (App Router), Tailwind CSS, shadcn/ui, and ECharts.
- **Consequences**: High development velocity, end-to-end type safety in TypeScript, reproducible builds, and clear separation of concerns.

---

### ADR-005: Staged Vertical Slice Implementation Strategy
- **Status**: Accepted
- **Context**: Attempting to implement all sensors, computer vision, and cloud dashboards simultaneously leads to high integration risk.
- **Decision**: The system will be built and verified in vertical slices:
  1. `ESP32 + DHT11 -> USB Serial`
  2. `ESP32 -> Wi-Fi -> MQTT`
  3. `MQTT -> Backend -> PostgreSQL`
  4. `Backend -> WebSocket -> Next.js Dashboard`
  5. Actuator control loop & local safety interlocks
  6. Multi-sensor expansion (pH, EC, flow, level)
  7. Camera & computer vision enhancements
- **Consequences**: Each milestone is testable and verifiable before proceeding to dependent tiers.