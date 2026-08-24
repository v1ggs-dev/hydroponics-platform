```markdown
# Hydroponics Platform — System Architecture

## 1. Purpose

This document defines the high-level system architecture of the
Hydroponics Platform.

The platform is a modular cyber-physical system that combines:

- Embedded hardware
- Sensors
- Actuators
- ESP32 firmware
- Raspberry Pi edge computing
- Wireless networking
- MQTT messaging
- Cloud backend
- PostgreSQL persistence
- REST API
- WebSocket real-time communication
- Web dashboard
- Camera systems
- Computer vision
- Future AI-based plant analysis

The architecture is designed to support an initial MVP while allowing
additional sensors, actuators, cameras, automation, and AI capabilities
to be integrated without redesigning the entire system.

---

# 2. Architectural Goals

The system must provide:

1. Real-time sensor monitoring.
2. Remote actuator control.
3. Local hardware safety.
4. Wireless ESP32-to-edge communication.
5. Cloud-connected monitoring.
6. Historical telemetry storage.
7. Real-time dashboard updates.
8. Modular hardware expansion.
9. Modular software expansion.
10. Offline-tolerant edge operation.
11. Secure remote access.
12. Hardware abstraction.
13. Clear separation of responsibilities.
14. Support for multiple ESP32 devices in the future.
15. Support for computer vision and AI without coupling AI to the
   core telemetry system.

---

# 3. Core Architectural Principle

The system is divided into five major layers:

    Hardware
       ↓
    Firmware
       ↓
    Edge
       ↓
    Cloud
       ↓
    Application

Conceptually:

                    ┌───────────────────────────┐
                    │        APPLICATION        │
                    │                           │
                    │       Web Dashboard       │
                    └────────────┬──────────────┘
                                 │
                          REST / WebSocket
                                 │
                                 ▼
                    ┌───────────────────────────┐
                    │           CLOUD           │
                    │                           │
                    │ Backend                   │
                    │ PostgreSQL                │
                    │ MQTT                     │
                    │ Authentication            │
                    │ Business Logic             │
                    └────────────┬──────────────┘
                                 │
                              Internet
                                 │
                                 ▼
                    ┌───────────────────────────┐
                    │           EDGE            │
                    │                           │
                    │ Raspberry Pi 5            │
                    │ Gateway                   │
                    │ Camera                    │
                    │ Computer Vision           │
                    │ Local Buffer              │
                    └────────────┬──────────────┘
                                 │
                               Wi-Fi
                                 │
                                 ▼
                    ┌───────────────────────────┐
                    │         FIRMWARE          │
                    │                           │
                    │ ESP32                     │
                    │ Sensor Acquisition        │
                    │ Actuator Control          │
                    │ Local Safety              │
                    └────────────┬──────────────┘
                                 │
                                 ▼
                    ┌───────────────────────────┐
                    │         HARDWARE          │
                    │                           │
                    │ Sensors                   │
                    │ Pumps                     │
                    │ Valves                    │
                    │ Relays                    │
                    │ Display                   │
                    │ Buzzer                    │
                    └───────────────────────────┘

---

# 4. System Components

The primary components are:

## Hardware

- DHT11
- pH sensor
- TDS sensor
- Flow sensor
- Water-level sensor
- Temperature sensors
- Pump
- Electrical valve / solenoid valve
- Relay or MOSFET driver
- TFT SPI display
- Buzzer
- Power supplies
- DC/DC converters
- Future sensors and actuators

## Embedded Controller

- ESP32

## Edge Computer

- Raspberry Pi 5

## Camera

Potential options:

- Raspberry Pi Camera
- USB camera
- ESP32-CAM
- Other compatible cameras

## Edge Software

- Gateway
- Camera service
- Computer vision service

## Cloud Software

- Backend API
- MQTT client
- PostgreSQL
- Authentication
- Authorization
- Business logic

## Frontend

- Professional web dashboard
- Charts
- Sensor cards
- Device status
- Actuator controls
- Alerts
- Camera interface
- AI/CV results

---

# 5. ESP32 Responsibilities

The ESP32 is the primary physical hardware controller.

It is responsible for:

- Reading sensors.
- Sampling sensor values.
- Performing basic validation.
- Maintaining device state.
- Controlling actuators.
- Executing local safety rules.
- Driving the TFT display.
- Driving the buzzer.
- Maintaining Wi-Fi connectivity.
- Publishing telemetry.
- Receiving commands.
- Reporting command results.
- Reporting device status.

The ESP32 should remain lightweight and deterministic.

The ESP32 should not be responsible for:

- Database access.
- Web application logic.
- User authentication.
- Complex cloud business logic.
- Large image processing.
- Heavy AI inference.

---

# 6. ESP32 as Local Safety Authority

The ESP32 is the final authority for immediate physical safety.

This is a fundamental architectural rule.

Example:

    Cloud:
        Pump ON

    ESP32:
        Water level = LOW

Result:

    Pump remains OFF.

The cloud cannot bypass this decision.

The same principle applies to:

- Pump protection
- Valve protection
- Dry-run prevention
- Sensor failure
- Temperature limits
- Emergency shutdown
- Other hardware safety conditions

Safety-critical rules must remain executable without internet
connectivity.

---

# 7. Raspberry Pi 5 Responsibilities

The Raspberry Pi 5 is the edge computing layer.

It provides:

- Local network connectivity.
- ESP32 gateway functionality.
- MQTT edge communication.
- Cloud connectivity.
- Local telemetry buffering.
- Camera management.
- Computer vision.
- Edge processing.
- Local system monitoring.
- Future local automation.

The Raspberry Pi should have substantially more responsibility than
the ESP32 for computationally intensive workloads.

---

# 8. Raspberry Pi as Network Gateway

The intended local architecture is:

    Raspberry Pi 5
          │
       Wi-Fi AP
          │
          ▼
        ESP32

The Raspberry Pi may provide the local wireless network, allowing the
system to operate without requiring a third-party consumer router.

The Pi may then use:

- Ethernet
- Wi-Fi
- USB cellular
- Other WAN connectivity

to reach the cloud.

This separates:

    Local hardware network

from:

    Cloud network

---

# 9. Raspberry Pi as Edge Boundary

The Raspberry Pi sits between:

    LOCAL HARDWARE

and:

    CLOUD

Conceptually:

    ESP32
       ↓
    Raspberry Pi
       ↓
    Internet
       ↓
    Cloud

This makes the Pi the natural location for:

- Protocol adaptation
- Buffering
- Camera processing
- Computer vision
- Edge services
- Future local AI

---

# 10. Camera Architecture

Camera processing is independent of the primary sensor telemetry
pipeline.

Preferred:

    Camera
       ↓
    Raspberry Pi
       ↓
    Image Capture
       ↓
    Processing
       ↓
    Computer Vision
       ↓
    Result
       ↓
    Backend
       ↓
    Dashboard

Large images should not normally be transmitted through MQTT.

MQTT may carry:

- Image metadata
- Image ID
- Event notification
- Processing status
- Detection results

Actual image files should use an appropriate HTTP/object-storage
pipeline.

---

# 11. Computer Vision Architecture

Computer vision runs primarily on the Raspberry Pi or another dedicated
compute resource.

Potential flow:

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
    Detection
       ↓
    Backend
       ↓
    Dashboard

Possible future detections:

- Plant presence
- Plant size
- Plant growth
- Leaf area
- Leaf color
- Visual anomalies
- Disease indicators
- Wilting indicators
- Growth trends

The computer vision system must remain modular.

Changing the AI model should not require rewriting the telemetry
system.

---

# 12. Cloud Backend Responsibilities

The backend is the central application authority.

It is responsible for:

- REST API
- WebSocket
- Authentication
- Authorization
- Device management
- Telemetry ingestion
- Telemetry validation
- Telemetry persistence
- Command creation
- Command lifecycle
- MQTT integration
- Alert management
- Dashboard aggregation
- Application business logic
- Audit logging

The backend should not contain hardware-specific GPIO logic.

---

# 13. Backend Does Not Control GPIO

The backend uses logical hardware identifiers.

Correct:

    pump-01
    valve-01
    buzzer-01

Incorrect:

    GPIO17
    GPIO23

The ESP32 firmware owns the mapping between:

    Logical Device

and:

    Physical GPIO / Driver

This keeps the backend independent of hardware revisions.

---

# 14. PostgreSQL Responsibilities

PostgreSQL is the persistent application data store.

Potential data includes:

    Users
    Devices
    Sensors
    Actuators
    Telemetry
    Commands
    Command Results
    Alerts
    Configuration
    Camera Metadata
    Computer Vision Results

PostgreSQL provides historical persistence.

It is not used as the real-time transport mechanism.

---

# 15. MQTT Architecture

MQTT is the device messaging layer.

It transports:

- Telemetry
- Device status
- Commands
- Command results
- Events

The MQTT architecture is defined in:

    docs/protocols/MQTT.md

The message contracts are defined in:

    docs/protocols/TELEMETRY.md
    docs/protocols/COMMANDS.md

---

# 16. REST API Architecture

The REST API provides application-level access to:

- Devices
- Sensors
- Telemetry
- Actuators
- Commands
- Alerts
- Dashboard data

The API specification is defined in:

    docs/protocols/API.md

The frontend communicates with the backend through REST.

The frontend must not communicate directly with MQTT.

---

# 17. WebSocket Architecture

WebSocket provides real-time dashboard updates.

Typical flow:

    ESP32
       ↓
    MQTT
       ↓
    Backend
       ↓
    WebSocket
       ↓
    Frontend

WebSocket events may include:

    telemetry
    device_status
    actuator_state
    command_result
    alert
    event

---

# 18. Frontend Responsibilities

The frontend is responsible for presentation and user interaction.

It provides:

- Dashboard
- Sensor cards
- Live readings
- Historical charts
- Device status
- Actuator controls
- Alerts
- Camera views
- Computer vision results
- Configuration interfaces

The frontend does not own physical state.

The backend remains authoritative for application state.

---

# 19. Frontend Communication

The frontend communicates through:

    REST API

and:

    WebSocket

The frontend must not communicate directly with:

    ESP32
    Raspberry Pi
    MQTT
    PostgreSQL

This creates a clean application boundary.

---

# 20. Primary Telemetry Architecture

Telemetry follows:

    Sensor
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
    REST / WebSocket
       ↓
    Frontend

---

# 21. Primary Control Architecture

Control follows:

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

The resulting physical state returns through:

    Actuator
       ↓
    ESP32
       ↓
    MQTT
       ↓
    Backend
       ↓
    WebSocket
       ↓
    Frontend

---

# 22. Requested State vs Actual State

The system must distinguish between:

    Requested State

and:

    Actual State

Example:

    User requests:
        Pump ON

The API may respond:

    QUEUED

The ESP32 may then determine:

    BLOCKED

because:

    Water level LOW

Therefore:

    Requested:
        ON

    Actual:
        OFF

The dashboard must display actual state when available.

---

# 23. Device Identity

Every physical controller has a unique device ID.

Example:

    esp32-01

Future devices:

    esp32-02
    esp32-03
    esp32-04

The device ID is a logical identity.

It should not depend on GPIO mappings.

---

# 24. Multiple ESP32 Architecture

The platform should support multiple controllers.

Example:

                       Raspberry Pi
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
           ESP32-01      ESP32-02      ESP32-03
              │             │             │
           Sensors       Sensors       Sensors
           Actuators     Actuators     Actuators

Each device uses its own identity and messaging namespace.

---

# 25. Multiple Hydroponics Systems

The architecture should eventually support:

    Organization
       ↓
    Hydroponics System
       ↓
    Raspberry Pi
       ↓
    ESP32 Devices
       ↓
    Sensors / Actuators

Example:

    System A
       ├── ESP32-01
       └── ESP32-02

    System B
       ├── ESP32-03
       └── ESP32-04

The backend must enforce ownership and authorization boundaries.

---

# 26. Data Ownership

Different layers own different types of state.

## Hardware

Owns:

    Physical state

Example:

    Pump physically running.

## ESP32

Owns:

    Local device state
    Safety state
    Actuator execution

## Raspberry Pi

Owns:

    Edge state
    Camera state
    Local buffering

## Backend

Owns:

    Application state
    Authorization
    Historical persistence
    Command lifecycle
    Alerts

## Frontend

Owns:

    UI state

---

# 27. Local Safety vs Cloud Logic

The system intentionally separates:

    SAFETY

from:

    AUTOMATION

Safety belongs close to the hardware.

Automation may occur in:

    Edge
    Cloud

depending on the required latency.

Example:

    Dry-run protection
        → ESP32

    Watering schedule
        → Backend / Edge

    Plant-growth analysis
        → Raspberry Pi / Cloud

---

# 28. Real-Time Requirements

Different operations have different latency requirements.

## Immediate

Examples:

    Emergency stop
    Dry-run protection
    Local actuator protection

Location:

    ESP32

---

## Near Real-Time

Examples:

    Dashboard sensor updates
    Device status
    Actuator state

Location:

    MQTT + Backend + WebSocket

---

## Non-Real-Time

Examples:

    Historical analytics
    Plant growth reports
    AI analysis
    Long-term trends

Location:

    Backend / Database / Edge AI

---

# 29. Failure Isolation

Subsystem failures should be isolated.

Example:

    Cloud unavailable

must not prevent:

    Local sensor acquisition

or:

    Local safety logic

Similarly:

    Camera service failure

must not prevent:

    DHT11 telemetry

And:

    Database failure

must not directly disable:

    ESP32 safety

---

# 30. Offline Operation

The system should degrade gracefully when connectivity is lost.

Example:

    Internet unavailable

The Raspberry Pi can continue:

    Local Wi-Fi
    ESP32 communication
    Sensor collection
    Camera processing
    Local buffering

When connectivity returns:

    Buffered telemetry
        ↓
    Cloud backend

---

# 31. Offline Safety

Offline operation must preserve:

- Sensor acquisition
- Local actuator safety
- Emergency behavior
- Device health
- Local display
- Local buzzer

Cloud connectivity must never be a hard dependency for immediate
physical safety.

---

# 32. Power Architecture

The power architecture is independent from the software architecture.

Typical structure:

    Main Power
        │
        ├── DC/DC Converter
        │       ↓
        │      5V
        │       ↓
        │    Raspberry Pi
        │
        ├── DC/DC Converter
        │       ↓
        │      5V / 3.3V
        │       ↓
        │      ESP32
        │
        └── Actuator Supply
                ↓
          Relay / MOSFET
                ↓
          Pump / Valve

Exact voltage, current, grounding, protection, and wiring requirements
are defined separately in:

    docs/hardware/HARDWARE.md
    docs/hardware/POWER.md
    docs/hardware/WIRING.md

---

# 33. Hardware Abstraction

The architecture must use logical identifiers.

Examples:

    dht11-01
    ph-01
    tds-01
    pump-01
    valve-01
    buzzer-01

The software should not assume that these devices will always use the
same physical GPIO.

Hardware mappings belong to the firmware/hardware configuration layer.

---

# 34. Sensor Expansion

New sensors should follow the existing telemetry architecture.

Example:

    Add pH sensor

Result:

    pH Sensor
       ↓
    ESP32
       ↓
    Existing Telemetry Pipeline
       ↓
    MQTT
       ↓
    Backend
       ↓
    PostgreSQL
       ↓
    API
       ↓
    Dashboard

A new sensor should not require a new transport protocol.

---

# 35. Actuator Expansion

New actuators should use the same command architecture.

Example:

    Add valve

Result:

    Dashboard
       ↓
    API
       ↓
    Command
       ↓
    MQTT
       ↓
    ESP32
       ↓
    Valve

The actuator type and parameters change, but the communication
architecture remains the same.

---

# 36. Camera Expansion

Multiple cameras should be supported without changing the telemetry
architecture.

Example:

    Camera 1 ──┐
    Camera 2 ──┼──→ Raspberry Pi Camera Service
    Camera 3 ──┘

The camera subsystem remains modular.

---

# 37. AI Expansion

AI functionality must remain modular.

Possible architecture:

    Camera
       ↓
    Image
       ↓
    CV Pipeline
       ↓
    AI Model
       ↓
    Analysis
       ↓
    Backend
       ↓
    Dashboard

The AI model can be replaced independently.

The core telemetry and actuator systems must not depend on AI.

---

# 38. Software Repository Boundaries

The repository is organized into:

    backend/
        Cloud application

    frontend/
        Web dashboard

    firmware/esp32/
        Embedded firmware

    edge/gateway/
        Raspberry Pi gateway

    edge/camera/
        Camera services

    edge/cv/
        Computer vision

    infrastructure/
        Deployment infrastructure

    tests/
        Testing

    docs/
        System documentation

---

# 39. Documentation Boundaries

The system documentation is divided into:

    docs/architecture/
        System-level architecture

    docs/hardware/
        Physical hardware

    docs/protocols/
        Communication contracts

    docs/operations/
        Deployment and troubleshooting

    docs/testing/
        Verification strategy

Important protocol documents:

    API.md
    MQTT.md
    TELEMETRY.md
    COMMANDS.md

---

# 40. Protocol Separation

Each protocol document has one responsibility.

## TELEMETRY.md

Defines:

    What sensor data looks like.

## COMMANDS.md

Defines:

    What commands look like.

## MQTT.md

Defines:

    How device messages travel.

## API.md

Defines:

    How the web application communicates with the backend.

These documents must remain consistent.

---

# 41. Security Architecture

The security boundary is:

    Internet
       ↓
    TLS
       ↓
    Backend
       ↓
    Authentication
       ↓
    Authorization
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

The frontend is not trusted to enforce authorization.

The ESP32 is not trusted with cloud-wide credentials.

Device credentials should eventually be unique per device.

---

# 42. Cloud Security

The backend should enforce:

- Authentication
- Authorization
- Device ownership
- Input validation
- Rate limiting
- Audit logging
- Secure secrets
- TLS
- MQTT authentication

Sensitive credentials must never be committed to Git.

---

# 43. Device Security

ESP32 devices should eventually have:

- Unique device identity
- Unique credentials
- Authenticated MQTT
- Secure configuration
- Firmware version tracking

Production devices should not use shared credentials wherever
practical.

---

# 44. API Security

The frontend communicates with:

    HTTPS

The backend verifies:

    User identity
    Device authorization
    Command authorization

The API must not trust:

    deviceId

from the client without validating ownership/access.

---

# 45. MQTT Security

MQTT should use:

    Authentication
    Authorization
    TLS in production

Topic-level access should be restricted.

For example:

    ESP32-01

should not publish:

    hydroponics/esp32-02/telemetry

or receive:

    hydroponics/esp32-02/commands

---

# 46. Observability

The platform should eventually provide visibility into:

    ESP32 health
    Raspberry Pi health
    MQTT health
    Backend health
    Database health
    WebSocket health
    Telemetry ingestion
    Command execution

Useful metrics include:

    Last device heartbeat
    Last telemetry timestamp
    MQTT connection state
    Command success rate
    API latency
    WebSocket connection count

---

# 47. Logging

Each major layer should provide structured logs.

ESP32:

    Connection
    Sensor errors
    Actuator errors
    Safety events

Raspberry Pi:

    Gateway events
    MQTT connection
    Camera errors
    CV errors

Backend:

    API requests
    MQTT events
    Commands
    Authorization
    Errors

Frontend:

    Client-side errors
    WebSocket state
    API failures

Secrets must never be logged.

---

# 48. End-to-End Traceability

Important operations should be traceable.

Example:

    User action
       ↓
    requestId
       ↓
    commandId
       ↓
    MQTT message
       ↓
    ESP32 execution
       ↓
    command result
       ↓
    Backend
       ↓
    WebSocket
       ↓
    Dashboard

This makes debugging and auditing possible.

---

# 49. Development Architecture

During development, the system may run as:

    Windows PC
       │
       ├── Backend
       ├── Frontend
       ├── PostgreSQL
       └── MQTT Broker
       
    Raspberry Pi
       │
       └── Edge Gateway

    ESP32
       │
       └── Firmware

The Windows development environment does not need to emulate the
physical ESP32.

---

# 50. Production Architecture

The production deployment may become:

                    INTERNET
                       │
                       ▼
              ┌─────────────────┐
              │ Reverse Proxy   │
              └────────┬────────┘
                       │
              ┌────────┴────────┐
              │                 │
              ▼                 ▼
          Frontend           Backend
                                │
                    ┌───────────┼───────────┐
                    │           │           │
                    ▼           ▼           ▼
                PostgreSQL     MQTT       Storage
                                │
                                ▼
                         Raspberry Pi
                                │
                              Wi-Fi
                                │
                                ▼
                              ESP32

The exact deployment infrastructure may change.

---

# 51. Scalability

The initial MVP may contain:

    1 Raspberry Pi
    1 ESP32
    1 Hydroponics System

The architecture should eventually support:

    Multiple Raspberry Pis
    Multiple ESP32 devices
    Multiple hydroponics systems
    Multiple users
    Multiple cameras
    Multiple AI workloads

Scalability should be achieved through logical device identity and
protocol consistency rather than rewriting the application for every
new device.

---

# 52. Replaceability

The following components should be replaceable:

    DHT11
       ↓
    Better temperature sensor

    ESP32
       ↓
    Future microcontroller

    MQTT broker
       ↓
    Alternative MQTT implementation

    PostgreSQL
       ↓
    Future database architecture

    Camera
       ↓
    Alternative camera

    AI model
       ↓
    New AI model

The interfaces should remain stable.

---

# 53. Design Rule — No Tight Coupling

Avoid architectures such as:

    Frontend
       ↓
    ESP32-specific API

or:

    Backend
       ↓
    GPIO-specific implementation

or:

    Dashboard
       ↓
    MQTT topic hard-coded into UI

Instead:

    Frontend
       ↓
    API
       ↓
    Logical Device
       ↓
    Backend
       ↓
    MQTT
       ↓
    Device

---

# 54. Design Rule — Local First for Physical Actions

Any operation that can damage hardware or plants must have local
protection.

Examples:

    Pump
    Valve
    Heater
    Nutrient dosing
    Lighting

The cloud can request an operation.

The device determines whether the operation is safe.

---

# 55. Design Rule — Cloud Is Not a Safety Dependency

The system must remain safe when:

    Internet = OFFLINE

    Backend = OFFLINE

    MQTT = OFFLINE

    Database = OFFLINE

Local hardware safety must continue.

---

# 56. Design Rule — Camera Is Optional

The core monitoring system must work without:

    Camera
    Computer Vision
    AI

Therefore:

    Camera failure
        ≠
    Sensor monitoring failure

---

# 57. Design Rule — AI Is Optional

The core system must work without AI.

AI is an enhancement layer.

The system should first establish:

    Reliable sensor telemetry
    Reliable device state
    Reliable actuator control

Then add:

    Computer Vision
    AI
    Automation
    Predictive analytics

---

# 58. MVP Architecture

The first complete MVP should contain:

    ESP32
       │
       ├── DHT11
       │
       └── Wi-Fi
              │
              ▼
        Raspberry Pi
              │
             MQTT
              │
              ▼
          Backend
              │
        ┌─────┴─────┐
        │           │
        ▼           ▼
    PostgreSQL   WebSocket
                    │
                    ▼
                 Frontend

The first MVP does not require:

    pH
    TDS
    Flow
    Water-level automation
    Complex valves
    Computer Vision
    AI
    Advanced automation

Those are modular extensions.

---

# 59. MVP Success Criteria

The MVP is successful when:

    DHT11
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
    API
       ↓
    Dashboard

works reliably end-to-end.

The dashboard should show:

    Temperature
    Humidity
    Device status
    Last update time

The system should also support:

    Real-time updates
    Historical readings
    Basic device health

---

# 60. Future Architecture

After the MVP:

                    CLOUD
                       │
               ┌───────┴────────┐
               │                │
           Monitoring        Automation
               │                │
               ▼                ▼
           Analytics         Commands
               │                │
               └───────┬────────┘
                       │
                    MQTT
                       │
                       ▼
                RASPBERRY PI
                       │
          ┌────────────┼────────────┐
          │            │            │
       Gateway       Camera        CV
          │            │            │
          ▼            ▼            ▼
        ESP32       Images         AI
          │
     ┌────┴────┐
     │         │
  Sensors   Actuators

---

# 61. Architectural Invariants

The following rules must remain true unless an explicit architecture
decision changes them.

### Invariant 1

The ESP32 handles physical sensor acquisition.

### Invariant 2

The ESP32 handles immediate hardware safety.

### Invariant 3

The Raspberry Pi is the edge computing layer.

### Invariant 4

MQTT is the device messaging transport.

### Invariant 5

The backend is the application authority.

### Invariant 6

PostgreSQL is the persistent application data store.

### Invariant 7

The frontend communicates through API/WebSocket.

### Invariant 8

The frontend does not communicate directly with hardware.

### Invariant 9

The cloud cannot bypass local hardware safety.

### Invariant 10

Camera and AI functionality remain optional modules.

---

# 62. Architecture Summary

The Hydroponics Platform is a layered cyber-physical system.

The fundamental architecture is:

    ┌───────────────────────────────────────┐
    │              FRONTEND                 │
    │       Dashboard / Controls / UI       │
    └──────────────────┬────────────────────┘
                       │
                 REST / WebSocket
                       │
                       ▼
    ┌───────────────────────────────────────┐
    │               BACKEND                  │
    │ API / Auth / Logic / MQTT / Database │
    └──────────────────┬────────────────────┘
                       │
                      MQTT
                       │
                       ▼
    ┌───────────────────────────────────────┐
    │            RASPBERRY PI 5             │
    │ Gateway / Camera / CV / Edge Compute │
    └──────────────────┬────────────────────┘
                       │
                     Wi-Fi
                       │
                       ▼
    ┌───────────────────────────────────────┐
    │                 ESP32                 │
    │ Sensors / Actuators / Local Safety   │
    └──────────────────┬────────────────────┘
                       │
                       ▼
    ┌───────────────────────────────────────┐
    │               HARDWARE                │
    │ Sensors / Pumps / Valves / Display   │
    └───────────────────────────────────────┘

The system is intentionally designed so that:

    Sensors can change.
    Actuators can change.
    ESP32 firmware can evolve.
    Cameras can change.
    AI models can change.
    Backend services can evolve.
    Frontend can evolve.

without requiring a complete architectural rewrite.

The most important boundary is:

    CLOUD
       ↓
    EDGE
       ↓
    DEVICE
       ↓
    PHYSICAL WORLD

Each layer has a clearly defined responsibility, and safety-critical
physical behavior remains local to the device.
```