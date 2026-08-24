# Hydroponics Platform — AI Agent Instructions

## 1. Project Identity

This repository contains a modular hydroponics monitoring, control, automation, and computer-vision platform.

The project is being developed as an MVP first, with a strong emphasis on:

- Modularity
- Reliability
- Hardware safety
- Clear separation of responsibilities
- Replaceable hardware components
- Clean interfaces between subsystems
- Real-time monitoring
- Remote control
- Future extensibility

The current MVP is being developed under a very short timeline. Prefer simple, reliable, testable implementations over unnecessary complexity.

---

# 2. System Architecture

The system consists of four primary execution environments:

1. ESP32
2. Raspberry Pi 5
3. Remote Cloud Server
4. User Web Browser

High-level architecture:

    Physical Sensors / Actuators
              |
              v
           ESP32
              |
              v
        Raspberry Pi 5
              |
              v
          MQTT / HTTPS
              |
              v
        Cloud Backend
              |
        +-----+------+
        |            |
        v            v
    PostgreSQL    WebSocket
                     |
                     v
              Web Dashboard


The Raspberry Pi also handles:

- Camera capture
- Computer vision
- Local processing
- Local automation
- Local buffering
- Cloud synchronization

---

# 3. Primary Data Flows

## 3.1 Telemetry Flow

Sensor readings must follow this general path:

    Sensor
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
    WebSocket / API
      ↓
    Frontend


The frontend must never directly communicate with sensors or the ESP32.

---

## 3.2 Control Flow

Remote actuator commands must follow:

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
    Local Safety Validation
      ↓
    Relay / Driver
      ↓
    Pump / Valve / Other Actuator


The frontend must never directly control GPIO, relays, pumps, valves, or other physical hardware.

---

## 3.3 Computer Vision Flow

The camera pipeline follows:

    Camera
      ↓
    Raspberry Pi
      ↓
    Image Processing
      ↓
    Computer Vision / AI
      ↓
    Plant Observation
      ↓
    Backend
      ↓
    Database
      ↓
    Dashboard


Computer vision must not be required for the basic monitoring and safety functions of the hydroponics system.

If the CV subsystem fails, sensor monitoring and hardware safety must continue operating.

---

# 4. ESP32 Responsibilities

The ESP32 is the primary hardware controller.

The ESP32 is responsible for:

- Reading sensors
- Basic sensor filtering
- Sensor validation
- Sensor calibration logic where appropriate
- Controlling actuators
- Hardware safety logic
- TFT display
- Buzzer
- Watchdog functionality
- Device health reporting
- Communication with the Raspberry Pi

Potential sensors include:

- pH
- EC/TDS
- Ambient temperature
- Humidity
- Water temperature
- Flow
- Water level
- Other future sensors

Potential actuators include:

- Pump
- Valve
- Relay-controlled equipment
- Buzzer
- Other future actuators

The current temporary temperature sensor is a DHT11.

The DHT11 represents:

- `air_temperature`
- `humidity`

Do NOT represent DHT11 as a water-temperature sensor.

A future waterproof temperature sensor should use a separate logical metric:

- `water_temperature`

---

# 5. ESP32 Independence

The ESP32 must not require an internet connection to perform basic hardware operation.

The ESP32 must remain capable of:

- Reading sensors
- Executing local safety rules
- Turning unsafe actuators off
- Maintaining safe startup states
- Operating basic hardware functionality

Cloud connectivity is not a prerequisite for physical safety.

Never implement safety-critical behavior exclusively in the cloud.

---

# 6. Raspberry Pi 5 Responsibilities

The Raspberry Pi 5 is the edge-computing layer.

It is responsible for:

- ESP32 communication
- Telemetry forwarding
- Command forwarding
- MQTT communication
- Camera capture
- Computer vision
- Local automation
- Local telemetry buffering
- Cloud synchronization
- Edge health monitoring

The Raspberry Pi should not directly expose raw hardware implementation details to the cloud.

For example, cloud services should use:

    pump-01

rather than:

    GPIO17

GPIO numbers belong to the hardware/firmware layer.

---

# 7. Raspberry Pi Offline Operation

The Raspberry Pi should be capable of continuing basic operation if the cloud becomes unavailable.

When the internet is unavailable:

    ESP32
       ↕
    Raspberry Pi

should continue functioning.

The Raspberry Pi may buffer telemetry locally and synchronize it with the cloud once connectivity is restored.

Do not implement complex distributed systems for the MVP.

Prefer a simple, reliable local buffer.

---

# 8. Backend Responsibilities

The cloud backend is responsible for:

- Authentication
- Authorization
- Device management
- Sensor management
- Telemetry ingestion
- Telemetry validation
- Historical data access
- Actuator commands
- Command tracking
- Alerts
- Device health
- WebSocket updates
- Persistence
- API endpoints

The backend must NOT directly manipulate:

- GPIO
- ESP32 pins
- Raspberry Pi hardware
- Relays
- Pumps
- Valves

The backend communicates with edge devices through defined protocols.

---

# 9. Frontend Responsibilities

The frontend is responsible for:

- Dashboard UI
- Sensor visualization
- Historical charts
- Device status
- Actuator controls
- Alerts
- Camera results
- Computer-vision results
- User interaction

The frontend communicates with the backend only.

The frontend must NOT directly communicate with:

- ESP32
- Raspberry Pi
- GPIO
- Sensors
- Relays
- Pumps
- Valves
- Cameras

---

# 10. Hardware Abstraction

Hardware implementation details must remain inside the hardware layer.

Never expose GPIO numbers outside the ESP32 firmware unless explicitly required for hardware documentation.

Use logical identifiers such as:

    esp32-01
    dht11-01
    ph-01
    ec-01
    flow-01
    level-01
    pump-01
    valve-01

Do not hard-code assumptions about the current hardware BOM throughout the application.

The hardware list is expected to change.

---

# 11. Modularity Requirements

Every major hardware component should be replaceable without requiring a complete system redesign.

Examples:

DHT11 → Waterproof temperature sensor

One pH module → Another pH module

One EC/TDS module → Another EC sensor

One relay → Another relay driver

One camera → Another compatible camera

The software architecture should depend on logical interfaces rather than specific hardware whenever practical.

---

# 12. Sensor Architecture

Sensors should expose normalized measurements.

A measurement should conceptually contain:

    sensorId
    metric
    value
    unit
    quality
    timestamp

Example:

    {
      "sensorId": "dht11-01",
      "metric": "air_temperature",
      "value": 27.4,
      "unit": "C",
      "quality": "GOOD",
      "timestamp": "..."
    }

Do not create separate application architectures for every sensor.

Prefer a common telemetry model.

---

# 13. Actuator Architecture

Actuators should be represented logically.

Example:

    {
      "actuatorId": "pump-01",
      "type": "pump",
      "state": "ON"
    }

The backend should not know how the actuator is physically implemented.

The ESP32 is responsible for translating logical actuator commands into physical GPIO/driver behavior.

---

# 14. Command Architecture

Commands should use logical identifiers.

Example:

    {
      "commandId": "cmd-123",
      "deviceId": "esp32-01",
      "actuatorId": "pump-01",
      "action": "SET_STATE",
      "value": "ON"
    }

A remote command is a REQUEST, not proof that the actuator changed state.

The actual hardware state must be reported by the device.

Do not make the frontend assume:

    user clicked ON → pump is ON

Instead:

    user clicked ON
        ↓
    command sent
        ↓
    ESP32 validates
        ↓
    actuator changes state
        ↓
    ESP32 reports actual state
        ↓
    backend persists state
        ↓
    frontend displays actual state

---

# 15. Safety Requirements

Safety logic is a high priority.

At minimum, the system should support safety conditions such as:

    Critical low water level
        ↓
    Pump OFF

and:

    Pump ON
    +
    No detected flow
    +
    timeout
        ↓
    Pump OFF
    ↓
    Fault / Alert

Safety-critical behavior must execute locally whenever possible.

Never rely exclusively on:

    Browser
    ↓
    Cloud
    ↓
    Internet

for physical safety.

---

# 16. Safe Startup

After ESP32 startup or reset:

- Pump must default to a safe state.
- Valves must default to a defined safe state.
- Buzzer must not remain active unexpectedly.
- Safety checks must initialize before enabling actuators.

Do not assume the previous actuator state is safe.

---

# 17. Communication Rules

Communication between subsystems must use explicit contracts.

Do not silently invent new message formats.

Primary communication model:

    ESP32 ↔ Raspberry Pi
    Raspberry Pi ↔ MQTT
    Backend ↔ MQTT
    Frontend ↔ Backend API/WebSocket

Communication schemas must be documented.

If a schema needs to change:

1. Identify all consumers.
2. Update the relevant protocol documentation.
3. Update all affected implementations.
4. Test the complete data path.

---

# 18. MQTT Rules

MQTT topics must use a consistent hierarchy.

Preferred initial structure:

    hydroponics/{deviceId}/telemetry
    hydroponics/{deviceId}/status
    hydroponics/{deviceId}/commands
    hydroponics/{deviceId}/events

Do not create arbitrary topic names without checking the existing MQTT specification.

MQTT message formats must be documented.

---

# 19. API Rules

The frontend must consume stable backend APIs.

Examples:

    GET  /api/devices
    GET  /api/devices/:id
    GET  /api/measurements/latest
    GET  /api/measurements/history
    POST /api/commands
    GET  /api/alerts

These are examples, not immutable requirements.

Use the existing API documentation as the source of truth once established.

---

# 20. Database Rules

Use a generalized measurement model.

Prefer:

    measurements

over separate tables such as:

    ph_readings
    tds_readings
    temperature_readings
    flow_readings

unless there is a demonstrated technical reason for a specialized schema.

The system must support adding new sensor types without requiring major database redesign.

Store:

- Device identity
- Sensor identity
- Metric
- Value
- Unit
- Quality
- Timestamp

where appropriate.

---

# 21. Frontend Data Rules

The frontend should not invent or transform authoritative sensor state.

The backend is the source of truth for:

- Device state
- Actuator state
- Historical measurements
- Alerts
- Command status

The frontend may perform presentation-level transformations such as:

- Formatting
- Unit display
- Chart formatting
- Human-readable labels

---

# 22. Time and Timestamps

Use UTC internally for timestamps.

Prefer ISO 8601 timestamps.

Example:

    2026-08-14T10:30:00Z

Convert to local time only at the presentation layer.

Do not rely on the local timezone of an ESP32, Raspberry Pi, or browser for authoritative timestamps.

---

# 23. Configuration

Configuration must not be hard-coded into source code when it is expected to vary by environment.

Use:

- Environment variables
- Configuration files
- Platform-specific configuration

Examples:

    MQTT_HOST
    MQTT_PORT
    MQTT_USERNAME
    MQTT_PASSWORD
    DATABASE_URL
    API_URL

Never hard-code secrets.

---

# 24. Secrets

NEVER commit:

- Passwords
- API keys
- Private keys
- MQTT credentials
- Database credentials
- Cloud credentials
- Access tokens
- `.env` files containing real secrets

Use:

    .env.example

for documenting required variables.

If a secret is accidentally exposed, immediately report it rather than ignoring it.

---

# 25. Dependency Rules

Do not add a new dependency simply because it is convenient.

Before adding a dependency:

1. Check whether an existing dependency already provides the functionality.
2. Check whether the standard library is sufficient.
3. Check compatibility with the target environment.
4. Check maintenance/security considerations.
5. Keep the dependency justified.

Do not introduce major frameworks or infrastructure without explicit justification.

---

# 26. Technology Direction

Current intended technology direction:

## Firmware

- ESP32
- C/C++
- PlatformIO

## Edge

- Raspberry Pi 5
- Python
- MQTT
- OpenCV / appropriate CV libraries

## Backend

- Node.js
- TypeScript
- NestJS or an equivalent modular TypeScript backend
- PostgreSQL
- MQTT
- WebSocket

## Frontend

- Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui
- ECharts

These technologies are the current direction, not permission to introduce unnecessary alternatives.

If a different technology is genuinely required, explain why before replacing an established choice.

---

# 27. Development Environment

Primary development machine:

    Windows

Primary development IDE:

    Google Antigravity

Target environments:

    Windows
    Raspberry Pi 5
    ESP32
    Linux cloud server

Do not assume the developer is working from Linux.

Development instructions must work from Windows where practical.

---

# 28. Repository Structure

The repository follows this general structure:

    /
    ├── AGENTS.md
    ├── ARCHITECTURE.md
    ├── DEVELOPMENT.md
    ├── README.md
    ├── STATUS.md
    │
    ├── firmware/
    │   └── esp32/
    │
    ├── edge/
    │   ├── gateway/
    │   ├── camera/
    │   └── cv/
    │
    ├── backend/
    ├── frontend/
    ├── infrastructure/
    │
    ├── docs/
    │   ├── hardware/
    │   ├── protocols/
    │   ├── api/
    │   └── deployment/
    │
    └── tests/

Keep responsibilities separated.

Do not move code between these areas without a clear architectural reason.

---

# 29. Agent Workflow

Before making changes:

1. Read this file.
2. Read `ARCHITECTURE.md`.
3. Read relevant documentation under `docs/`.
4. Inspect the existing implementation.
5. Determine the smallest set of files that need modification.
6. Implement the change.
7. Run relevant tests/builds.
8. Review the resulting diff.
9. Report what changed and any remaining issues.

Do not blindly rewrite existing code.

---

# 30. Scope Control

The current objective is a functional MVP.

Prioritize:

1. Sensor acquisition
2. ESP32 firmware
3. Actuator control
4. ESP32 ↔ Raspberry Pi communication
5. Raspberry Pi gateway
6. MQTT
7. Backend telemetry ingestion
8. PostgreSQL
9. Dashboard
10. Real-time updates
11. Remote actuator commands
12. Basic safety
13. Camera
14. Basic computer vision

Do not prioritize advanced features over a working core system.

---

# 31. Avoid Overengineering

Do NOT introduce:

- Kubernetes
- Microservices unless clearly necessary
- Complex event-sourcing
- Distributed consensus systems
- Complex service meshes
- Excessive abstraction layers
- Multiple databases without justification
- Complex message brokers beyond project requirements
- Premature optimization

The MVP should remain understandable and maintainable.

Prefer:

    simple + modular + reliable

over:

    complex + theoretically scalable + unfinished

---

# 32. Changes Must Be Incremental

Prefer small, isolated changes.

For example:

Good:

    Add DHT11 sensor support.

Then:

    Add telemetry serialization.

Then:

    Add Raspberry Pi ingestion.

Bad:

    Rewrite the entire firmware architecture,
    backend, frontend and gateway simultaneously.

Do not modify unrelated modules unless required.

---

# 33. Hardware Changes

Never assume a hardware component based only on its generic name.

For example:

"DHT11" may refer to different physical module configurations.

Before generating wiring instructions or GPIO assignments:

- Check the exact module.
- Check the existing hardware documentation.
- Ask for clarification if electrical details are uncertain.

Never guess electrical connections when incorrect wiring could damage hardware.

---

# 34. Electrical Safety

Never assume a GPIO pin can directly drive:

- Pumps
- Motors
- Solenoid valves
- High-current loads
- Mains equipment

Use appropriate:

- Relay modules
- MOSFET drivers
- Transistors
- Flyback protection
- External power supplies
- Isolation where required

The ESP32 GPIO must not directly power high-current loads.

When voltage/current information is unknown, stop and request the relevant specifications before generating wiring instructions.

---

# 35. Testing Philosophy

Testing must happen at multiple levels.

## Firmware

Test:

- Sensor reading
- Validation
- Filtering
- Safety
- Communication formatting

## Edge

Test:

- Serial communication
- Message parsing
- MQTT
- Buffering
- Camera capture

## Backend

Test:

- API
- MQTT ingestion
- Validation
- Database persistence
- Commands
- Authorization

## Frontend

Test:

- Rendering
- API integration
- WebSocket updates
- Control interactions
- Error states

## Integration

Test complete flows:

    Sensor
    → ESP32
    → Pi
    → Cloud
    → Database
    → Dashboard

and:

    Dashboard
    → Cloud
    → Pi
    → ESP32
    → Actuator

---

# 36. Do Not Claim Hardware Success Without Verification

A successful compilation does NOT mean hardware functionality is verified.

A successful unit test does NOT mean physical hardware is verified.

Clearly distinguish:

    Code implemented

    Build successful

    Software test successful

    Hardware tested

    End-to-end integration tested

Never claim physical functionality without evidence.

---

# 37. Error Handling

Errors must be explicit.

Examples:

- Sensor disconnected
- Sensor out of range
- Invalid telemetry
- Device offline
- MQTT unavailable
- Database unavailable
- Camera unavailable
- Actuator failure
- Flow failure

Do not silently swallow important errors.

Use structured logging where appropriate.

---

# 38. Logging

Logs should provide enough information to diagnose failures.

Prefer structured messages containing:

- Timestamp
- Device ID
- Component
- Event
- Severity
- Error information

Avoid logging secrets or sensitive credentials.

---

# 39. AI / Computer Vision

Computer vision is an enhancement layer.

The core hydroponics monitoring system must not depend on AI.

The initial CV implementation should prioritize simple measurable observations such as:

- Plant presence
- Plant area
- Leaf/plant segmentation
- Color statistics
- Visual anomaly indicators

Do not claim medical/agricultural disease diagnosis without validated models and appropriate evidence.

AI/CV failures must not stop basic monitoring or safety.

---

# 40. MVP Time Constraint

The MVP is intended to be completed in approximately 4–5 days.

When forced to choose:

    working core feature

takes priority over:

    advanced feature

Cut features in this order if necessary:

1. Advanced AI
2. Advanced analytics
3. Advanced automation
4. Camera enhancements
5. Additional nonessential sensors
6. UI polish

Do NOT sacrifice:

- Sensor acquisition
- Hardware safety
- Core telemetry
- Backend
- Database
- Dashboard
- Basic actuator control

---

# 41. Git Safety

Never execute destructive Git commands without explicit approval.

Do NOT automatically execute:

    git reset --hard
    git clean -fd
    git push --force

Do not overwrite uncommitted user changes.

Before potentially destructive operations:

1. Inspect `git status`.
2. Report the risk.
3. Ask for approval.

Prefer small commits.

---

# 42. File Safety

Do not delete files merely because they appear unused.

Before deleting or replacing files:

1. Search for references.
2. Determine whether they are part of the current architecture.
3. Confirm the change is safe.

Do not modify generated files unnecessarily.

---

# 43. Agent Communication

When completing a task, report:

## Changed

List important files changed.

## Implemented

Summarize functionality.

## Tested

List commands/tests/builds performed.

## Not Tested

Clearly state hardware or integration tests that could not be performed.

## Issues

List remaining problems.

## Next Recommended Step

Provide the smallest logical next step.

Do not claim completion if important tests are still failing.

---

# 44. Current Development Strategy

The project should be developed using vertical slices.

Example:

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
    Dashboard

Once the first vertical slice works, add the next sensor.

Do not build every subsystem independently and postpone integration until the end.

---

# 45. Current First Milestone

The current immediate milestone is:

    DHT11
      ↓
    ESP32
      ↓
    USB Serial
      ↓
    Windows

The DHT11 should produce:

- `air_temperature`
- `humidity`

The first implementation should NOT involve:

- Raspberry Pi
- MQTT
- Cloud
- Backend
- PostgreSQL
- Frontend
- Camera
- AI

Only after the DHT11 → ESP32 → Serial path is verified should the next integration stage begin.

---

# 46. Source of Truth

When making architectural decisions, use the following order:

1. Explicit user requirements
2. `AGENTS.md`
3. `ARCHITECTURE.md`
4. Hardware documentation
5. Protocol documentation
6. API documentation
7. Existing implementation
8. Agent preference

Agent preference must never override an explicit project requirement.

When requirements conflict or are ambiguous, do not silently choose a potentially destructive interpretation. Explain the conflict and ask for clarification when necessary.

---

# 47. Final Principle

Build the system as a collection of replaceable modules with explicit contracts.

The fundamental architecture is:

    SENSE
      ↓
    PROCESS
      ↓
    TRANSPORT
      ↓
    STORE
      ↓
    VISUALIZE
      ↓
    DECIDE
      ↓
    CONTROL
      ↓
    VERIFY

Every implementation decision should preserve this separation.

The goal is not merely to make the MVP work.

The goal is to make the MVP a clean foundation that can later evolve into a production-grade hydroponics platform without requiring a complete rewrite.