# Hydroponics Platform — Security Architecture

## 1. Purpose

This document defines the security architecture, trust boundaries,
security responsibilities, threat model, and security requirements for
the Hydroponics Platform.

The platform is a cyber-physical system. A security failure can affect
not only software and data, but also physical equipment such as:

- Pumps
- Valves
- Relays
- Nutrient systems
- Lighting
- Water circulation systems

Therefore, security must protect both:

    DIGITAL SYSTEMS

and:

    PHYSICAL SYSTEMS

The primary security principle is:

> Remote connectivity must never be able to bypass local hardware safety.

---

# 2. Security Objectives

The system must protect:

1. User accounts.
2. Device identities.
3. MQTT credentials.
4. API credentials.
5. Database credentials.
6. Sensor telemetry.
7. Actuator commands.
8. Camera data.
9. Computer vision results.
10. System configuration.
11. Hardware safety.
12. Audit information.

The system should provide:

- Authentication
- Authorization
- Confidentiality
- Integrity
- Availability
- Accountability
- Device isolation
- Command validation
- Local safety enforcement
- Secure secret management

---

# 3. Security Architecture

The high-level security boundary is:

```text
                         INTERNET
                            │
                           TLS
                            │
                            ▼
                   ┌─────────────────┐
                   │    FRONTEND     │
                   └────────┬────────┘
                            │
                         HTTPS
                            │
                            ▼
                   ┌─────────────────┐
                   │     BACKEND     │
                   │                 │
                   │ Authentication │
                   │ Authorization  │
                   │ Validation      │
                   │ Business Logic │
                   └────────┬────────┘
                            │
                         MQTT/TLS
                            │
                            ▼
                   ┌─────────────────┐
                   │  MQTT BROKER    │
                   └────────┬────────┘
                            │
                         TLS / LAN
                            │
                            ▼
                   ┌─────────────────┐
                   │  RASPBERRY PI   │
                   │                 │
                   │ Edge Gateway    │
                   │ Camera / CV     │
                   └────────┬────────┘
                            │
                         Local Wi-Fi
                            │
                            ▼
                   ┌─────────────────┐
                   │      ESP32      │
                   │                 │
                   │ Device Auth     │
                   │ Validation      │
                   │ Local Safety    │
                   └────────┬────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │    HARDWARE     │
                   │                 │
                   │ Sensors         │
                   │ Pumps           │
                   │ Valves          │
                   │ Relays          │
                   └─────────────────┘
```

---

# 4. Core Security Principles

## Principle 1 — Least Privilege

Every component must receive only the permissions required for its
function.

Examples:

- Frontend cannot access PostgreSQL.
- Frontend cannot access MQTT.
- ESP32 cannot access PostgreSQL.
- ESP32 cannot access arbitrary cloud APIs.
- Backend should not have unnecessary operating-system privileges.
- Raspberry Pi services should run as non-root users whenever possible.

---

# 5. Principle 2 — Defense in Depth

Security must not depend on a single control.

Example:

```text
User Authentication
        ↓
Authorization
        ↓
API Validation
        ↓
Command Validation
        ↓
MQTT Authorization
        ↓
Device Validation
        ↓
ESP32 Safety Rules
        ↓
Physical Hardware
```

A failure of one layer should not automatically compromise the entire
system.

---

# 6. Principle 3 — Local Safety

The ESP32 is the final authority for immediate physical safety.

The backend can request:

```text
PUMP ON
```

but the ESP32 must determine whether this operation is safe.

Example:

```text
Backend:
    Pump ON

ESP32:
    Water level LOW

Result:
    Pump OFF
    Reason = LOW_WATER
```

Cloud services must never be able to bypass this protection.

---

# 7. Principle 4 — Never Trust the Client

The frontend is an untrusted client.

The backend must not trust:

- device IDs
- actuator IDs
- command parameters
- user roles
- permissions
- timestamps
- ownership claims

provided by the frontend.

All security-sensitive decisions must be enforced server-side.

---

# 8. Principle 5 — Fail Securely

When security or communication state is uncertain, the system should
prefer a safe state.

Examples:

```text
Invalid command
    → Reject

Unknown device
    → Reject

Unauthorized actuator
    → Reject

Invalid MQTT message
    → Reject

Unsafe physical condition
    → Keep actuator in safe state
```

---

# 9. Trust Boundaries

The system contains several trust boundaries.

## Boundary 1

```text
Internet
    ↓
Cloud Infrastructure
```

Untrusted external traffic enters the platform here.

---

## Boundary 2

```text
Frontend
    ↓
Backend
```

The frontend is treated as untrusted.

---

## Boundary 3

```text
Backend
    ↓
MQTT Broker
```

Only authenticated and authorized services may publish or subscribe.

---

## Boundary 4

```text
Raspberry Pi
    ↓
ESP32
```

Device messages must be validated.

---

## Boundary 5

```text
ESP32
    ↓
Physical Hardware
```

The firmware is the final software safety boundary.

---

# 10. User Authentication

Users must authenticate before accessing protected dashboard
functionality.

Possible mechanisms include:

- Secure session cookies
- JWT
- OAuth/OIDC
- Identity provider integration

The final mechanism should be selected based on the deployment
environment.

Authentication credentials must never be stored in frontend source
code.

---

# 11. Session Security

If session cookies are used, production cookies should use:

```text
Secure
HttpOnly
SameSite
```

The appropriate `SameSite` configuration depends on deployment
architecture.

Sessions should have appropriate expiration and revocation behavior.

---

# 12. Password Security

If the platform manages passwords directly:

- Never store plaintext passwords.
- Never log passwords.
- Use a modern password hashing algorithm.
- Use appropriate password hashing parameters.
- Support password reset through a secure flow.
- Rate-limit authentication attempts.

Prefer a mature identity provider where practical rather than
implementing authentication primitives from scratch.

---

# 13. Authorization

Authentication answers:

```text
Who is the user?
```

Authorization answers:

```text
What is the user allowed to do?
```

Every protected resource must be authorized.

Example:

```text
User A
  ↓
Device A
  ✓

User A
  ↓
Device B
  ✗
```

The frontend must not be relied upon to enforce this boundary.

---

# 14. Device Authorization

The backend must verify that the authenticated user has permission
to access the requested device.

Example request:

```text
GET /api/v1/devices/esp32-01/telemetry
```

The backend must verify:

```text
Authenticated user
        ↓
Authorized for esp32-01?
        ↓
YES → Continue
NO  → 403 Forbidden
```

Never assume that possession of a `deviceId` grants access.

---

# 15. Actuator Authorization

Actuator control is more sensitive than telemetry access.

Before creating a command:

```text
Authenticate user
        ↓
Authorize device
        ↓
Authorize actuator
        ↓
Validate action
        ↓
Validate parameters
        ↓
Create command
```

Unauthorized actuator operations must be rejected.

---

# 16. Emergency Stop Authorization

Emergency stop should have explicit authorization.

The endpoint must:

- Authenticate the user.
- Authorize access to the device.
- Validate the device.
- Record the request.
- Publish the stop command.
- Track the result.

However, the ESP32 should also support local emergency/safety
conditions independently of the cloud.

---

# 17. Device Identity

Every ESP32 must have a unique logical identity.

Example:

```text
esp32-01
```

Production devices should have unique credentials.

Do not use one shared credential for every ESP32 if per-device
credentials are practical.

---

# 18. Device Credentials

Device credentials must:

- Be unique where practical.
- Be stored securely.
- Never be committed to Git.
- Never be embedded in public documentation.
- Never be logged.
- Be revocable or replaceable.
- Be rotated when compromise is suspected.

Development credentials must be separate from production credentials.

---

# 19. Raspberry Pi Credentials

The Raspberry Pi should use its own identity when communicating with
cloud services.

Do not reuse:

```text
ESP32 credentials
```

for:

```text
Raspberry Pi
```

Each security principal should have only the permissions it needs.

---

# 20. MQTT Security

Production MQTT communication should use:

```text
TLS
Authentication
Authorization
```

The MQTT broker must not be exposed anonymously to the public
internet.

---

# 21. MQTT Authentication

MQTT clients should authenticate before connecting.

Potential clients:

```text
Backend
Raspberry Pi
ESP32
```

Each client should have an appropriate identity.

Example:

```text
backend-service
raspberrypi-gateway-01
esp32-01
```

---

# 22. MQTT Authorization

MQTT ACLs should restrict topic access.

Example:

```text
esp32-01
    can publish:
        hydroponics/esp32-01/telemetry

    can publish:
        hydroponics/esp32-01/status

    can subscribe:
        hydroponics/esp32-01/commands
```

It should not be able to publish:

```text
hydroponics/esp32-02/telemetry
```

or subscribe to:

```text
hydroponics/esp32-02/commands
```

unless explicitly authorized.

---

# 23. MQTT Topic Security

Topics must follow the contract defined in:

```text
docs/protocols/MQTT.md
```

Topic structure should make device boundaries explicit.

Example:

```text
hydroponics/{deviceId}/telemetry
hydroponics/{deviceId}/status
hydroponics/{deviceId}/commands
hydroponics/{deviceId}/events
```

---

# 24. MQTT Message Validation

Receiving a message over MQTT does not make it trustworthy.

The backend and/or edge gateway must validate:

- Message schema
- Message version
- Device identity
- Message type
- Metric
- Unit
- Value
- Timestamp
- Message ID

Invalid messages must be rejected.

---

# 25. Command Security

Commands are security-sensitive because they can cause physical actions.

The command pipeline is:

```text
Frontend
    ↓
Backend Authentication
    ↓
Backend Authorization
    ↓
Schema Validation
    ↓
Command Creation
    ↓
MQTT Authorization
    ↓
Raspberry Pi
    ↓
ESP32 Validation
    ↓
Local Safety
    ↓
Actuator
```

Every layer should validate what it can.

---

# 26. Command Replay Protection

Commands should have unique identifiers.

Example:

```text
commandId:
    cmd-01J...
```

Commands should also support idempotency where appropriate.

The backend should prevent accidental duplicate execution caused by
network retries.

Recommended API mechanism:

```text
Idempotency-Key
```

---

# 27. Command Expiration

Commands should have a limited validity period when appropriate.

Example:

```text
Created:
    10:30:00

Expires:
    10:30:30
```

A command that arrives after its validity period may be rejected.

This is particularly important for time-sensitive physical operations.

---

# 28. Local Command Validation

The ESP32 must validate commands before execution.

Validation may include:

```text
Known actuator?
Valid command?
Valid parameters?
Allowed operating range?
Safety conditions satisfied?
Command still valid?
```

Only after validation should hardware control occur.

---

# 29. Physical Safety

Physical safety must be considered independently from cybersecurity.

Examples:

```text
Pump dry-run protection
Valve operating limits
Maximum pump runtime
Maximum valve-open duration
Low-water protection
Over-temperature protection
Sensor failure handling
Emergency shutdown
```

These rules should be implemented as close to the physical system as
practical.

---

# 30. Safety Example

Unsafe architecture:

```text
Cloud
  ↓
Pump ON
  ↓
Relay
  ↓
Pump
```

Required architecture:

```text
Cloud
  ↓
Command
  ↓
ESP32
  ↓
Safety Validation
  ↓
Relay
  ↓
Pump
```

The ESP32 remains the final authority.

---

# 31. API Security

All production API communication must use HTTPS.

Example:

```text
https://api.example.com/api/v1/...
```

Do not expose production credentials or tokens through query
parameters.

Prefer:

```text
Authorization header
```

or:

```text
Secure session cookie
```

depending on the authentication architecture.

---

# 32. API Input Validation

All externally supplied data must be validated.

Examples:

```text
deviceId
sensorId
actuatorId
metric
value
timestamp
command parameters
pagination
filters
```

Reject:

- Unexpected fields where strict validation is appropriate.
- Invalid types.
- Invalid ranges.
- Invalid identifiers.
- Oversized requests.
- Malformed JSON.

---

# 33. API Rate Limiting

Rate limiting should be applied to sensitive endpoints.

Especially:

```text
Authentication
Command creation
Emergency stop
Configuration changes
Large telemetry queries
```

Read-only endpoints may use different limits.

---

# 34. WebSocket Security

WebSocket connections must be authenticated.

Production:

```text
WSS
```

not:

```text
WS
```

The backend must ensure that a connected user receives only events
they are authorized to see.

---

# 35. WebSocket Reconnection Security

When the frontend reconnects:

```text
Authenticate
    ↓
Authorize
    ↓
Establish WebSocket
```

Do not assume that a previous WebSocket authorization remains valid
forever.

---

# 36. CORS

CORS must be explicitly configured.

Production should allow only known frontend origins.

Avoid:

```text
Access-Control-Allow-Origin: *
```

for authenticated private APIs unless the architecture specifically
requires it.

---

# 37. CSRF

If cookie-based authentication is used, protect state-changing
endpoints against CSRF.

Relevant operations include:

```text
POST commands
POST emergency-stop
POST acknowledge
POST configuration
PATCH configuration
DELETE resources
```

Use appropriate:

- SameSite cookies
- CSRF tokens
- Origin checks

depending on the authentication architecture.

---

# 38. Database Security

PostgreSQL must not be directly exposed to the public internet.

Preferred:

```text
Backend
   ↓
PostgreSQL
```

The frontend must never connect directly to PostgreSQL.

Database credentials must be stored securely.

---

# 39. Database Least Privilege

The backend database user should have only the permissions required by
the application.

Do not run the application using a PostgreSQL superuser in production.

Separate administrative access from application access.

---

# 40. Database Encryption

Production database storage should use appropriate encryption at rest
provided by the hosting environment.

Backups should also be protected.

---

# 41. Secrets Management

Secrets include:

```text
Database passwords
MQTT credentials
API secrets
JWT signing keys
Session secrets
Cloud credentials
Device credentials
TLS private keys
```

Secrets must not be committed to Git.

Use:

```text
.env
```

for local development where appropriate.

Use a proper secret manager for production.

---

# 42. Environment Files

The repository may contain:

```text
.env.example
```

It must not contain:

```text
.env
```

with real credentials.

Example files must contain placeholders only.

Bad:

```text
MQTT_PASSWORD=myRealPassword
```

Good:

```text
MQTT_PASSWORD=
```

---

# 43. Git Security

Never commit:

```text
.env
*.pem
*.key
*.p12
credentials.json
service-account.json
private keys
database dumps containing secrets
MQTT credentials
production tokens
```

The repository should include a strong `.gitignore`.

---

# 44. Secret Scanning

The project should eventually use automated secret scanning.

Examples of detection targets:

```text
API keys
Private keys
Passwords
JWT secrets
Cloud credentials
Database URLs
MQTT credentials
```

Secret scanning should run before deployment.

---

# 45. Raspberry Pi Security

The Raspberry Pi should be hardened.

Recommended:

- Use a dedicated non-root application user.
- Disable unnecessary services.
- Use SSH keys rather than password authentication where practical.
- Keep the OS patched.
- Restrict exposed ports.
- Use a firewall.
- Keep credentials out of source code.
- Use automatic security updates where appropriate.
- Minimize installed packages.

---

# 46. Raspberry Pi Network Security

The Raspberry Pi may provide the local Wi-Fi network.

The local network should use:

- Strong Wi-Fi credentials.
- WPA2/WPA3 where supported.
- No unnecessary exposed services.
- Firewall rules.
- Network isolation where practical.

The ESP32 should not have unnecessary access to the Raspberry Pi's
operating system.

---

# 47. ESP32 Security

The ESP32 firmware should:

- Avoid hard-coded production secrets.
- Validate all commands.
- Validate all sensor inputs.
- Restrict accepted commands.
- Enforce safety limits.
- Handle malformed messages safely.
- Reconnect safely after network failure.

Future production hardening may include:

- Secure boot
- Flash encryption
- Signed firmware
- OTA update authentication
- Unique device certificates/credentials

---

# 48. Firmware Updates

Firmware updates are security-sensitive.

Future OTA updates should provide:

```text
Authenticated update
        ↓
Integrity verification
        ↓
Version validation
        ↓
Optional signature verification
        ↓
Installation
```

The device should reject invalid or unauthorized firmware.

---

# 49. Dependency Security

All software dependencies should be tracked.

This includes:

```text
Backend dependencies
Frontend dependencies
Python dependencies
Raspberry Pi packages
ESP32 libraries
Docker images
System packages
```

Dependencies should be regularly updated.

Security vulnerabilities should be reviewed before production deployment.

---

# 50. Docker Security

If Docker is used:

- Do not expose unnecessary ports.
- Avoid privileged containers.
- Avoid host networking unless required.
- Avoid running applications as root where practical.
- Use pinned or controlled image versions.
- Keep images updated.
- Do not mount sensitive host directories unnecessarily.
- Do not expose Docker socket to application containers.

---

# 51. Network Exposure

Only required services should be exposed publicly.

Typical public services:

```text
HTTPS
WSS
```

Potentially:

```text
HTTP → redirect to HTTPS
```

The following should normally remain private:

```text
PostgreSQL
MQTT broker
Raspberry Pi SSH
Internal gateway services
CV services
```

---

# 52. MQTT Broker Exposure

The MQTT broker should not be publicly accessible without strong
authentication and TLS.

Preferred architecture:

```text
Raspberry Pi
      ↓
   Secure MQTT
      ↓
MQTT Broker
```

Network access should be restricted using:

- Firewall
- TLS
- Authentication
- MQTT ACLs
- Private networking where available

---

# 53. Camera Security

Cameras can contain sensitive visual information.

Camera streams and images must be treated as private data.

Do not expose raw camera streams publicly.

Access should require authorization.

Stored images should use appropriate:

- Access control
- Encryption
- Retention policy
- Secure URLs or authenticated endpoints

---

# 54. Computer Vision Security

Computer vision inputs are untrusted data.

The CV pipeline must handle:

- Malformed images
- Oversized images
- Unexpected formats
- Corrupt files
- Excessive processing workloads

Image processing must not allow arbitrary code execution through
untrusted file handling.

---

# 55. Resource Exhaustion

The platform should protect against resource exhaustion.

Potential attack vectors:

```text
Huge image uploads
Huge telemetry queries
MQTT message floods
WebSocket connection floods
Command floods
API request floods
```

Controls may include:

```text
Rate limiting
Payload limits
Query limits
Connection limits
Timeouts
Backpressure
```

---

# 56. Telemetry Integrity

Telemetry must not be blindly trusted.

The backend should validate:

```text
deviceId
sensorId
metric
unit
value
timestamp
messageId
```

Suspicious telemetry should be rejected or flagged.

---

# 57. Telemetry Confidentiality

Telemetry may contain operational information.

Production telemetry should be transmitted over authenticated encrypted
channels where possible.

Example:

```text
ESP32 → MQTT/TLS
Raspberry Pi → MQTT/TLS
Frontend → HTTPS/WSS
```

---

# 58. Telemetry Replay

Telemetry messages should include a unique message ID.

The backend should be able to detect duplicate messages where required.

Example:

```text
messageId:
    msg-001
```

Receiving the same message twice should not unintentionally create
duplicate application state.

---

# 59. Timestamp Security

Timestamps received from devices should not automatically be trusted
for security-sensitive decisions.

The backend should record:

```text
deviceTimestamp
receivedAt
```

where useful.

Server-side timestamps should be used for security auditing.

---

# 60. Audit Logging

Security-sensitive operations should be auditable.

Examples:

```text
Login
Logout
Failed login
Device access
Command creation
Command execution
Emergency stop
Configuration change
Firmware update
Permission change
```

Audit entries should include:

```text
timestamp
userId where applicable
deviceId where applicable
action
result
requestId
commandId where applicable
```

Do not store secrets in audit logs.

---

# 61. Command Audit Trail

A physical command should be traceable:

```text
User
  ↓
API Request
  ↓
requestId
  ↓
commandId
  ↓
MQTT
  ↓
ESP32
  ↓
Execution Result
  ↓
Backend
```

This is important for both security and troubleshooting.

---

# 62. Emergency Events

Safety events should be logged.

Examples:

```text
LOW_WATER
OVER_TEMPERATURE
PUMP_TIMEOUT
SENSOR_FAILURE
EMERGENCY_STOP
ACTUATOR_BLOCKED
```

The system should distinguish between:

```text
Normal operation
```

and:

```text
Safety intervention
```

---

# 63. Error Handling

Security-sensitive errors should not reveal internal implementation
details.

Avoid exposing:

```text
Database connection strings
Stack traces
Filesystem paths
MQTT credentials
Internal IP addresses
Secret configuration
```

to frontend users.

Use generic external errors and detailed internal logs.

---

# 64. Logging Security

Never log:

```text
Passwords
API keys
JWT signing secrets
Private keys
MQTT passwords
Database passwords
Session secrets
```

Be careful with:

```text
Authorization headers
Cookies
Camera URLs
Device credentials
```

Logs should be treated as sensitive operational data.

---

# 65. Dependency and Supply Chain Security

The project should eventually verify:

- Dependency provenance.
- Package versions.
- Container image provenance.
- Firmware libraries.
- Build tooling.

Avoid unnecessary dependencies.

Prefer actively maintained libraries.

---

# 66. Build Security

Production builds should be reproducible where practical.

The build pipeline should:

```text
Install dependencies
        ↓
Run tests
        ↓
Run linting
        ↓
Run security checks
        ↓
Build
        ↓
Generate artifacts
        ↓
Deploy
```

A failed security check should block production deployment when
appropriate.

---

# 67. CI/CD Security

CI/CD credentials should:

- Use least privilege.
- Be stored as protected secrets.
- Never be printed.
- Never be committed.
- Be rotated periodically.

Production deployment should require appropriate authentication and
authorization.

---

# 68. Backup Security

Backups should be:

- Encrypted.
- Access-controlled.
- Tested periodically.
- Retained according to policy.

Backups containing:

- User information
- Telemetry
- Camera metadata
- Configuration

must be protected appropriately.

---

# 69. Recovery

The system should have a documented recovery process.

Recovery targets include:

```text
Backend failure
Database failure
MQTT failure
Raspberry Pi failure
ESP32 failure
Storage failure
Credential compromise
Power failure
Network failure
```

Operational procedures belong in:

```text
docs/operations/RUNBOOK.md
```

---

# 70. Power Failure Security and Safety

Power failure is primarily a physical reliability problem, but the
system should recover safely.

After restart:

```text
ESP32 boots
    ↓
Initialize hardware
    ↓
Apply safe actuator defaults
    ↓
Validate sensors
    ↓
Connect network
    ↓
Connect MQTT
    ↓
Resume normal operation
```

Actuators should not unexpectedly enter an unsafe state during boot.

---

# 71. Boot Safety

The ESP32 should define explicit safe boot states.

For example:

```text
Pump:
    OFF

Valve:
    SAFE/CLOSED

Buzzer:
    OFF
```

unless the hardware design explicitly requires another safe state.

The exact safe state must be documented in:

```text
docs/hardware/HARDWARE.md
docs/hardware/WIRING.md
```

---

# 72. Sensor Failure Security

A failed sensor must not automatically cause unsafe behavior.

Example:

```text
Water-level sensor unavailable
        ↓
ESP32
        ↓
Cannot verify safe pump operation
        ↓
Pump remains OFF
```

The exact fail-safe behavior depends on the physical system.

---

# 73. Actuator Failure

Actuator failures should be detectable where feedback hardware exists.

Example:

```text
Pump ON
   ↓
Flow expected
   ↓
No flow detected
   ↓
Fault
   ↓
Pump OFF
   ↓
Alert
```

This may require:

- Flow sensor
- Current sensor
- Pressure sensor
- Other feedback mechanism

---

# 74. Security vs Availability

The system must balance:

```text
Security
Safety
Availability
```

For physical safety, safety takes precedence.

Example:

```text
Cloud unavailable
    ↓
Local pump protection continues
```

For administrative operations, authorization takes precedence over
convenience.

---

# 75. Threat Model

The platform should consider at least the following threats.

## Threat 1 — Unauthorized Dashboard Access

Attacker gains access to a user account.

Mitigations:

- Strong authentication
- Session security
- Authorization
- Rate limiting
- Audit logging

---

## Threat 2 — Unauthorized Device Control

Attacker attempts:

```text
Pump ON
Valve OPEN
```

Mitigations:

- Authentication
- Authorization
- Command validation
- MQTT ACLs
- ESP32 safety rules

---

## Threat 3 — MQTT Credential Theft

Attacker obtains MQTT credentials.

Mitigations:

- TLS
- Unique credentials
- ACLs
- Credential rotation
- No credentials in Git

---

## Threat 4 — Malicious MQTT Message

Attacker attempts to publish fake telemetry or commands.

Mitigations:

- Authentication
- ACLs
- Schema validation
- Device identity validation
- ESP32 command validation

---

## Threat 5 — Device Impersonation

Attacker attempts to impersonate:

```text
esp32-01
```

Mitigations:

- Unique device credentials
- TLS
- Device identity
- MQTT ACLs
- Credential rotation

---

## Threat 6 — Replay Attack

Attacker replays an old command.

Mitigations:

- Command IDs
- Timestamps
- Expiration
- Idempotency
- Device-side validation

---

## Threat 7 — Malicious Firmware

Attacker attempts to install unauthorized firmware.

Future mitigations:

- Signed firmware
- Secure boot
- Flash encryption
- Authenticated OTA

---

## Threat 8 — Raspberry Pi Compromise

An attacker compromises the edge gateway.

Mitigations:

- OS hardening
- Firewall
- SSH key authentication
- Least privilege
- Minimal installed services
- Regular patching
- Credential isolation

---

## Threat 9 — Database Compromise

Attacker obtains database access.

Mitigations:

- Private database networking
- Least privilege
- Encryption
- Strong credentials
- Backups
- Monitoring

---

## Threat 10 — Camera Data Exposure

Attacker obtains private plant/system imagery.

Mitigations:

- Authentication
- Authorization
- Encrypted transport
- Secure storage
- Retention controls

---

# 76. Security Incident Response

If credentials are compromised:

```text
Identify credential
       ↓
Revoke/disable
       ↓
Rotate credential
       ↓
Inspect logs
       ↓
Inspect affected devices
       ↓
Restore trusted state
```

For a compromised ESP32:

```text
Isolate device
       ↓
Revoke credentials
       ↓
Inspect firmware
       ↓
Reflash trusted firmware
       ↓
Provision new credentials
       ↓
Reconnect
```

---

# 77. Development Security

Development should use separate credentials from production.

Never use:

```text
Production MQTT credentials
```

or:

```text
Production database credentials
```

on a developer workstation unless explicitly required and properly
protected.

---

# 78. Local Development

Development services may use:

```text
HTTP
WS
Local MQTT
Local PostgreSQL
```

Production must use the hardened equivalents:

```text
HTTPS
WSS
Authenticated MQTT/TLS
Protected PostgreSQL
```

Development shortcuts must never silently become production defaults.

---

# 79. Security Configuration

Security-sensitive configuration must be environment-driven.

Examples:

```text
JWT_SECRET
SESSION_SECRET
DATABASE_URL
MQTT_USERNAME
MQTT_PASSWORD
MQTT_TLS
MQTT_CA
DEVICE_CREDENTIALS
```

Do not hard-code these values.

---

# 80. Security Testing

The project should eventually test:

## Authentication

```text
Valid credentials
Invalid credentials
Expired session
Revoked session
```

## Authorization

```text
Allowed device
Unauthorized device
Allowed actuator
Unauthorized actuator
```

## API

```text
Malformed requests
Oversized requests
Invalid IDs
Invalid commands
Rate limits
```

## MQTT

```text
Unauthorized publish
Unauthorized subscribe
Invalid message
Wrong device ID
Replay
```

## Firmware

```text
Invalid command
Unsafe parameter
Unknown actuator
Sensor failure
Network failure
MQTT failure
```

---

# 81. Security Testing Philosophy

Security tests should exist at multiple layers:

```text
Frontend
    ↓
API
    ↓
Backend
    ↓
MQTT
    ↓
Raspberry Pi
    ↓
ESP32
    ↓
Hardware
```

Do not rely only on frontend validation.

Do not rely only on backend validation.

Do not rely only on firmware validation.

Use defense in depth.

---

# 82. Production Security Baseline

Before production deployment, the system should have at minimum:

- HTTPS
- WSS
- Authenticated users
- Server-side authorization
- Authenticated MQTT
- MQTT ACLs
- TLS for MQTT where applicable
- Unique device credentials
- Protected PostgreSQL
- Secure secrets
- Rate limiting
- Input validation
- Audit logging
- Raspberry Pi hardening
- Safe actuator defaults
- ESP32 local safety
- Backup strategy
- Dependency updates
- Security monitoring

---

# 83. MVP Security Scope

For the first MVP, prioritize:

```text
1. No secrets committed to Git.
2. Backend validates all inputs.
3. Backend owns authorization.
4. MQTT is not publicly exposed without authentication.
5. ESP32 validates every actuator command.
6. ESP32 enforces local safety rules.
7. PostgreSQL is not publicly exposed.
8. Frontend cannot directly access MQTT.
9. Frontend cannot directly access PostgreSQL.
10. Production credentials are separated from development credentials.
```

Advanced features such as:

```text
Secure Boot
Flash Encryption
Signed OTA
Hardware security modules
Full PKI
Advanced intrusion detection
```

can be implemented later.

---

# 84. Security Priorities

The security priorities are:

## Priority 1 — Physical Safety

Prevent unsafe hardware operation.

```text
ESP32 local safety
```

## Priority 2 — Unauthorized Control

Prevent unauthorized users/devices from controlling equipment.

```text
Authentication
Authorization
MQTT ACLs
Command validation
```

## Priority 3 — Credential Protection

Protect:

```text
API secrets
MQTT credentials
Database credentials
Device credentials
```

## Priority 4 — Data Protection

Protect:

```text
Telemetry
Camera data
User data
Configuration
```

## Priority 5 — Availability

Maintain operation during:

```text
Internet failure
Cloud failure
MQTT failure
Temporary hardware failures
```

---

# 85. Security Invariants

The following rules must remain true unless explicitly changed by an
architecture decision.

### Invariant 1

The frontend is never trusted to enforce authorization.

### Invariant 2

The frontend never communicates directly with MQTT.

### Invariant 3

The frontend never communicates directly with PostgreSQL.

### Invariant 4

The backend never directly controls ESP32 GPIO.

### Invariant 5

The backend cannot bypass ESP32 local safety.

### Invariant 6

The ESP32 validates every actuator command.

### Invariant 7

Production MQTT requires authentication.

### Invariant 8

Production secrets are never committed to Git.

### Invariant 9

PostgreSQL is not publicly exposed.

### Invariant 10

Camera and AI systems cannot bypass hardware safety.

### Invariant 11

A cloud outage must not disable local safety.

### Invariant 12

An optional subsystem failure must not unnecessarily disable core
sensor monitoring.

---

# 86. Security Architecture Summary

The Hydroponics Platform uses layered security:

```text
                    USER
                     │
              Authentication
                     │
                     ▼
                  FRONTEND
                     │
                    TLS
                     │
                     ▼
                  BACKEND
                     │
             Authorization
                     │
            Input Validation
                     │
              Command Policy
                     │
                     ▼
                  MQTT
                     │
            Authentication
               + ACLs
                     │
                     ▼
              RASPBERRY PI
                     │
              Device Validation
                     │
                     ▼
                   ESP32
                     │
             Command Validation
                     │
              Local Safety
                     │
                     ▼
                 HARDWARE
```

The fundamental security model is:

```text
REMOTE REQUEST
      ↓
AUTHENTICATE
      ↓
AUTHORIZE
      ↓
VALIDATE
      ↓
TRANSPORT SECURELY
      ↓
VALIDATE AGAIN AT DEVICE
      ↓
APPLY LOCAL SAFETY
      ↓
EXECUTE PHYSICAL ACTION
```

No remote component is allowed to directly bypass the device-level
safety boundary.

The most important rule of the entire platform is:

> The cloud may request a physical action, but the device must always
> retain the authority to reject an unsafe physical action.
