# Hydroponics Platform — Development Guide

## 1. Purpose

This document defines the development workflow, coding standards,
testing strategy, Git workflow, environment conventions, and deployment
practices for the Hydroponics Platform.

This project is being developed as a modular MVP first, with a target
development window of approximately 4–5 days.

The primary objective is to establish a working end-to-end system
without sacrificing the architectural boundaries required for future
expansion.

---

# 2. Development Philosophy

The project should be developed using:

- Small incremental changes
- Vertical integration
- Clear module boundaries
- Explicit interfaces
- Hardware abstraction
- Testable components
- Frequent builds
- Frequent commits
- Early physical testing
- Minimal unnecessary infrastructure

Prefer:

    Simple + reliable + modular

over:

    Complex + theoretically scalable + unfinished

---

# 3. Development Environment

## Primary Development Machine

Operating System:

    Windows

Primary IDE:

    Google Antigravity

Primary shell:

    PowerShell

---

# 4. Development Toolchain

Expected development tools:

- Google Antigravity
- Git
- GitHub
- Node.js LTS
- npm
- Python 3
- PlatformIO
- Docker Desktop
- SSH

Optional tools may be added when justified.

WSL2 is optional and must not become a mandatory dependency unless
there is a clear requirement.

---

# 5. Target Environments

The project has three primary runtime targets.

## 5.1 ESP32

Runtime:

    ESP32 microcontroller

Development:

    Windows + PlatformIO

Deployment:

    USB flashing during development
    OTA may be added later

---

## 5.2 Raspberry Pi 5

Runtime:

    Raspberry Pi OS / compatible Linux ARM64 environment

Responsibilities:

- Edge gateway
- Local networking
- MQTT
- Camera
- Computer vision
- Local automation
- Local buffering

---

## 5.3 Cloud

Runtime:

    Linux cloud server

Responsibilities:

- Frontend
- Backend
- PostgreSQL
- MQTT infrastructure

Docker is preferred for reproducible cloud deployment where practical.

---

# 6. Repository Structure

The repository is a monorepo.

Expected structure:

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

Do not move responsibilities between directories without an
architectural reason.

---

# 7. Source of Truth

The following documents define the project:

    AGENTS.md
    ARCHITECTURE.md
    DEVELOPMENT.md
    docs/

Before implementing a significant change:

1. Read the relevant documentation.
2. Inspect the existing implementation.
3. Check whether the change conflicts with an existing contract.
4. Update documentation if the architecture or protocol changes.

Documentation and implementation should remain consistent.

---

# 8. Development Order

The project should be developed in vertical slices.

The preferred order is:

    1. ESP32 hardware
    2. ESP32 telemetry
    3. Raspberry Pi gateway
    4. MQTT
    5. Backend
    6. PostgreSQL
    7. Frontend
    8. Real-time updates
    9. Actuator control
    10. Camera
    11. Computer vision
    12. Advanced automation

Do not build the entire frontend before verifying that real hardware
telemetry can reach the backend.

---

# 9. Current First Milestone

The first milestone is:

    DHT11
      ↓
    ESP32
      ↓
    USB
      ↓
    Windows
      ↓
    Serial Monitor

The DHT11 currently provides:

    air_temperature
    humidity

The DHT11 is NOT a water-temperature sensor.

A future waterproof temperature sensor should provide:

    water_temperature

---

# 10. Vertical Slice Development

A vertical slice means implementing one feature through the complete
system before adding unnecessary additional features.

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

Once this works, add pH.

Then:

    pH
      ↓
    ESP32
      ↓
    Existing telemetry pipeline

The existing architecture should not need to be redesigned for every
new sensor.

---

# 11. ESP32 Development

## Framework

Use:

    PlatformIO

Target:

    ESP32

Language:

    C/C++

---

# 12. ESP32 Firmware Organization

Expected structure:

    firmware/esp32/
    ├── platformio.ini
    └── src/
        ├── main.cpp
        │
        ├── sensors/
        ├── actuators/
        ├── communication/
        ├── safety/
        └── display/

Keep hardware-specific code inside the firmware layer.

---

# 13. ESP32 Development Rules

Firmware should:

- Initialize hardware explicitly
- Validate sensor readings
- Handle sensor failures
- Use safe actuator startup states
- Avoid blocking operations where possible
- Use watchdog functionality where appropriate
- Separate communication from hardware logic
- Keep GPIO mappings centralized
- Report device health
- Use structured telemetry

Avoid:

- Large monolithic `main.cpp`
- Hard-coded cloud logic
- Hard-coded frontend assumptions
- Blocking network operations inside safety-critical logic
- Unexplained magic numbers

---

# 14. ESP32 Hardware Safety

Hardware safety takes precedence over remote control.

The ESP32 should locally enforce rules such as:

    Low water
      ↓
    Pump OFF

and:

    Pump ON
      +
    No flow
      +
    Timeout
      ↓
    Pump OFF
      ↓
    Fault

Remote commands must never bypass local safety validation.

---

# 15. ESP32 Communication

The intended deployment transport is:

    ESP32
      ↓
    Wi-Fi
      ↓
    Raspberry Pi

MQTT is the preferred messaging protocol.

During initial development:

    Windows
      ↓
    USB
      ↓
    ESP32

may be used for:

- Flashing
- Debugging
- Serial logs
- Initial sensor testing

USB development communication does not define the final deployment
architecture.

---

# 16. Raspberry Pi Development

The Raspberry Pi software should primarily use:

    Python

The edge layer should be divided into:

    edge/
    ├── gateway/
    ├── camera/
    └── cv/

---

# 17. Raspberry Pi Gateway

The gateway is responsible for:

- ESP32 communication
- MQTT
- Command forwarding
- Telemetry forwarding
- Device health
- Local buffering
- Cloud synchronization

The gateway should not contain unrelated camera/CV logic.

---

# 18. Raspberry Pi Local Network

The Raspberry Pi should be capable of acting as the local Wi-Fi
access point for the hydroponics installation where practical.

Target architecture:

    Raspberry Pi 5
        │
        ├── Local Wi-Fi AP
        │       │
        │       ▼
        │     ESP32
        │
        └── WAN / Internet
                │
                ▼
              Cloud

The local ESP32 ↔ Raspberry Pi connection must not require a
third-party consumer router.

---

# 19. Raspberry Pi Offline Operation

The Raspberry Pi should continue communicating with the ESP32 when the
cloud is unavailable.

Expected:

    ESP32
      ↕
    Raspberry Pi

The Pi should buffer telemetry locally.

When the cloud becomes available:

    Local Buffer
      ↓
    Backend
      ↓
    PostgreSQL

Do not implement a complex distributed database synchronization system
for the MVP.

---

# 20. Backend Development

Current technology direction:

    Node.js
    TypeScript
    NestJS or equivalent modular TypeScript framework

The backend should be organized by domain.

Conceptual modules:

    auth/
    devices/
    sensors/
    actuators/
    telemetry/
    commands/
    alerts/
    camera/

Do not create a microservice architecture for the MVP.

Use a modular monolith unless there is a demonstrated reason to
separate services.

---

# 21. Backend Responsibilities

The backend should handle:

- Authentication
- Authorization
- Device identity
- Telemetry ingestion
- Validation
- Persistence
- Commands
- Command tracking
- Alerts
- WebSocket updates
- Device health
- Historical data

---

# 22. Frontend Development

Current technology direction:

    Next.js
    TypeScript
    Tailwind CSS
    shadcn/ui
    ECharts

The frontend should be organized by feature.

Example:

    dashboard/
    devices/
    sensors/
    controls/
    alerts/
    camera/
    analytics/

Avoid giant monolithic components.

---

# 23. Frontend Rules

The frontend communicates with:

    Backend API
    WebSocket

The frontend must not communicate directly with:

    ESP32
    Raspberry Pi
    MQTT
    GPIO
    Sensors
    Relays

The frontend displays actual backend/device state rather than assuming
that commands succeeded.

---

# 24. Database Development

Database:

    PostgreSQL

Use migrations.

Do not manually modify production database schemas without a migration.

Prefer generalized measurement storage:

    measurements

with fields such as:

    id
    device_id
    sensor_id
    metric
    value
    unit
    quality
    timestamp

New sensors should normally be represented by new metrics rather than
new database tables.

---

# 25. Telemetry Development

Telemetry must use a documented contract.

Conceptual format:

    {
      "version": 1,
      "deviceId": "esp32-01",
      "type": "telemetry",
      "timestamp": "...",
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

The actual schema must be maintained in:

    docs/protocols/TELEMETRY.md

Do not silently change telemetry fields.

---

# 26. Command Development

Commands must be explicit.

Conceptual format:

    {
      "version": 1,
      "commandId": "cmd-123",
      "deviceId": "esp32-01",
      "actuatorId": "pump-01",
      "action": "SET_STATE",
      "value": "ON"
    }

Command success must be distinguished from actual hardware state.

---

# 27. MQTT Development

Preferred initial topics:

    hydroponics/{deviceId}/telemetry
    hydroponics/{deviceId}/status
    hydroponics/{deviceId}/commands
    hydroponics/{deviceId}/events

Document all changes in:

    docs/protocols/MQTT.md

Do not invent inconsistent topic structures.

---

# 28. API Development

Backend APIs should be versionable and predictable.

Examples:

    GET  /api/devices
    GET  /api/devices/:id
    GET  /api/measurements/latest
    GET  /api/measurements/history
    POST /api/commands
    GET  /api/alerts

Actual endpoints must be documented in:

    docs/api/API.md

---

# 29. API Design Rules

APIs should:

- Validate input
- Return structured errors
- Use appropriate HTTP status codes
- Authenticate protected endpoints
- Authorize device access
- Avoid exposing internal implementation details
- Avoid exposing GPIO mappings
- Use stable resource identifiers

---

# 30. Configuration Management

Use environment variables for deployment-specific configuration.

Examples:

    DATABASE_URL
    MQTT_HOST
    MQTT_PORT
    MQTT_USERNAME
    MQTT_PASSWORD
    API_URL

Provide:

    .env.example

Never commit real secrets.

---

# 31. Secrets Management

Never commit:

- Passwords
- API keys
- Tokens
- Private keys
- Database credentials
- MQTT credentials
- Cloud credentials
- Production `.env` files

Use environment variables or a proper secrets mechanism.

If a secret is accidentally exposed, report it immediately.

---

# 32. Dependency Management

Before adding a dependency:

1. Check whether an existing dependency provides the functionality.
2. Check whether the standard library is sufficient.
3. Check compatibility with the target platform.
4. Check maintenance status.
5. Consider security implications.

Avoid dependency proliferation.

---

# 33. Code Style

## TypeScript

Use:

- Strict TypeScript
- Explicit types where useful
- Small modules
- Domain-oriented organization
- Async/await
- Structured error handling

Avoid:

- `any` unless justified
- Global mutable state
- Huge services
- Hidden side effects

---

## Python

Use:

- Type hints
- Small functions
- Clear modules
- Structured logging
- Explicit exception handling

Avoid:

- Large scripts
- Global state
- Silent exception handling

---

## C/C++ Firmware

Use:

- Clear interfaces
- Small modules
- Constants instead of magic numbers
- Explicit initialization
- Defensive checks

Avoid:

- Excessive dynamic allocation
- Giant global state
- Unbounded blocking loops
- Hard-coded configuration scattered throughout the code

---

# 34. Naming Conventions

Logical device identifiers:

    esp32-01
    dht11-01
    ph-01
    ec-01
    pump-01
    valve-01

Use consistent naming throughout:

- Firmware
- MQTT
- Backend
- Database
- Frontend

Do not use different names for the same physical device in different
layers.

---

# 35. Logging

Use structured logging where practical.

Logs should include useful context such as:

- Timestamp
- Component
- Device ID
- Event
- Severity
- Error information

Do not log:

- Passwords
- Tokens
- Private keys
- Secrets

---

# 36. Error Handling

Expected failures include:

- Sensor disconnected
- Invalid sensor reading
- Sensor out of range
- ESP32 offline
- Raspberry Pi offline
- Wi-Fi unavailable
- MQTT unavailable
- Backend unavailable
- Database unavailable
- Camera unavailable
- CV failure
- Pump failure
- Valve failure
- No-flow condition
- Low-water condition

Errors must be explicit and observable.

Do not silently ignore important failures.

---

# 37. Testing Strategy

Testing occurs at four levels:

1. Unit tests
2. Component tests
3. Integration tests
4. Physical hardware tests

---

# 38. Unit Tests

Use unit tests for:

- Data validation
- Protocol parsing
- Telemetry transformation
- Business logic
- Alert logic
- Command validation
- Utility functions

---

# 39. Component Tests

Test individual modules such as:

    ESP32 telemetry serialization
    Raspberry Pi serial parser
    MQTT handler
    Backend telemetry ingestion
    Database repository
    Frontend data components

---

# 40. Integration Tests

Verify complete flows.

Telemetry:

    Sensor
      ↓
    ESP32
      ↓
    Pi
      ↓
    MQTT
      ↓
    Backend
      ↓
    PostgreSQL
      ↓
    Frontend

Control:

    Frontend
      ↓
    Backend
      ↓
    MQTT
      ↓
    Pi
      ↓
    ESP32
      ↓
    Actuator

---

# 41. Physical Hardware Tests

A successful software build does NOT mean the hardware works.

Physical verification must be explicitly performed for:

- Sensor readings
- GPIO behavior
- Relay behavior
- Pump behavior
- Valve behavior
- Safety shutdown
- Wi-Fi connectivity
- Raspberry Pi communication

Do not claim hardware functionality without physical verification.

---

# 42. Build Validation

After modifying code, run the appropriate build.

## ESP32

    PlatformIO build

## Backend

    npm install
    npm run build
    npm test

Use the actual package scripts defined by the repository.

## Frontend

    npm install
    npm run build
    npm test

Use the actual package scripts defined by the repository.

## Edge

    Python environment
    dependency installation
    tests
    static checks where configured

Do not invent commands that do not exist in the project.

---

# 43. Git Workflow

Use Git continuously.

Preferred workflow:

    Make change
      ↓
    Test
      ↓
    Review diff
      ↓
    Commit
      ↓
    Continue

Keep commits small and meaningful.

---

# 44. Commit Naming

Preferred commit prefixes:

    feat:
    fix:
    refactor:
    docs:
    test:
    chore:
    build:

Examples:

    feat: add DHT11 telemetry
    fix: handle sensor timeout
    docs: define telemetry protocol
    test: add telemetry parser tests
    chore: update dependencies

---

# 45. Git Safety

Never automatically execute destructive commands.

Do NOT run without explicit approval:

    git reset --hard
    git clean -fd
    git push --force

Before potentially destructive operations:

1. Check `git status`.
2. Identify affected files.
3. Explain the consequence.
4. Ask for approval.

Never overwrite uncommitted user work.

---

# 46. File Deletion

Do not delete files merely because they appear unused.

Before deleting a file:

1. Search for references.
2. Determine whether it is generated.
3. Determine whether another module depends on it.
4. Confirm the deletion is safe.

---

# 47. Agent Development Workflow

Every coding-agent task should follow:

    1. Read instructions
    2. Read architecture
    3. Inspect repository
    4. Understand existing code
    5. Identify affected modules
    6. Implement smallest change
    7. Build
    8. Test
    9. Review diff
    10. Report results

Agents should not modify unrelated areas.

---

# 48. Agent Task Scope

A task should preferably affect one subsystem at a time.

Good:

    Implement DHT11 sensor support.

Good:

    Implement ESP32 telemetry serialization.

Good:

    Implement Raspberry Pi MQTT client.

Bad:

    Build the entire hydroponics platform.

Large tasks should be decomposed into smaller tasks.

---

# 49. Agent Output Requirements

After completing a task, the agent should report:

## Summary

What was implemented.

## Files Changed

List important files.

## Tests

Commands/tests executed.

## Build

Whether the affected project built successfully.

## Hardware Verification

Whether physical hardware was tested.

## Known Issues

Remaining problems.

## Next Step

The smallest logical next development task.

---

# 50. Documentation Updates

When implementation changes an interface, update the relevant documentation.

Examples:

Telemetry change:

    docs/protocols/TELEMETRY.md

MQTT change:

    docs/protocols/MQTT.md

Hardware change:

    docs/hardware/HARDWARE.md

GPIO change:

    docs/hardware/PINOUT.md

API change:

    docs/api/API.md

Deployment change:

    docs/deployment/DEPLOYMENT.md

Do not leave documentation describing an obsolete interface.

---

# 51. Hardware Changes

Never guess hardware specifications.

Before generating hardware-specific code or wiring:

- Confirm exact component model.
- Confirm operating voltage.
- Confirm interface.
- Confirm current requirements.
- Confirm pinout where necessary.

If a hardware detail is uncertain and could cause damage, stop and ask
for the required information.

---

# 52. Electrical Rules

ESP32 GPIO pins must not directly power:

- Pumps
- Motors
- Solenoid valves
- High-current loads
- Mains equipment

Use appropriate driver hardware.

Possible interfaces include:

- Relay modules
- MOSFET drivers
- Transistor drivers
- Isolated drivers

Use appropriate external power supplies.

Do not assume a GPIO can source the required load current.

---

# 53. Calibration

Sensor calibration values must be treated as configuration.

Do not bury calibration constants inside unrelated application code.

Examples:

    pH calibration
    EC calibration
    Sensor offset
    Temperature compensation

Calibration documentation belongs under:

    docs/hardware/

---

# 54. Security Development

Security must be considered at each layer.

## ESP32

- Do not expose unnecessary services.
- Authenticate communication where practical.
- Do not hard-code credentials.

## Raspberry Pi

- Use secure credentials.
- Restrict exposed services.
- Keep the local network private.

## Backend

- Authenticate users.
- Authorize device access.
- Validate incoming device data.
- Validate commands.

## Frontend

- Do not store secrets.
- Do not trust client-side authorization.
- Treat backend authorization as authoritative.

---

# 55. Local vs Cloud Responsibilities

Local:

- Hardware control
- Safety
- Immediate sensor acquisition
- Basic automation
- Device communication

Cloud:

- Historical data
- User management
- Remote monitoring
- Remote commands
- Analytics
- Long-term storage

Never move safety-critical behavior exclusively to the cloud.

---

# 56. Performance Philosophy

Do not optimize prematurely.

First prioritize:

    Correctness
    Reliability
    Safety
    Maintainability

Then optimize based on actual measurements.

Avoid premature introduction of:

- Complex caching
- Distributed processing
- Multiple databases
- Message replay infrastructure
- GPU processing

unless the actual workload requires them.

---

# 57. MVP Feature Priority

## P0 — Mandatory

- ESP32
- DHT11
- Sensor telemetry
- Raspberry Pi gateway
- Wi-Fi communication
- MQTT
- Backend
- PostgreSQL
- Dashboard
- Basic actuator control
- Local safety

## P1 — Important

- pH
- EC/TDS
- Water temperature
- Flow
- Water level
- Alerts
- WebSocket
- Camera

## P2 — Enhancement

- Computer vision
- Plant analysis
- Advanced automation
- Historical analytics
- Predictive models
- OTA firmware updates

---

# 58. Time Management

The project has a very short MVP timeline.

If time becomes constrained:

Keep:

- Core telemetry
- Core backend
- Database
- Dashboard
- Actuator control
- Safety
- Device communication

Defer:

- Advanced AI
- Advanced analytics
- Complex automation
- Extensive UI customization
- Multi-device management
- Nonessential sensors

A smaller working system is preferable to a large incomplete system.

---

# 59. Development Checkpoint

At the end of each major stage, verify:

    Does it build?
    Does it run?
    Does it communicate?
    Does it handle failure?
    Does it preserve the architecture?
    Is the interface documented?

Do not proceed indefinitely while a foundational stage is broken.

---

# 60. Current Development Roadmap

## Phase 1 — ESP32

    DHT11
      ↓
    ESP32
      ↓
    Serial

Goal:

    Verified sensor readings.

---

## Phase 2 — Local Wireless

    DHT11
      ↓
    ESP32
      ↓
    Wi-Fi
      ↓
    Raspberry Pi

Goal:

    Reliable local communication.

---

## Phase 3 — Messaging

    ESP32
      ↓
    Wi-Fi
      ↓
    Raspberry Pi
      ↓
    MQTT

Goal:

    Structured telemetry and commands.

---

## Phase 4 — Cloud

    MQTT
      ↓
    Backend
      ↓
    PostgreSQL

Goal:

    Persistent telemetry.

---

## Phase 5 — Dashboard

    PostgreSQL
      ↓
    Backend
      ↓
    WebSocket/API
      ↓
    Dashboard

Goal:

    Real-time monitoring.

---

## Phase 6 — Control

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
    Pump/Valve

Goal:

    Verified remote actuator control.

---

## Phase 7 — Vision

    Camera
      ↓
    Raspberry Pi
      ↓
    CV/AI
      ↓
    Backend
      ↓
    Dashboard

Goal:

    Basic plant visual analysis.

---

# 61. Definition of Done

A feature is considered complete only when:

1. Code is implemented.
2. Relevant tests pass.
3. Build succeeds.
4. Documentation is updated if required.
5. No unrelated code was modified unnecessarily.
6. Error handling exists for expected failures.
7. Hardware is physically verified when applicable.
8. Git diff has been reviewed.
9. The feature does not violate the architecture.
10. The next developer/agent can understand the implementation.

---

# 62. Final Development Principle

Always maintain this progression:

    BUILD
      ↓
    TEST
      ↓
    VERIFY
      ↓
    DOCUMENT
      ↓
    COMMIT
      ↓
    INTEGRATE

Do not accumulate large amounts of unverified code.

The objective is not simply to produce source code.

The objective is to produce a working, testable, modular hydroponics
system whose hardware, edge, cloud, and frontend layers can evolve
independently.