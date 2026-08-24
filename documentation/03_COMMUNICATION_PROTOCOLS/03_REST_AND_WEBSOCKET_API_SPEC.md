# Hydroponics Platform — API Specification

## 1. Purpose

This document defines the HTTP REST API and WebSocket interface for the
Hydroponics Platform.

The API is the application boundary between the web dashboard and the
backend.

The architecture is:

    Web Dashboard
          ↓
    REST API / WebSocket
          ↓
       Backend
          ↓
        MQTT
          ↓
    Raspberry Pi
          ↓
        ESP32
          ↓
    Sensors / Actuators

The frontend must never directly communicate with:

- ESP32
- Raspberry Pi
- MQTT broker
- PostgreSQL
- Hardware GPIO

---

# 2. Responsibilities

The backend API is responsible for:

- Authentication
- Authorization
- Device discovery
- Device status
- Sensor information
- Latest telemetry
- Historical telemetry
- Actuator information
- Actuator commands
- Command status
- Alerts
- Dashboard aggregation
- Real-time WebSocket updates

The API is not responsible for direct hardware control.

The backend sends commands through MQTT.

---

# 3. API Version

Current API version:

    v1

Base path:

    /api/v1

Example:

    GET /api/v1/devices

Breaking API changes require a new version.

Example:

    /api/v2

---

# 4. Transport

REST:

    HTTPS

Real-time:

    WebSocket over TLS

Production:

    HTTPS
    WSS

Development may use:

    HTTP
    WS

---

# 5. Base URL

Development:

    http://localhost:<BACKEND_PORT>/api/v1

Production:

    https://<BACKEND_DOMAIN>/api/v1

The production URL must be supplied through environment configuration.

Never hard-code deployment-specific URLs in frontend source code.

---

# 6. Authentication

Protected endpoints require authentication.

The authentication mechanism is implementation-dependent.

Possible mechanisms:

- JWT
- Secure session cookies
- OAuth/OIDC

The frontend must not be treated as a trusted security boundary.

All authorization decisions must occur server-side.

---

# 7. Authorization

Authentication determines:

    Who is the user?

Authorization determines:

    What is the user allowed to access?

The backend must verify access to every protected device resource.

Example:

    User A
      ↓
    Device A
      ✓

    User A
      ↓
    Device B
      ✗

The frontend must never be relied upon to enforce device isolation.

---

# 8. Device Identity

Devices are identified using logical IDs.

Example:

    esp32-01

The API must never expose or depend on hardware implementation
details such as:

    GPIO17
    GPIO23
    relay-channel-2

Hardware mappings belong to the ESP32 firmware.

---

# 9. Standard Response Envelope

Successful response:

```json
{
  "success": true,
  "data": {}
}
```

Error response:

```json
{
  "success": false,
  "error": {
    "code": "DEVICE_NOT_FOUND",
    "message": "The requested device does not exist."
  }
}
```

---

# 10. Error Object

Error fields:

| Field | Required | Description |
|---|---:|---|
| `code` | Yes | Machine-readable error code |
| `message` | Yes | Human-readable message |
| `details` | No | Additional structured information |
| `requestId` | Recommended | Request correlation ID |

Example:

```json
{
  "success": false,
  "error": {
    "code": "DEVICE_NOT_FOUND",
    "message": "The requested device does not exist.",
    "requestId": "req-123"
  }
}
```

---

# 11. HTTP Status Codes

| Status | Meaning |
|---:|---|
| 200 | Successful request |
| 201 | Resource created |
| 202 | Accepted for asynchronous processing |
| 204 | Successful request with no response body |
| 400 | Invalid request |
| 401 | Authentication required |
| 403 | Insufficient permission |
| 404 | Resource not found |
| 409 | Resource conflict |
| 422 | Validation error |
| 429 | Rate limit exceeded |
| 500 | Internal server error |
| 502 | Upstream/edge failure |
| 503 | Service unavailable |

---

# 12. Request IDs

Every API request should have a request ID.

Example:

    req-01J8K8X4R3

The request ID should be used for tracing:

    Frontend
      ↓
    Backend
      ↓
    MQTT
      ↓
    Raspberry Pi
      ↓
    ESP32

Do not expose internal secrets in request logs.

---

# 13. Health Endpoint

## GET

    /api/health

Purpose:

Determine whether the backend process is running.

Example:

```json
{
  "status": "ok"
}
```

This endpoint should not expose sensitive infrastructure information.

---

# 14. Readiness Endpoint

## GET

    /api/ready

Purpose:

Determine whether the backend is ready to serve requests.

The backend may verify:

- Database connectivity
- MQTT connectivity
- Required services

Example:

```json
{
  "status": "ready"
}
```

Do not expose credentials or connection strings.

---

# 15. Device Endpoints

Base:

    /api/v1/devices

---

# 16. List Devices

## GET

    /api/v1/devices

Returns devices accessible to the authenticated user.

Example:

```json
{
  "success": true,
  "data": {
    "devices": [
      {
        "id": "esp32-01",
        "name": "Hydroponics Controller 01",
        "status": "ONLINE",
        "firmwareVersion": "0.1.0",
        "lastSeenAt": "2026-08-14T10:30:00.000Z"
      }
    ]
  }
}
```

---

# 17. Get Device

## GET

    /api/v1/devices/{deviceId}

Example:

    GET /api/v1/devices/esp32-01

Response:

```json
{
  "success": true,
  "data": {
    "id": "esp32-01",
    "name": "Hydroponics Controller 01",
    "status": "ONLINE",
    "firmwareVersion": "0.1.0",
    "uptimeSeconds": 4821,
    "lastSeenAt": "2026-08-14T10:30:00.000Z"
  }
}
```

---

# 18. Device Status

## GET

    /api/v1/devices/{deviceId}/status

Example:

    GET /api/v1/devices/esp32-01/status

Response:

```json
{
  "success": true,
  "data": {
    "deviceId": "esp32-01",
    "status": "ONLINE",
    "lastSeenAt": "2026-08-14T10:30:00.000Z",
    "firmwareVersion": "0.1.0",
    "uptimeSeconds": 4821
  }
}
```

---

# 19. Device Sensors

## GET

    /api/v1/devices/{deviceId}/sensors

Example:

    GET /api/v1/devices/esp32-01/sensors

Response:

```json
{
  "success": true,
  "data": {
    "sensors": [
      {
        "id": "dht11-01",
        "type": "DHT11",
        "status": "CONNECTED",
        "metrics": [
          "air_temperature",
          "humidity"
        ]
      }
    ]
  }
}
```

---

# 20. Device Actuators

## GET

    /api/v1/devices/{deviceId}/actuators

Example response:

```json
{
  "success": true,
  "data": {
    "actuators": [
      {
        "id": "pump-01",
        "type": "PUMP",
        "state": "OFF",
        "capabilities": [
          "ON",
          "OFF"
        ]
      }
    ]
  }
}
```

---

# 21. Latest Telemetry

## GET

    /api/v1/devices/{deviceId}/telemetry/latest

Returns the latest known measurement for each metric.

Example:

```json
{
  "success": true,
  "data": {
    "deviceId": "esp32-01",
    "timestamp": "2026-08-14T10:30:00.000Z",
    "measurements": [
      {
        "sensorId": "dht11-01",
        "metric": "air_temperature",
        "value": 27.4,
        "unit": "C",
        "quality": "GOOD"
      },
      {
        "sensorId": "dht11-01",
        "metric": "humidity",
        "value": 61.2,
        "unit": "%",
        "quality": "GOOD"
      }
    ]
  }
}
```

---

# 22. Historical Telemetry

## GET

    /api/v1/devices/{deviceId}/telemetry

Supported query parameters:

    sensorId
    metric
    from
    to
    limit
    cursor

Example:

    GET /api/v1/devices/esp32-01/telemetry?metric=air_temperature&from=2026-08-14T00:00:00Z&to=2026-08-14T12:00:00Z

---

# 23. Historical Telemetry Response

```json
{
  "success": true,
  "data": {
    "deviceId": "esp32-01",
    "measurements": [
      {
        "sensorId": "dht11-01",
        "metric": "air_temperature",
        "value": 27.4,
        "unit": "C",
        "quality": "GOOD",
        "timestamp": "2026-08-14T10:30:00.000Z"
      },
      {
        "sensorId": "dht11-01",
        "metric": "air_temperature",
        "value": 27.3,
        "unit": "C",
        "quality": "GOOD",
        "timestamp": "2026-08-14T10:35:00.000Z"
      }
    ],
    "pagination": {
      "nextCursor": "cursor-value"
    }
  }
}
```

---

# 24. Pagination

Historical telemetry must support pagination.

Preferred approach:

    Cursor-based pagination

Example:

    ?limit=100&cursor=<cursor>

The API must never return an unlimited number of telemetry records.

---

# 25. Telemetry Query Limits

The backend must enforce:

- Maximum result count
- Maximum time range
- Valid timestamps
- Valid metric names
- Valid sensor IDs

Exact limits:

    TBD

---

# 26. Telemetry Aggregation

Future versions may support aggregation.

Example:

    GET /api/v1/devices/esp32-01/telemetry
        ?metric=air_temperature
        &interval=5m
        &aggregation=avg

Potential aggregations:

    avg
    min
    max
    sum

The MVP should initially support raw measurements only.

---

# 27. Sensor Latest Reading

## GET

    /api/v1/sensors/{sensorId}/latest

Example:

    GET /api/v1/sensors/dht11-01/latest

Response:

```json
{
  "success": true,
  "data": {
    "sensorId": "dht11-01",
    "metric": "air_temperature",
    "value": 27.4,
    "unit": "C",
    "quality": "GOOD",
    "timestamp": "2026-08-14T10:30:00.000Z"
  }
}
```

---

# 28. Actuator State

## GET

    /api/v1/devices/{deviceId}/actuators/{actuatorId}

Example:

    GET /api/v1/devices/esp32-01/actuators/pump-01

Response:

```json
{
  "success": true,
  "data": {
    "id": "pump-01",
    "type": "PUMP",
    "state": "OFF",
    "capabilities": [
      "ON",
      "OFF"
    ],
    "lastChangedAt": "2026-08-14T10:20:00.000Z"
  }
}
```

---

# 29. Send Actuator Command

## POST

    /api/v1/devices/{deviceId}/actuators/{actuatorId}/commands

Example:

    POST /api/v1/devices/esp32-01/actuators/pump-01/commands

Request:

```json
{
  "action": "SET_ACTUATOR_STATE",
  "parameters": {
    "state": "ON"
  }
}
```

The backend generates a unique:

    commandId

---

# 30. Command Response

Hardware commands are asynchronous.

The API therefore returns:

    202 Accepted

Example:

```json
{
  "success": true,
  "data": {
    "commandId": "cmd-001",
    "status": "QUEUED"
  }
}
```

`QUEUED` means the backend accepted the request.

It does NOT mean the physical actuator is ON.

---

# 31. Command Status

## GET

    /api/v1/commands/{commandId}

Example:

    GET /api/v1/commands/cmd-001

Response:

```json
{
  "success": true,
  "data": {
    "commandId": "cmd-001",
    "deviceId": "esp32-01",
    "actuatorId": "pump-01",
    "action": "SET_ACTUATOR_STATE",
    "status": "EXECUTED",
    "requestedAt": "2026-08-14T10:35:00.000Z",
    "executedAt": "2026-08-14T10:35:02.000Z"
  }
}
```

---

# 32. Command Status Values

Commands use the lifecycle defined in `COMMANDS.md`:

    CREATED
    QUEUED
    DELIVERED
    ACCEPTED
    EXECUTED
    REJECTED
    BLOCKED
    FAILED
    EXPIRED

---

# 33. Emergency Stop

## POST

    /api/v1/devices/{deviceId}/emergency-stop

Example:

    POST /api/v1/devices/esp32-01/emergency-stop

Request:

```json
{
  "reason": "Manual emergency shutdown"
}
```

Response:

```json
{
  "success": true,
  "data": {
    "commandId": "cmd-stop-001",
    "status": "QUEUED"
  }
}
```

Emergency stop must have appropriate authorization and audit logging.

---

# 34. Request Device Status

## POST

    /api/v1/devices/{deviceId}/status/request

Purpose:

Request a fresh status message from the device.

Response:

```json
{
  "success": true,
  "data": {
    "commandId": "cmd-status-001",
    "status": "QUEUED"
  }
}
```

---

# 35. Dashboard Summary

## GET

    /api/v1/dashboard/summary

Purpose:

Return the information required to initialize the main dashboard.

Example:

```json
{
  "success": true,
  "data": {
    "devices": {
      "total": 1,
      "online": 1,
      "offline": 0
    },
    "alerts": {
      "active": 0,
      "critical": 0
    },
    "latestMeasurements": [
      {
        "deviceId": "esp32-01",
        "sensorId": "dht11-01",
        "metric": "air_temperature",
        "value": 27.4,
        "unit": "C",
        "quality": "GOOD",
        "timestamp": "2026-08-14T10:30:00.000Z"
      },
      {
        "deviceId": "esp32-01",
        "sensorId": "dht11-01",
        "metric": "humidity",
        "value": 61.2,
        "unit": "%",
        "quality": "GOOD",
        "timestamp": "2026-08-14T10:30:00.000Z"
      }
    ]
  }
}
```

---

# 36. WebSocket

WebSocket endpoint:

    /api/v1/ws

Production:

    wss://<backend-domain>/api/v1/ws

WebSocket is used for real-time dashboard updates.

---

# 37. WebSocket Event Types

Initial event types:

    telemetry
    device_status
    actuator_state
    command_result
    alert
    event

---

# 38. WebSocket Event Envelope

```json
{
  "type": "telemetry",
  "timestamp": "2026-08-14T10:30:00.000Z",
  "data": {}
}
```

---

# 39. Telemetry WebSocket Event

```json
{
  "type": "telemetry",
  "timestamp": "2026-08-14T10:30:00.000Z",
  "data": {
    "deviceId": "esp32-01",
    "sensorId": "dht11-01",
    "metric": "air_temperature",
    "value": 27.4,
    "unit": "C",
    "quality": "GOOD"
  }
}
```

---

# 40. Device Status Event

```json
{
  "type": "device_status",
  "timestamp": "2026-08-14T10:31:00.000Z",
  "data": {
    "deviceId": "esp32-01",
    "status": "OFFLINE"
  }
}
```

---

# 41. Actuator State Event

```json
{
  "type": "actuator_state",
  "timestamp": "2026-08-14T10:35:02.000Z",
  "data": {
    "deviceId": "esp32-01",
    "actuatorId": "pump-01",
    "state": "ON"
  }
}
```

---

# 42. Command Result Event

```json
{
  "type": "command_result",
  "timestamp": "2026-08-14T10:35:02.000Z",
  "data": {
    "commandId": "cmd-001",
    "deviceId": "esp32-01",
    "actuatorId": "pump-01",
    "status": "EXECUTED"
  }
}
```

---

# 43. Alert Event

```json
{
  "type": "alert",
  "timestamp": "2026-08-14T10:40:00.000Z",
  "data": {
    "id": "alert-001",
    "deviceId": "esp32-01",
    "type": "LOW_WATER",
    "severity": "CRITICAL",
    "status": "ACTIVE"
  }
}
```

---

# 44. WebSocket Authentication

The WebSocket connection must be authenticated.

Unauthenticated clients must not receive private telemetry or device
events.

---

# 45. WebSocket Authorization

The backend must filter events based on the authenticated user's
device permissions.

Example:

    User A
      ↓
    esp32-01
      ✓

    User A
      ↓
    esp32-99
      ✗

---

# 46. WebSocket Reconnection

The frontend must automatically reconnect after connection loss.

Use exponential backoff.

Avoid aggressive reconnect loops.

After reconnecting, the frontend should refresh current state through
REST before relying solely on live events.

Recommended:

    WebSocket reconnect
          ↓
    GET dashboard summary
          ↓
    Resume live events

---

# 47. REST vs WebSocket

Use REST for:

- Initial page load
- Device discovery
- Historical telemetry
- Device configuration
- Commands
- Command status
- Alerts

Use WebSocket for:

- Live telemetry
- Device status
- Actuator state
- Command results
- Alerts
- Events

---

# 48. Dashboard Initialization

Recommended flow:

    Dashboard loads
          ↓
    GET /dashboard/summary
          ↓
    Render initial state
          ↓
    Connect WebSocket
          ↓
    Receive live events
          ↓
    Update UI

The dashboard must not wait indefinitely for WebSocket connectivity
before rendering.

---

# 49. Historical Chart Flow

Example:

    User selects:
        Last 24 hours

Frontend:

    GET /devices/{deviceId}/telemetry
        ?metric=air_temperature
        &from=...
        &to=...

Backend:

    PostgreSQL

Frontend:

    Render chart

New measurements:

    MQTT
      ↓
    Backend
      ↓
    WebSocket
      ↓
    Chart update

---

# 50. Control Flow

When the user clicks:

    Pump ON

Frontend:

    POST /devices/esp32-01/actuators/pump-01/commands

Backend:

    Authenticate
      ↓
    Authorize
      ↓
    Validate
      ↓
    Create command
      ↓
    Publish MQTT

ESP32:

    Receive command
      ↓
    Validate
      ↓
    Safety check
      ↓
    Control pump

ESP32:

    Publish command result
      ↓
    MQTT

Backend:

    Process result
      ↓
    WebSocket

Frontend:

    Pump ON

---

# 51. Command Safety

The API must never assume that an accepted command will be executed.

Example:

    API:
        202 Accepted

does not mean:

    Pump = ON

The ESP32 may return:

    BLOCKED
    LOW_WATER

The backend must propagate the resulting state to the dashboard.

---

# 52. API Does Not Control GPIO

The API operates using logical actuator identifiers.

Correct:

    pump-01 = ON

Incorrect:

    GPIO17 = HIGH

The mapping is handled by the ESP32 firmware.

---

# 53. API Does Not Communicate Directly With ESP32

Incorrect:

    Browser
       ↓
    ESP32

Correct:

    Browser
       ↓
    Backend
       ↓
    MQTT
       ↓
    Raspberry Pi
       ↓
    ESP32

This provides:

- Authentication
- Authorization
- Auditability
- Device isolation
- Centralized control
- Network abstraction

---

# 54. Idempotency

Actuator command creation should support idempotency.

Recommended HTTP header:

    Idempotency-Key: <unique-key>

If the same request is retried with the same idempotency key, the
backend should return the original command rather than creating a
second command.

This is important when the frontend loses the HTTP response after the
backend has already created the command.

---

# 55. Rate Limiting

The backend should rate-limit sensitive endpoints.

Examples:

    Authentication
    Command creation
    Emergency stop
    Historical telemetry queries

Read-only telemetry endpoints may have higher limits.

---

# 56. Freshness

Measurement responses must contain timestamps.

Example:

```json
{
  "value": 27.4,
  "unit": "C",
  "timestamp": "2026-08-14T10:30:00.000Z"
}
```

The frontend should determine whether data is:

    FRESH
    STALE
    OFFLINE

based on timestamp and device status.

---

# 57. Device Offline Detection

The backend should track:

    lastTelemetryAt
    lastStatusAt
    lastHeartbeatAt

If the device exceeds the configured timeout:

    ONLINE
        ↓
    STALE
        ↓
    OFFLINE

Exact timeout:

    TBD

---

# 58. Database Boundary

The frontend must never connect directly to PostgreSQL.

Correct:

    Frontend
      ↓
    API
      ↓
    PostgreSQL

Incorrect:

    Frontend
      ↓
    PostgreSQL

---

# 59. MQTT Boundary

The frontend must never connect directly to MQTT.

Correct:

    Frontend
      ↓
    API / WebSocket
      ↓
    Backend
      ↓
    MQTT

Incorrect:

    Frontend
      ↓
    MQTT Broker

---

# 60. API ↔ MQTT Relationship

The API defines the application interface.

MQTT defines the hardware messaging interface.

Example:

Frontend sends:

```json
{
  "action": "SET_ACTUATOR_STATE",
  "parameters": {
    "state": "ON"
  }
}
```

Backend converts this into the command format defined by
`COMMANDS.md` and publishes:

    hydroponics/esp32-01/commands

The frontend does not need to know the MQTT topic.

---

# 61. API ↔ Telemetry Relationship

MQTT receives telemetry according to:

    TELEMETRY.md

The backend validates and persists the telemetry.

The API exposes normalized representations to the frontend.

Therefore:

    ESP32
      ↓
    TELEMETRY
      ↓
    MQTT
      ↓
    Backend
      ↓
    PostgreSQL
      ↓
    API
      ↓
    Frontend

---

# 62. API ↔ Command Relationship

The frontend sends an API command request.

The backend creates a command using the contract in:

    COMMANDS.md

Then publishes it using:

    MQTT.md

The hardware executes it according to local safety rules.

---

# 63. Alerts

Base endpoint:

    /api/v1/alerts

---

# 64. List Alerts

## GET

    /api/v1/alerts

Supported filters:

    deviceId
    severity
    status
    from
    to
    limit
    cursor

Example:

    GET /api/v1/alerts?deviceId=esp32-01&status=ACTIVE

---

# 65. Alert Response

```json
{
  "success": true,
  "data": {
    "alerts": [
      {
        "id": "alert-001",
        "deviceId": "esp32-01",
        "type": "LOW_WATER",
        "severity": "CRITICAL",
        "status": "ACTIVE",
        "createdAt": "2026-08-14T10:40:00.000Z"
      }
    ]
  }
}
```

---

# 66. Acknowledge Alert

## POST

    /api/v1/alerts/{alertId}/acknowledge

Acknowledgement does not disable the underlying safety condition.

Example:

```json
{
  "success": true,
  "data": {
    "id": "alert-001",
    "status": "ACKNOWLEDGED"
  }
}
```

---

# 67. Resolve Alert

## POST

    /api/v1/alerts/{alertId}/resolve

An alert should only be resolved when its underlying condition has been
cleared or the system explicitly permits resolution.

---

# 68. Logging

API logs should contain:

    requestId
    endpoint
    HTTP method
    response status
    request duration

Command-related logs should also contain:

    commandId
    deviceId
    actuatorId

Never log:

- Passwords
- JWT secrets
- API keys
- MQTT passwords
- Private keys

---

# 69. Observability

Future backend metrics should include:

    API request count
    API latency
    MQTT message rate
    MQTT connection status
    Telemetry ingestion rate
    Command success rate
    Command failure rate
    WebSocket connections

These are infrastructure/application metrics and are separate from
hydroponics telemetry.

---

# 70. Future Camera API

Potential future endpoint:

    GET /api/v1/devices/{deviceId}/camera

Potential functionality:

- Latest image
- Image history
- Camera status
- Capture request

Images should not normally be transferred through MQTT.

Preferred architecture:

    Camera
      ↓
    Raspberry Pi
      ↓
    HTTP/Object Storage
      ↓
    Backend
      ↓
    Dashboard

MQTT may carry image metadata or event notifications.

---

# 71. Future Computer Vision API

Potential endpoint:

    GET /api/v1/devices/{deviceId}/vision/latest

Potential results:

    plant_detected
    plant_area_percent
    leaf_area
    anomaly_detected
    confidence

The API must remain independent of the specific AI model.

---

# 72. Future Automation API

Potential endpoints:

    GET    /api/v1/automations

    POST   /api/v1/automations

    PATCH  /api/v1/automations/{automationId}

    DELETE /api/v1/automations/{automationId}

Automation must never bypass ESP32 safety rules.

---

# 73. Future Configuration API

Potential configuration:

    Sensor sampling intervals
    Alert thresholds
    Pump runtime limits
    Water-level thresholds
    Calibration settings

Configuration changes must be:

- Authenticated
- Authorized
- Validated
- Audited

---

# 74. OpenAPI

The production implementation should eventually expose an OpenAPI
specification.

Possible location:

    /api/docs

The OpenAPI definition should eventually become the machine-readable
source of truth for:

- Backend
- Frontend
- API clients
- Testing
- Documentation

---

# 75. MVP Endpoint Set

The 4–5 day MVP should implement only:

## Health

    GET /api/health

## Devices

    GET /api/v1/devices

    GET /api/v1/devices/{deviceId}

## Device status

    GET /api/v1/devices/{deviceId}/status

## Sensors

    GET /api/v1/devices/{deviceId}/sensors

## Latest telemetry

    GET /api/v1/devices/{deviceId}/telemetry/latest

## Historical telemetry

    GET /api/v1/devices/{deviceId}/telemetry

## Actuators

    GET /api/v1/devices/{deviceId}/actuators

    GET /api/v1/devices/{deviceId}/actuators/{actuatorId}

## Commands

    POST /api/v1/devices/{deviceId}/actuators/{actuatorId}/commands

## Command status

    GET /api/v1/commands/{commandId}

## Emergency stop

    POST /api/v1/devices/{deviceId}/emergency-stop

## Dashboard

    GET /api/v1/dashboard/summary

## Real-time

    WS /api/v1/ws

---

# 76. MVP Implementation Order

Implement in this order:

    1. Health endpoint
    2. Device model
    3. Telemetry ingestion
    4. Latest telemetry endpoint
    5. Historical telemetry endpoint
    6. Device status
    7. Dashboard summary
    8. WebSocket
    9. Actuator model
    10. Command creation
    11. MQTT command publishing
    12. Command result handling
    13. Emergency stop
    14. Authentication hardening
    15. Authorization hardening

Do not build the complete future API before the telemetry path works
end-to-end.

---

# 77. End-to-End Monitoring Flow

    DHT11
      ↓
    ESP32
      ↓
    MQTT
      ↓
    Backend
      ↓
    PostgreSQL

Dashboard:

    Frontend
      ↓
    GET /dashboard/summary
      ↓
    Backend
      ↓
    PostgreSQL
      ↓
    Dashboard

Live update:

    MQTT
      ↓
    Backend
      ↓
    WebSocket
      ↓
    Frontend

---

# 78. End-to-End Control Flow

    User clicks:
        Pump ON

          ↓

    Frontend

          ↓

    POST /devices/esp32-01/actuators/pump-01/commands

          ↓

    Backend

        Authenticate
        Authorize
        Validate
        Create command

          ↓

    MQTT

          ↓

    Raspberry Pi

          ↓

    ESP32

        Validate
        Safety check

          ↓

    Pump

          ↓

    Command result

          ↓

    MQTT

          ↓

    Backend

          ↓

    WebSocket

          ↓

    Dashboard

        Pump: ON
```

---

# 79. Definition of Done

The API layer is MVP-ready when:

- Health endpoint works.
- Device list works.
- Device status works.
- Sensor information works.
- Latest telemetry works.
- Historical telemetry works.
- Dashboard summary works.
- WebSocket delivers live telemetry.
- Actuator state can be queried.
- Commands can be created.
- Commands are published through MQTT.
- Command results are processed.
- Emergency stop works.
- API validation exists.
- Consistent errors are returned.
- Device authorization is enforced.
- Request IDs are supported.
- Sensitive data is not logged.

---

# 80. Final API Principle

The application boundary is:

    FRONTEND
        ↓
    REST API / WEBSOCKET
        ↓
    BACKEND
        ↓
    MQTT
        ↓
    RASPBERRY PI
        ↓
    ESP32
        ↓
    HARDWARE

The frontend owns presentation.

The backend owns application logic, authorization, persistence, and
MQTT integration.

The Raspberry Pi owns edge processing and gateway responsibilities.

The ESP32 owns hardware interaction and local safety.

The hardware owns physical state.

The system must never treat:

    "API accepted"

or:

    "MQTT message delivered"

as equivalent to:

    "physical action completed".

Only confirmed hardware state or command execution results should be
presented as successful physical actions.