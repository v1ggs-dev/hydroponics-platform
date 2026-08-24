```markdown
# Hydroponics Platform — Data Flow Specification

## 1. Purpose

This document defines how data, commands, events, images, and system
state flow through the Hydroponics Platform.

The system consists of:

- ESP32 microcontroller
- Sensors
- Actuators
- Raspberry Pi 5 edge gateway
- Cameras
- Computer vision services
- MQTT broker
- Cloud backend
- PostgreSQL database
- REST API
- WebSocket
- Web dashboard

The primary architecture is:

    HARDWARE
       ↓
    ESP32
       ↓
    Raspberry Pi 5
       ↓
    MQTT
       ↓
    CLOUD BACKEND
       ↓
    DATABASE / API
       ↓
    WEB DASHBOARD

Control flows in the opposite direction:

    WEB DASHBOARD
       ↓
    BACKEND API
       ↓
    MQTT
       ↓
    RASPBERRY PI
       ↓
    ESP32
       ↓
    ACTUATOR

---

# 2. Core Architecture

The system is divided into five major layers:

    Layer 1 — Hardware
    Layer 2 — Firmware
    Layer 3 — Edge
    Layer 4 — Cloud
    Layer 5 — Frontend

Architecture:

                    ┌──────────────────────────┐
                    │       WEB FRONTEND       │
                    │                          │
                    │ Dashboard                │
                    │ Charts                   │
                    │ Controls                 │
                    │ Alerts                   │
                    └────────────┬─────────────┘
                                 │
                          HTTPS / WebSocket
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │       CLOUD BACKEND      │
                    │                          │
                    │ REST API                 │
                    │ Authentication           │
                    │ Authorization            │
                    │ Business Logic           │
                    │ MQTT Client              │
                    └───────┬─────────┬────────┘
                            │         │
                         MQTT      PostgreSQL
                            │         │
                            ▼         ▼
                    ┌──────────────────────────┐
                    │      MQTT BROKER         │
                    └────────────┬─────────────┘
                                 │
                              Internet
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │      RASPBERRY PI 5      │
                    │                          │
                    │ Edge Gateway              │
                    │ Camera                   │
                    │ Computer Vision          │
                    │ Local Buffering          │
                    └────────────┬─────────────┘
                                 │
                               Wi-Fi
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │          ESP32           │
                    │                          │
                    │ Sensor Acquisition       │
                    │ Actuator Control         │
                    │ Local Safety             │
                    │ Device State             │
                    └────────────┬─────────────┘
                                 │
                     ┌───────────┴───────────┐
                     │                       │
                  SENSORS                ACTUATORS
                     │                       │
              DHT11 / pH / TDS          Pump / Valve
              Flow / Level              Relay / Buzzer
              Future Sensors            TFT Display

---

# 3. Layer Responsibilities

## 3.1 Hardware Layer

Contains:

- Sensors
- Pumps
- Valves
- Relays
- Buzzers
- TFT displays
- Cameras
- Power electronics
- Other physical components

Hardware generates physical measurements and responds to control
signals.

Hardware does not communicate directly with the cloud.

---

# 4. ESP32 Firmware Layer

The ESP32 is responsible for:

- Reading sensors
- Basic sensor validation
- Sensor sampling
- Device state
- Actuator control
- Local safety logic
- Wi-Fi connectivity
- MQTT communication
- Local error handling
- Device heartbeat/status

The ESP32 must remain capable of performing safety-critical actions
without cloud connectivity.

Example:

    LOW WATER
       ↓
    ESP32
       ↓
    PUMP OFF

This must work even when:

    Internet = OFFLINE
    MQTT = OFFLINE
    Backend = OFFLINE

---

# 5. Raspberry Pi Edge Layer

The Raspberry Pi 5 is the edge computing layer.

It is responsible for:

- ESP32 connectivity
- MQTT edge communication
- Cloud connectivity
- Local buffering
- Camera management
- Computer vision
- Edge processing
- Local system monitoring
- Future device orchestration

The Raspberry Pi should not replace the ESP32 as the hardware safety
authority.

The Raspberry Pi may lose connectivity without causing immediate
hardware safety failures.

---

# 6. Cloud Backend Layer

The backend is responsible for:

- REST API
- WebSocket
- Authentication
- Authorization
- Device management
- Telemetry ingestion
- Telemetry persistence
- Command creation
- MQTT integration
- Command tracking
- Alerts
- Dashboard aggregation
- Application business logic

The backend is the application authority.

It is not the physical safety authority.

---

# 7. Database Layer

PostgreSQL stores persistent application data.

Potential data:

- Devices
- Sensors
- Actuators
- Telemetry
- Commands
- Command results
- Alerts
- Users
- Device ownership
- Configuration
- Camera metadata
- Computer vision results

The database is not accessed directly by the frontend.

---

# 8. Frontend Layer

The frontend is responsible for:

- Dashboard rendering
- Charts
- Sensor cards
- Device status
- Actuator controls
- Alerts
- Historical data visualization
- Camera visualization
- Computer vision results

The frontend communicates only with:

    REST API
    WebSocket

The frontend must not communicate directly with:

    ESP32
    Raspberry Pi
    MQTT
    PostgreSQL

---

# 9. Primary Telemetry Flow

Telemetry is the most important data flow in the MVP.

Example:

    DHT11
       ↓
    ESP32
       ↓
    Wi-Fi
       ↓
    Raspberry Pi
       ↓
    MQTT
       ↓
    Backend
       ↓
    PostgreSQL
       ↓
    REST API / WebSocket
       ↓
    Frontend

---

# 10. Sensor Acquisition

The ESP32 periodically reads connected sensors.

Example:

    DHT11

produces:

    Temperature
    Humidity

The ESP32 converts the raw sensor output into normalized measurements.

Example:

    Raw sensor value
          ↓
    Firmware processing
          ↓
    27.4 °C

The firmware should attach:

- Sensor ID
- Metric
- Value
- Unit
- Quality
- Timestamp where appropriate

The telemetry contract is defined in:

    docs/protocols/TELEMETRY.md

---

# 11. Sensor Validation

Before publishing telemetry, the ESP32 should perform basic validation.

Examples:

    Sensor disconnected
    Invalid reading
    Out-of-range value
    Communication failure

Example:

    DHT11 read
       ↓
    Value = 27.4 °C
       ↓
    Valid
       ↓
    Publish

Invalid example:

    DHT11 read
       ↓
    NaN
       ↓
    Invalid
       ↓
    Do not publish as valid telemetry

The system should report sensor health where appropriate.

---

# 12. ESP32 Telemetry Generation

The ESP32 generates a telemetry message according to:

    docs/protocols/TELEMETRY.md

Example:

```json
{
  "version": 1,
  "messageId": "msg-001",
  "deviceId": "esp32-01",
  "type": "telemetry",
  "timestamp": "2026-08-14T10:30:00.000Z",
  "measurements": [
    {
      "sensorId": "dht11-01",
      "metric": "air_temperature",
      "value": 27.4,
      "unit": "C",
      "quality": "GOOD"
    }
  ]
}
```

---

# 13. ESP32 → Raspberry Pi

The ESP32 communicates with the Raspberry Pi wirelessly.

Preferred MVP architecture:

    ESP32
       ↓
    Wi-Fi
       ↓
    Raspberry Pi

The Raspberry Pi may provide the local Wi-Fi access point if the system
is designed to operate without a third-party router.

The ESP32 should not require direct internet access for normal operation.

---

# 14. Raspberry Pi Gateway

The Raspberry Pi receives data from the ESP32 and provides the edge
gateway function.

Conceptually:

    ESP32
       ↓
    Local Wi-Fi
       ↓
    Raspberry Pi Gateway

The gateway validates the message at the edge and forwards it toward
the cloud messaging layer.

---

# 15. MQTT Transport

MQTT is the primary messaging protocol between edge and cloud.

MQTT defines:

- Topics
- QoS
- Retained messages
- Device status
- Telemetry transport
- Commands
- Events
- Reconnection behavior

The MQTT protocol is defined in:

    docs/protocols/MQTT.md

---

# 16. Telemetry MQTT Topic

Telemetry uses:

    hydroponics/{deviceId}/telemetry

Example:

    hydroponics/esp32-01/telemetry

The message payload follows:

    TELEMETRY.md

---

# 17. Backend Telemetry Ingestion

The backend subscribes to telemetry topics.

Example:

    hydroponics/+/telemetry

Flow:

    MQTT Broker
       ↓
    Backend MQTT Consumer
       ↓
    Validate message
       ↓
    Check device identity
       ↓
    Check schema
       ↓
    Persist telemetry
       ↓
    Publish real-time event

---

# 18. Telemetry Validation

The backend must validate:

- Message structure
- Device ID
- Sensor ID
- Metric
- Value
- Unit
- Timestamp
- Message version
- Authorization/ownership

Invalid telemetry must not corrupt the database.

---

# 19. Telemetry Persistence

Validated telemetry is stored in PostgreSQL.

Example:

    ESP32
       ↓
    MQTT
       ↓
    Backend
       ↓
    Validation
       ↓
    PostgreSQL

The database becomes the historical source of truth.

---

# 20. Latest Telemetry

The backend should maintain an efficient representation of the latest
known device measurements.

The dashboard should not query millions of historical records just to
display:

    Current Temperature
    Current Humidity
    Current pH
    Current TDS

The latest state should be quickly accessible.

---

# 21. REST Telemetry Flow

When the frontend requests historical telemetry:

    Frontend
       ↓
    GET /api/v1/devices/{deviceId}/telemetry
       ↓
    Backend
       ↓
    Authorization
       ↓
    PostgreSQL
       ↓
    JSON response
       ↓
    Frontend

The API contract is defined in:

    docs/protocols/API.md

---

# 22. Real-Time Telemetry Flow

For live dashboard updates:

    ESP32
       ↓
    MQTT
       ↓
    Backend
       ↓
    WebSocket
       ↓
    Frontend

The frontend should not repeatedly poll the API for high-frequency
telemetry.

---

# 23. Dashboard Initialization

When the dashboard opens:

    Frontend
       ↓
    GET /api/v1/dashboard/summary
       ↓
    Backend
       ↓
    PostgreSQL
       ↓
    Initial dashboard state

Then:

    Frontend
       ↓
    WebSocket connection
       ↓
    Live events

This gives the dashboard both:

    Initial state

and:

    Real-time updates

---

# 24. Dashboard Data Flow

Example:

    DHT11
       ↓
    ESP32
       ↓
    MQTT
       ↓
    Backend
       ↓
    PostgreSQL
       ↓
    Dashboard API
       ↓
    Frontend

The frontend displays:

    Temperature
    Humidity

Additional sensors will follow the same architecture:

    pH
    TDS
    Water Temperature
    Flow
    Water Level
    EC
    ORP
    etc.

---

# 25. Command Flow

Commands flow from the dashboard toward the hardware.

Primary flow:

    Frontend
       ↓
    REST API
       ↓
    Backend
       ↓
    MQTT
       ↓
    Raspberry Pi
       ↓
    ESP32
       ↓
    Local Safety
       ↓
    Actuator

---

# 26. Creating a Command

Example:

User clicks:

    Pump ON

Frontend sends:

    POST /api/v1/devices/esp32-01/actuators/pump-01/commands

The backend:

    Authenticate
       ↓
    Authorize
       ↓
    Validate
       ↓
    Create command
       ↓
    Publish MQTT

---

# 27. Command MQTT Flow

The backend publishes to:

    hydroponics/{deviceId}/commands

Example:

    hydroponics/esp32-01/commands

The command format is defined in:

    docs/protocols/COMMANDS.md

---

# 28. Raspberry Pi Command Handling

The Raspberry Pi receives the command.

Example:

    MQTT
       ↓
    Raspberry Pi
       ↓
    Validate target device
       ↓
    Forward command to ESP32

The Raspberry Pi must not blindly execute commands intended for
another device.

---

# 29. ESP32 Command Handling

The ESP32 receives the command.

Flow:

    MQTT
       ↓
    ESP32
       ↓
    Validate command
       ↓
    Validate actuator
       ↓
    Perform safety checks
       ↓
    Execute or reject

---

# 30. Local Safety Authority

The ESP32 is the final authority for immediate hardware safety.

Example:

    Cloud:
        Pump ON

    ESP32:
        Water level LOW

Result:

    Pump remains OFF

The ESP32 publishes:

    BLOCKED

or:

    SAFETY_SHUTDOWN

The cloud must never be able to bypass this local safety decision.

---

# 31. Actuator Execution

If the command passes safety checks:

    Command
       ↓
    ESP32
       ↓
    Hardware driver
       ↓
    GPIO / control interface
       ↓
    Relay / MOSFET / driver
       ↓
    Pump / Valve

The API must never directly control GPIO.

---

# 32. Command Result Flow

After execution:

    Actuator
       ↓
    ESP32
       ↓
    Command result
       ↓
    MQTT
       ↓
    Backend
       ↓
    PostgreSQL
       ↓
    WebSocket
       ↓
    Frontend

Example:

    User:
        Pump ON

    Dashboard:
        Command pending...

    ESP32:
        Pump ON

    Backend:
        EXECUTED

    Dashboard:
        Pump ON

---

# 33. Requested State vs Actual State

The system must distinguish:

    Requested State

from:

    Actual State

Example:

    Requested:
        Pump ON

    Actual:
        Pump OFF

This can happen because:

- Safety condition
- Hardware failure
- Communication failure
- Power failure
- Actuator fault

The dashboard should display actual state whenever available.

---

# 34. Command Failure

Example:

    Frontend
       ↓
    Backend
       ↓
    MQTT
       ↓
    ESP32
       ↓
    Safety check
       ↓
    BLOCKED

The result flows back:

    ESP32
       ↓
    MQTT
       ↓
    Backend
       ↓
    WebSocket
       ↓
    Frontend

The UI should explain the reason.

Example:

    Pump OFF
    Command blocked: LOW WATER

---

# 35. Device Status Flow

The ESP32 periodically publishes status.

Example:

    ESP32
       ↓
    MQTT
       ↓
    Backend
       ↓
    PostgreSQL / Cache
       ↓
    WebSocket
       ↓
    Frontend

Possible states:

    ONLINE
    STALE
    OFFLINE
    ERROR

---

# 36. Heartbeat

The ESP32 should periodically provide a heartbeat/status signal.

Purpose:

- Determine device availability
- Detect communication failure
- Display connection state
- Trigger alerts

The backend records the last known status.

---

# 37. Offline Detection

Example:

    ESP32
       ↓
    No telemetry
       ↓
    Timeout
       ↓
    Backend marks device STALE
       ↓
    Continued timeout
       ↓
    Backend marks device OFFLINE
       ↓
    WebSocket
       ↓
    Dashboard

The exact timeout values are configuration and should not be hard-coded
into the frontend.

---

# 38. Wi-Fi Failure

If the ESP32 loses Wi-Fi:

    ESP32
       X
    Wi-Fi

The ESP32 should:

- Continue local safety logic
- Continue sensor sampling where possible
- Continue actuator safety behavior
- Attempt reconnection

The device must not permanently stop because of network failure.

---

# 39. MQTT Failure

If MQTT becomes unavailable:

    ESP32
       ↓
    Wi-Fi = available
       ↓
    MQTT = unavailable

The ESP32 should:

- Continue local operation
- Continue safety logic
- Retry MQTT connection
- Avoid blocking hardware control on MQTT

---

# 40. Internet Failure

If the internet connection is lost:

    ESP32
       ↓
    Raspberry Pi
       ↓
    Local network

may continue operating.

The Raspberry Pi should optionally buffer telemetry until cloud
connectivity returns.

---

# 41. Offline Buffering

If cloud connectivity is unavailable:

    ESP32
       ↓
    Raspberry Pi
       ↓
    Local Buffer

When connectivity returns:

    Local Buffer
       ↓
    MQTT
       ↓
    Backend
       ↓
    PostgreSQL

Original measurement timestamps must be preserved.

---

# 42. Camera Data Flow

Camera processing is separate from normal sensor telemetry.

Preferred architecture:

    Camera
       ↓
    Raspberry Pi
       ↓
    Image Capture
       ↓
    Local Storage / Processing
       ↓
    Computer Vision
       ↓
    Result
       ↓
    Backend
       ↓
    Dashboard

Large image files should not normally be sent through MQTT.

---

# 43. Camera Ownership

The Raspberry Pi should manage cameras connected to the edge system.

Possible cameras:

- Raspberry Pi Camera
- USB camera
- ESP32-CAM
- Future cameras

The camera subsystem should remain independent of the sensor telemetry
pipeline.

---

# 44. Computer Vision Data Flow

Future architecture:

    Camera
       ↓
    Raspberry Pi
       ↓
    Image
       ↓
    CV Pipeline
       ↓
    AI Model
       ↓
    Detection Result
       ↓
    Backend
       ↓
    Database
       ↓
    Dashboard

Possible results:

    Plant detected
    Plant area
    Leaf area
    Leaf color
    Growth estimate
    Disease/anomaly detection
    Confidence score

The CV subsystem must not be required for basic sensor monitoring.

---

# 45. ESP32-CAM

If an ESP32-CAM is used:

    ESP32-CAM
       ↓
    Wi-Fi
       ↓
    Raspberry Pi
       ↓
    Camera Pipeline

It should be treated as a separate device from the primary ESP32
controller unless the architecture explicitly combines their roles.

---

# 46. TFT Display Data Flow

The TFT display is a local user interface.

Preferred flow:

    ESP32
       ↓
    Local device state
       ↓
    TFT Display

The display should not require cloud connectivity for basic local
information.

Possible display values:

    Temperature
    Humidity
    pH
    TDS
    Pump state
    Water level
    Device status

---

# 47. Buzzer Data Flow

The buzzer is a local alert mechanism.

Example:

    ESP32
       ↓
    Safety condition
       ↓
    Buzzer

The buzzer should be capable of operating without cloud connectivity.

Examples:

    Low water
    Pump fault
    Sensor fault
    Critical temperature
    Other safety conditions

---

# 48. Local vs Cloud Responsibilities

## ESP32

Owns:

- Sensor reading
- Actuator control
- Immediate safety
- Local display
- Local buzzer
- Device state

## Raspberry Pi

Owns:

- Edge gateway
- Camera
- Computer vision
- Local buffering
- Network gateway
- Edge processing

## Backend

Owns:

- Authentication
- Authorization
- Persistence
- Business logic
- API
- MQTT cloud integration
- Alerts
- Command lifecycle

## Frontend

Owns:

- Visualization
- User interaction
- Dashboard
- Charts
- Controls
- Status presentation

---

# 49. Data Ownership

The system has multiple types of state.

## Physical State

Authoritative source:

    Hardware

Example:

    Actual pump state

---

## Device State

Authoritative source:

    ESP32

Example:

    Device status
    Firmware version
    Local safety state

---

## Historical Application State

Authoritative source:

    PostgreSQL

Example:

    Telemetry history
    Commands
    Alerts

---

## UI State

Authoritative source:

    Frontend

Example:

    Selected chart range
    Open dashboard panel
    Current UI filters

The frontend must not overwrite authoritative hardware state.

---

# 50. Timestamp Rules

Measurements should carry timestamps.

Where possible, the original measurement time should be preserved.

Example:

    Sensor measured:
        10:30:00

    Raspberry Pi received:
        10:30:01

    Backend received:
        10:30:02

The measurement timestamp remains:

    10:30:00

The system may additionally record:

    receivedAt

to measure transport latency.

---

# 51. Message Identity

Telemetry messages should have:

    messageId

Commands should have:

    commandId

These IDs allow the system to:

- Detect duplicates
- Trace messages
- Correlate requests and results
- Debug failures

---

# 52. Data Transformation

Data should be transformed only when necessary.

Preferred:

    Sensor
       ↓
    ESP32 normalized measurement
       ↓
    MQTT
       ↓
    Backend validation
       ↓
    Database
       ↓
    API
       ↓
    Frontend

Do not repeatedly transform units between layers.

Example:

    Temperature = Celsius

should remain Celsius throughout the system unless the frontend
explicitly requests another presentation format.

---

# 53. Units

Every physical measurement must define its unit.

Examples:

    Temperature:
        C

    Humidity:
        %

    pH:
        pH

    TDS:
        ppm

    Flow:
        L/min

    Water volume:
        L

The exact metric and unit conventions are defined in:

    docs/protocols/TELEMETRY.md

---

# 54. Invalid Data Flow

Invalid sensor data must not be treated as valid measurements.

Example:

    Sensor
       ↓
    Invalid reading
       ↓
    ESP32 validation
       ↓
    Sensor error state

The system may publish a sensor health/error event rather than
persisting the invalid value as normal telemetry.

---

# 55. Sensor Disconnect

Example:

    DHT11 disconnected
       ↓
    ESP32 detects failure
       ↓
    Sensor status = ERROR
       ↓
    MQTT event/status
       ↓
    Backend
       ↓
    Alert
       ↓
    Dashboard

The system should distinguish:

    Sensor failure

from:

    Device offline

---

# 56. Actuator Failure

Example:

    Backend:
        Pump ON

    ESP32:
        Command accepted

    Hardware:
        Pump does not operate

The system should eventually detect this using appropriate feedback,
such as:

- Flow sensor
- Current sensor
- Pressure sensor
- Other actuator feedback

Then:

    Pump command
       ↓
    No expected flow
       ↓
    Fault detection
       ↓
    Safety action
       ↓
    Alert

This is a future enhancement unless the required feedback hardware is
already available.

---

# 57. Flow Control Architecture

Future water-flow control may include:

    Backend
       ↓
    Command
       ↓
    ESP32
       ↓
    Valve / Pump
       ↓
    Flow Sensor
       ↓
    ESP32
       ↓
    Telemetry
       ↓
    Backend

This creates a closed-loop control system.

The ESP32 should perform immediate local control logic where timing is
important.

Cloud automation should operate at a higher level.

---

# 58. Closed-Loop Control

Example:

    Target:
        Flow = 2 L/min

    Flow Sensor:
        1.2 L/min

    ESP32:
        Local control logic

    Valve:
        Adjust

    Flow Sensor:
        2.0 L/min

This is preferable to sending every low-level adjustment through the
cloud.

---

# 59. Automation Architecture

Future automation:

    Sensor telemetry
       ↓
    Backend / Edge Rules
       ↓
    Automation decision
       ↓
    Command
       ↓
    ESP32
       ↓
    Local safety validation
       ↓
    Actuator

Safety constraints remain local.

---

# 60. Cloud Automation Limitation

Cloud automation must not be the only mechanism protecting physical
equipment.

Example:

    Cloud automation:
        Pump OFF

is useful.

But:

    ESP32 safety:
        Pump OFF

must remain available independently.

---

# 61. Failure Containment

A failure in one layer should not unnecessarily cascade through the
entire system.

Example:

    Cloud unavailable

should not automatically cause:

    ESP32 hardware failure

Similarly:

    Camera service unavailable

should not prevent:

    DHT11 telemetry

---

# 62. Component Independence

The following subsystems should be independently restartable:

    ESP32 firmware
    Raspberry Pi gateway
    Camera service
    CV service
    MQTT broker
    Backend
    Database
    Frontend

A camera failure must not bring down the telemetry pipeline.

---

# 63. MVP Data Flow

The first implementation should focus only on:

    DHT11
       ↓
    ESP32
       ↓
    Wi-Fi
       ↓
    Raspberry Pi
       ↓
    MQTT
       ↓
    Backend
       ↓
    PostgreSQL
       ↓
    REST API
       ↓
    Frontend

Then add:

    WebSocket
       ↓
    Live dashboard

Only after this path is operational should additional sensors and
actuators be integrated.

---

# 64. MVP Control Flow

Once telemetry works:

    Frontend
       ↓
    Backend API
       ↓
    MQTT
       ↓
    Raspberry Pi
       ↓
    ESP32
       ↓
    Test actuator
       ↓
    Command result
       ↓
    MQTT
       ↓
    Backend
       ↓
    WebSocket
       ↓
    Frontend

Use a safe test actuator before integrating pumps or valves.

---

# 65. Future Sensor Expansion

Adding a new sensor should require changes primarily in:

    ESP32 firmware
    Sensor configuration
    TELEMETRY.md

The backend and frontend should use generic telemetry structures where
possible.

Example:

    Add pH sensor

should result in:

    pH sensor
       ↓
    ESP32
       ↓
    Existing telemetry pipeline
       ↓
    MQTT
       ↓
    Backend
       ↓
    PostgreSQL
       ↓
    Dashboard

The architecture should not require a completely new communication
system for every sensor.

---

# 66. Future Actuator Expansion

Adding:

    Pump
    Valve
    Buzzer
    Lighting

should use the same command architecture.

Example:

    Frontend
       ↓
    API
       ↓
    Command
       ↓
    MQTT
       ↓
    ESP32
       ↓
    Actuator

Only the actuator type and command parameters should differ.

---

# 67. Future Camera Expansion

Adding another camera should not affect the sensor telemetry path.

Example:

    Camera 1 ──┐
    Camera 2 ──┼──→ Raspberry Pi Camera Pipeline
    Camera 3 ──┘

The camera subsystem remains independent.

---

# 68. Future AI Expansion

AI inference should be modular.

Possible architecture:

    Camera
       ↓
    Image
       ↓
    CV Pipeline
       ↓
    Model
       ↓
    Detection
       ↓
    Result
       ↓
    Backend
       ↓
    Dashboard

Changing the AI model should not require changing:

    ESP32 firmware
    MQTT telemetry protocol
    Core API

---

# 69. Security Boundary

The following boundaries must be maintained:

    Internet
       ↓
    TLS
       ↓
    Backend
       ↓
    AuthZ
       ↓
    MQTT
       ↓
    Raspberry Pi
       ↓
    ESP32
       ↓
    Local Safety
       ↓
    Hardware

The cloud must not be able to bypass device-level safety.

---

# 70. Network Boundary

The intended network architecture is:

    LOCAL NETWORK
    ─────────────────────────

    Raspberry Pi
         │
       Wi-Fi AP
         │
       ESP32

    ─────────────────────────
             │
          WAN/Internet
             │
             ▼
        Cloud Backend

The Raspberry Pi may provide local network connectivity for the ESP32,
eliminating the need for a separate consumer Wi-Fi router.

---

# 71. No Direct Internet Requirement for ESP32

The ESP32 should primarily communicate with the Raspberry Pi.

Preferred:

    ESP32
       ↓
    Local Wi-Fi
       ↓
    Raspberry Pi

rather than:

    ESP32
       ↓
    Internet
       ↓
    Cloud

This reduces exposure and centralizes edge connectivity.

---

# 72. Raspberry Pi as Gateway

The Raspberry Pi acts as the boundary between:

    Local Hardware Network

and:

    Cloud Network

Conceptually:

    LOCAL
       │
       ▼
    Raspberry Pi
       │
       ▼
    CLOUD

This makes the architecture easier to extend with:

- Multiple ESP32 devices
- Multiple cameras
- Offline buffering
- Local AI
- Local dashboards
- Additional edge processing

---

# 73. Multiple ESP32 Devices

The architecture must support future expansion.

Example:

             Raspberry Pi
                  │
        ┌─────────┼─────────┐
        │         │         │
      ESP32-01  ESP32-02  ESP32-03
        │         │         │
      Sensors   Sensors   Sensors

Each device has a unique:

    deviceId

Example:

    esp32-01
    esp32-02
    esp32-03

---

# 74. Multiple Hydroponics Systems

Future deployment may contain multiple systems:

    User
      │
      ├── Hydroponics System A
      │      ├── ESP32-01
      │      └── ESP32-02
      │
      └── Hydroponics System B
             ├── ESP32-03
             └── ESP32-04

The backend must maintain ownership and authorization boundaries.

---

# 75. End-to-End System Flow

The complete monitoring path is:

    ┌──────────────┐
    │    Sensor    │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │    ESP32     │
    │ Acquisition  │
    └──────┬───────┘
           │
         Wi-Fi
           │
           ▼
    ┌──────────────┐
    │ Raspberry Pi │
    │    Gateway   │
    └──────┬───────┘
           │
          MQTT
           │
           ▼
    ┌──────────────┐
    │ MQTT Broker  │
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │   Backend    │
    └──────┬───────┘
           │
      ┌────┴────┐
      │         │
      ▼         ▼
 PostgreSQL   WebSocket
                │
                ▼
          ┌──────────────┐
          │  Dashboard   │
          └──────────────┘

---

# 76. End-to-End Control Flow

The complete control path is:

    ┌──────────────┐
    │  Dashboard   │
    └──────┬───────┘
           │
        HTTPS
           │
           ▼
    ┌──────────────┐
    │   Backend    │
    └──────┬───────┘
           │
          MQTT
           │
           ▼
    ┌──────────────┐
    │ Raspberry Pi │
    └──────┬───────┘
           │
         Wi-Fi
           │
           ▼
    ┌──────────────┐
    │    ESP32     │
    └──────┬───────┘
           │
      Safety Check
           │
           ▼
    ┌──────────────┐
    │   Actuator   │
    └──────┬───────┘
           │
      Actual State
           │
           ▼
        ESP32
           │
          MQTT
           │
           ▼
        Backend
           │
       WebSocket
           │
           ▼
       Dashboard

---

# 77. Complete System Boundary

The final conceptual architecture is:

                         INTERNET
                            │
                            ▼
                  ┌───────────────────┐
                  │   CLOUD PLATFORM  │
                  │                   │
                  │ Frontend          │
                  │ Backend           │
                  │ PostgreSQL        │
                  │ MQTT              │
                  └─────────┬─────────┘
                            │
                         Internet
                            │
                            ▼
                  ┌───────────────────┐
                  │   RASPBERRY PI 5  │
                  │                   │
                  │ Edge Gateway      │
                  │ Camera            │
                  │ Computer Vision   │
                  │ Local Buffer      │
                  └─────────┬─────────┘
                            │
                          Wi-Fi
                            │
                            ▼
                  ┌───────────────────┐
                  │       ESP32       │
                  │                   │
                  │ Sensors           │
                  │ Actuators         │
                  │ Display           │
                  │ Buzzer            │
                  │ Safety            │
                  └─────────┬─────────┘
                            │
                    ┌───────┴───────┐
                    │               │
                 Sensors         Actuators
                    │               │
                    ▼               ▼
                 Physical        Physical
                 Environment     Equipment

---

# 78. Core Design Principles

The implementation must follow these principles.

## Principle 1 — Local Safety

Safety-critical hardware behavior must work without cloud connectivity.

---

## Principle 2 — Edge First

The Raspberry Pi handles edge-specific workloads such as:

- Gateway
- Camera
- Computer vision
- Buffering

---

## Principle 3 — Cloud for Coordination

The cloud handles:

- Persistence
- Authentication
- Authorization
- API
- Dashboard data
- Historical analysis
- Commands
- Alerts

---

## Principle 4 — Hardware Abstraction

The cloud should address:

    pump-01

not:

    GPIO17

---

## Principle 5 — Protocol Separation

The system separates:

    TELEMETRY.md
        ↓
    What data means

    COMMANDS.md
        ↓
    What commands mean

    MQTT.md
        ↓
    How device messages travel

    API.md
        ↓
    How applications communicate

---

## Principle 6 — Failure Isolation

A failure in one subsystem should not unnecessarily disable unrelated
subsystems.

Examples:

    Camera failure
        ≠
    Sensor failure

    Cloud failure
        ≠
    ESP32 safety failure

    Database failure
        ≠
    Local actuator safety failure

---

## Principle 7 — Replaceability

The following should be replaceable without redesigning the entire
system:

- Sensors
- ESP32 firmware implementation
- Raspberry Pi services
- MQTT broker
- Database implementation
- AI model
- Camera
- Frontend framework

The logical interfaces should remain stable.

---

# 79. MVP Scope

The first complete vertical slice is:

    DHT11
       ↓
    ESP32
       ↓
    Wi-Fi
       ↓
    Raspberry Pi
       ↓
    MQTT
       ↓
    Backend
       ↓
    PostgreSQL
       ↓
    REST API
       ↓
    Frontend

Then:

    WebSocket
       ↓
    Real-time dashboard

Only after this works should the following be integrated:

    pH
    TDS
    Flow
    Water level
    Pump
    Valve
    Relay
    TFT
    Buzzer
    Camera
    Computer Vision
    Automation

---

# 80. Definition of Done

The data-flow architecture is considered implemented when:

- ESP32 can acquire sensor data.
- ESP32 can communicate with Raspberry Pi.
- Raspberry Pi can communicate with MQTT.
- Backend can consume MQTT telemetry.
- Backend can validate telemetry.
- Backend can persist telemetry.
- REST API can expose telemetry.
- WebSocket can deliver real-time telemetry.
- Frontend can display current readings.
- Backend can create actuator commands.
- Commands can travel through MQTT.
- ESP32 can validate commands locally.
- ESP32 can execute safe commands.
- ESP32 can report command results.
- Backend can persist command results.
- Frontend can display actual actuator state.
- Hardware safety continues to work without cloud connectivity.

---

# 81. Final System Flow

The fundamental system loop is:

                    MONITORING

    Physical Environment
            ↓
         Sensors
            ↓
          ESP32
            ↓
       Raspberry Pi
            ↓
           MQTT
            ↓
         Backend
            ↓
        PostgreSQL
            ↓
       REST/WebSocket
            ↓
        Dashboard


                    CONTROL

        Dashboard
            ↓
        Backend API
            ↓
           MQTT
            ↓
       Raspberry Pi
            ↓
          ESP32
            ↓
      Local Safety
            ↓
        Actuator
            ↓
      Actual State
            ↓
          ESP32
            ↓
           MQTT
            ↓
         Backend
            ↓
        Dashboard


                    INTELLIGENCE

        Camera
            ↓
       Raspberry Pi
            ↓
       CV Pipeline
            ↓
        AI Model
            ↓
      Vision Result
            ↓
         Backend
            ↓
        Dashboard


The system must always preserve the separation between:

    PHYSICAL HARDWARE
    FIRMWARE
    EDGE
    CLOUD
    APPLICATION

No layer should bypass the responsibilities of another layer without
an explicit architectural decision.
```