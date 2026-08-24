```markdown
# Hydroponics Platform — Operations Runbook

## 1. Purpose

This document defines the operational procedures for deploying,
starting, stopping, diagnosing, recovering, and maintaining the
Hydroponics Platform.

The runbook covers:

- ESP32
- Raspberry Pi 5
- Sensors
- Actuators
- MQTT
- Backend
- PostgreSQL
- Frontend
- Camera services
- Computer vision
- Networking
- Power-related failures
- Common operational incidents

The objective is to provide a predictable procedure for operating the
system without requiring the operator to understand every internal
implementation detail.

---

# 2. System Overview

The production system is:

```text
                         INTERNET
                            │
                            ▼
                    ┌───────────────┐
                    │   FRONTEND    │
                    │  Dashboard    │
                    └───────┬───────┘
                            │
                       HTTPS/WSS
                            │
                            ▼
                    ┌───────────────┐
                    │    BACKEND    │
                    └───────┬───────┘
                            │
                  ┌─────────┼─────────┐
                  │         │         │
                  ▼         ▼         ▼
             PostgreSQL   MQTT     Storage
                            │
                            ▼
                    ┌───────────────┐
                    │ Raspberry Pi  │
                    │    Gateway    │
                    └───────┬───────┘
                            │
                           Wi-Fi
                            │
                            ▼
                    ┌───────────────┐
                    │     ESP32     │
                    └───────┬───────┘
                            │
                  ┌─────────┼─────────┐
                  │         │         │
                  ▼         ▼         ▼
               Sensors   Display   Actuators
```

---

# 3. Operational Principles

The following rules apply to every operation.

## Rule 1 — Safety First

Physical safety takes precedence over software availability.

If uncertain about a pump, valve, relay, or electrical circuit:

```text
STOP THE ACTUATOR
```

and investigate before continuing.

---

## Rule 2 — Local Safety Must Continue

The ESP32 must maintain local safety behavior even when:

```text
Internet = OFFLINE
Backend = OFFLINE
MQTT = OFFLINE
Raspberry Pi = OFFLINE
```

---

## Rule 3 — Do Not Debug Multiple Layers Simultaneously

Use the dependency chain:

```text
Power
  ↓
ESP32
  ↓
Sensors
  ↓
Local Network
  ↓
Raspberry Pi
  ↓
MQTT
  ↓
Backend
  ↓
Database
  ↓
Frontend
```

Verify each layer before moving upward.

---

# 4. Service Inventory

The platform consists of these major services.

| Component | Location | Primary Responsibility |
|---|---|---|
| ESP32 firmware | ESP32 | Sensors, actuators, local safety |
| Gateway | Raspberry Pi | Edge/device communication |
| Camera service | Raspberry Pi | Camera acquisition |
| CV service | Raspberry Pi | Computer vision |
| MQTT broker | Cloud/server | Messaging |
| Backend | Cloud/server | API/business logic |
| PostgreSQL | Cloud/server | Persistent data |
| Frontend | Cloud/server | Dashboard |

Exact service names and deployment commands should be documented in
the deployment configuration.

---

# 5. Required Documentation

Before making operational changes, consult:

```text
AGENTS.md
ARCHITECTURE.md
SYSTEM.md
SECURITY.md
POWER.md
WIRING.md
PINOUT.md
HARDWARE.md
TELEMETRY.md
MQTT.md
COMMANDS.md
API.md
```

---

# 6. Initial MVP

The first operational path should be:

```text
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
Frontend
```

Do not introduce all hardware at once.

---

# 7. Pre-Startup Checklist

Before powering the system:

```text
[ ] Power supplies verified
[ ] Polarity verified
[ ] ESP32 wiring verified
[ ] Sensor wiring verified
[ ] Actuators disconnected or in safe state
[ ] Raspberry Pi power verified
[ ] Network available
[ ] MQTT available
[ ] Backend available
[ ] Database available
[ ] Frontend available
```

For a hardware prototype:

```text
[ ] No exposed dangerous electrical connections
[ ] Water separated from electronics
[ ] Pump/valve cannot unexpectedly activate
[ ] Emergency power-off available
```

---

# 8. Startup Sequence

Use this order for a normal startup.

```text
1. Verify power
2. Start Raspberry Pi
3. Start local network
4. Start Raspberry Pi gateway
5. Start camera/CV services if required
6. Start cloud infrastructure
7. Verify MQTT
8. Verify backend
9. Verify PostgreSQL
10. Power/start ESP32
11. Verify ESP32 safety state
12. Verify sensor readings
13. Verify telemetry
14. Open dashboard
15. Verify real-time updates
16. Enable actuators only after verification
```

---

# 9. ESP32 Startup

After powering the ESP32:

Verify:

```text
[ ] ESP32 boots
[ ] No continuous reset loop
[ ] Safe actuator state established
[ ] Sensors initialize
[ ] Wi-Fi connects
[ ] MQTT connects
[ ] Telemetry starts
[ ] Heartbeat/status appears
```

The first check should be the serial console during development.

---

# 10. ESP32 Safe Boot

Immediately after boot, the firmware should establish safe outputs.

Expected example:

```text
Pump:
    OFF

Valve:
    SAFE/CLOSED

Buzzer:
    OFF
```

The actual state depends on the hardware design.

Never assume that a relay's default state is safe.

---

# 11. Raspberry Pi Startup

After boot:

```text
Check OS
  ↓
Check network
  ↓
Check Wi-Fi AP if used
  ↓
Check gateway service
  ↓
Check MQTT connectivity
  ↓
Check camera service
  ↓
Check CV service
```

The gateway should be able to communicate with the ESP32 before
attempting to diagnose cloud problems.

---

# 12. Raspberry Pi Health Checks

Check:

```text
CPU
Memory
Disk
Temperature
Network
Wi-Fi
MQTT
Gateway
Camera
```

Example commands:

```bash
hostname
uptime
free -h
df -h
ip addr
ip route
```

For systemd-based services:

```bash
systemctl --failed
systemctl status <service>
```

Use the actual service names configured by the project.

---

# 13. Network Verification

Verify the Raspberry Pi has an IP address:

```bash
ip addr
```

Verify routing:

```bash
ip route
```

Verify connectivity:

```bash
ping -c 4 <gateway>
```

If internet connectivity is expected:

```bash
ping -c 4 1.1.1.1
```

If DNS is required:

```bash
getent hosts example.com
```

Do not use internet connectivity as proof that the ESP32-to-Pi network
is functioning.

---

# 14. ESP32 Network Verification

The ESP32 should report:

```text
Wi-Fi connected
IP address
Signal strength
Gateway
MQTT connection
```

If the ESP32 cannot connect:

```text
Check:
    SSID
    Password
    Wi-Fi availability
    Raspberry Pi AP
    DHCP
    Signal strength
```

---

# 15. MQTT Verification

The MQTT path is:

```text
ESP32
  ↓
Raspberry Pi
  ↓
MQTT
  ↓
Backend
```

Verify the broker is reachable.

If using a command-line MQTT client:

```bash
mosquitto_pub
mosquitto_sub
```

Use the project's configured credentials and topics.

Do not paste production credentials into shell history or documentation.

---

# 16. MQTT Topic Verification

Expected topic structure is defined in:

```text
docs/protocols/MQTT.md
```

Typical topics include:

```text
hydroponics/{deviceId}/telemetry
hydroponics/{deviceId}/status
hydroponics/{deviceId}/commands
hydroponics/{deviceId}/events
```

Do not invent alternate topics during troubleshooting.

---

# 17. Telemetry Verification

The complete telemetry path is:

```text
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
API/WebSocket
  ↓
Frontend
```

Verify in this order:

```text
1. Sensor value exists on ESP32
2. ESP32 publishes telemetry
3. Raspberry Pi receives it
4. MQTT broker receives it
5. Backend receives it
6. Database stores it
7. API returns it
8. WebSocket broadcasts it
9. Dashboard displays it
```

---

# 18. DHT11 Verification

Expected output:

```text
Temperature: <value> °C
Humidity: <value> %
```

Check for:

```text
NaN
0 values
Impossible values
Repeated identical readings
Sensor timeout
```

If the DHT11 fails:

```text
Check power
Check GND
Check DATA GPIO
Check pull-up
Check sensor module
Check firmware configuration
```

---

# 19. Sensor Failure Handling

If a sensor fails:

```text
Sensor
  ↓
Invalid reading
  ↓
ESP32
  ↓
Sensor ERROR
```

Do not treat invalid values as real measurements.

Example:

```text
NaN
```

must not become:

```text
Temperature = 0°C
```

unless explicitly defined by the data contract.

---

# 20. Dashboard Verification

After telemetry is confirmed:

```text
Open dashboard
      ↓
Verify authentication
      ↓
Verify device appears
      ↓
Verify current readings
      ↓
Verify timestamps
      ↓
Verify device status
      ↓
Verify real-time updates
```

Check that the displayed value matches the ESP32 reading.

---

# 21. WebSocket Verification

A real-time dashboard should show new telemetry without a manual refresh.

Test:

```text
ESP32
  ↓
New measurement
  ↓
Backend
  ↓
WebSocket
  ↓
Dashboard
```

If the dashboard updates only after refreshing:

```text
Check:
    WebSocket connection
    Authentication
    Backend event publishing
    Frontend event handling
```

---

# 22. Database Verification

Telemetry should be persisted.

Verify:

```text
Latest reading exists
Timestamp exists
Device ID is correct
Sensor ID is correct
Metric is correct
Unit is correct
```

Do not modify database records manually unless required for an
incident.

---

# 23. Backend Health

Check:

```text
API availability
Database connectivity
MQTT connectivity
WebSocket
Authentication
Error logs
```

Typical API health endpoint:

```text
GET /health
```

or:

```text
GET /api/v1/health
```

The actual endpoint is defined by the backend implementation.

---

# 24. Backend Logs

When troubleshooting:

```text
Check:
    startup errors
    database errors
    MQTT errors
    authentication errors
    authorization failures
    validation errors
    WebSocket errors
```

Use structured logs where available.

Never expose or paste secrets from logs.

---

# 25. PostgreSQL Health

Verify:

```text
Database process
Database connectivity
Connection pool
Disk space
Recent errors
```

Check system resources:

```bash
df -h
free -h
```

If PostgreSQL is containerized:

```bash
docker compose ps
docker compose logs <postgres-service>
```

Use the actual service name from the project's Compose file.

---

# 26. Frontend Failure

If the dashboard is unavailable:

```text
Check:
    Frontend service
    Reverse proxy
    DNS
    HTTPS
    Backend URL
```

Then verify backend independently.

Do not assume that a frontend failure means the hardware system is
offline.

---

# 27. Backend Failure

If the frontend loads but shows no data:

```text
Check:
    Backend
    Database
    MQTT
```

The correct troubleshooting path is:

```text
Frontend
   ↓
Backend
   ↓
MQTT
   ↓
Raspberry Pi
   ↓
ESP32
```

---

# 28. Database Failure

If telemetry reaches the backend but is not persisted:

```text
Check:
    PostgreSQL status
    Database connectivity
    Credentials
    Connection pool
    Disk space
    Database logs
```

Do not delete or recreate the database during an incident without
first determining whether data recovery is required.

---

# 29. MQTT Failure

Symptoms:

```text
ESP32 online
Raspberry Pi online
Backend online
No telemetry
```

Check:

```text
MQTT broker
MQTT credentials
MQTT ACLs
Network connectivity
TLS
Topic names
Subscriptions
```

---

# 30. Raspberry Pi Gateway Failure

Symptoms:

```text
ESP32 connected to Wi-Fi
No data reaches cloud
```

Check:

```text
Gateway process
Wi-Fi
MQTT client
Gateway logs
CPU
Memory
Disk
```

Restart only the gateway service if possible.

Avoid rebooting the entire Raspberry Pi unless necessary.

---

# 31. ESP32 Offline

Symptoms:

```text
Dashboard:
    Device OFFLINE
```

Troubleshooting:

```text
1. Check power.
2. Check USB/power cable.
3. Check serial output.
4. Check Wi-Fi.
5. Check Raspberry Pi AP.
6. Check firmware.
7. Check MQTT.
```

---

# 32. ESP32 Continuous Reset

Possible causes:

```text
Power instability
Brownout
Firmware crash
Watchdog
Memory issue
Peripheral fault
Short circuit
```

Procedure:

```text
1. Disconnect actuators.
2. Disconnect nonessential peripherals.
3. Power ESP32.
4. Observe serial output.
5. Check voltage.
6. Reconnect components one at a time.
```

If the reset disappears after removing an actuator:

```text
Investigate the actuator power architecture.
```

Do not hide a brownout by simply disabling the ESP32 brownout
detector.

---

# 33. ESP32 Wi-Fi Failure

Check:

```text
SSID
Password
Wi-Fi AP
Signal strength
DHCP
IP address
Firmware configuration
```

If using Raspberry Pi as the AP:

```text
ESP32
  ↓
Check SSID
  ↓
Raspberry Pi Wi-Fi AP
```

Verify the AP is actually running.

---

# 34. Raspberry Pi AP Failure

If the Pi provides the local Wi-Fi:

```text
Check:
    Wi-Fi interface
    AP service
    DHCP service
    IP forwarding where required
    Firewall
```

Verify that the ESP32 can see the SSID.

---

# 35. Internet Failure

If the local network is operational but internet connectivity is lost:

```text
ESP32
  ↓
Raspberry Pi
  ↓
Local operation continues
```

The expected behavior is:

```text
Local sensor acquisition
    ✓

Local safety
    ✓

Local actuator protection
    ✓

Cloud telemetry
    unavailable

Remote dashboard
    unavailable
```

The Raspberry Pi may buffer telemetry if implemented.

---

# 36. Offline Buffering

When cloud connectivity returns:

```text
Local Buffer
    ↓
MQTT
    ↓
Backend
    ↓
Database
```

Original measurement timestamps should be preserved.

Verify that replayed telemetry does not create duplicates.

---

# 37. Actuator Control Procedure

Do not test pumps/valves directly from the cloud during initial
bring-up.

Use this order:

```text
ESP32
  ↓
Driver
  ↓
No-load test
  ↓
Safe test load
  ↓
Actual actuator
```

Only then test:

```text
Dashboard
  ↓
Backend
  ↓
MQTT
  ↓
ESP32
  ↓
Actuator
```

---

# 38. Pump Test

Before activating the pump:

```text
[ ] Correct voltage
[ ] Correct polarity
[ ] Driver correctly wired
[ ] Protection installed
[ ] Water available
[ ] Tubing correctly connected
[ ] Pump cannot run dry
[ ] Emergency power-off available
```

Test:

```text
OFF
  ↓
ON briefly
  ↓
Observe
  ↓
OFF
```

Do not immediately run the pump indefinitely.

---

# 39. Pump Does Not Start

Check:

```text
Power supply
Pump voltage
Pump current
Relay/MOSFET
GPIO state
Driver wiring
Ground
Protection
Mechanical blockage
```

Measure the actuator supply rather than assuming it is present.

---

# 40. Pump Causes ESP32 Reset

Immediately:

```text
Pump OFF
```

Then investigate:

```text
Shared power rail
Voltage drop
Grounding
Startup current
EMI
Transient suppression
Relay/MOSFET
DC/DC converter
```

Do not continue repeatedly cycling the pump while the cause is unknown.

---

# 41. Pump Does Not Stop

Immediate response:

```text
Remove actuator power if necessary.
```

Then investigate:

```text
Relay stuck
MOSFET failed
GPIO state
Active-low logic
Firmware command loop
Driver failure
```

A pump that cannot be reliably switched OFF must not remain in production
operation.

---

# 42. Valve Test

Before testing:

```text
[ ] Correct valve voltage
[ ] Correct valve polarity
[ ] Correct driver
[ ] Correct default state
[ ] Correct water pressure
[ ] Maximum open duration configured
[ ] Safe shutdown verified
```

Test with a short activation.

---

# 43. Valve Does Not Close

Immediately stop the water source if required.

Then check:

```text
Valve type
Valve supply
Driver state
GPIO state
Mechanical obstruction
Firmware state
```

Never rely solely on the software command if physical water flow
continues.

---

# 44. Flow Sensor Verification

When the pump runs:

```text
Pump ON
   ↓
Water Flow
   ↓
Flow Sensor
   ↓
ESP32
```

Verify:

```text
Flow > expected minimum
```

If:

```text
Pump ON
Flow = 0
```

investigate:

```text
Pump
Tubing
Valve
Flow sensor
Sensor wiring
Water level
```

---

# 45. Closed-Loop Pump Protection

Future implementation:

```text
Pump ON
   ↓
Wait for flow
   ↓
Flow detected?
   │
 ┌─┴─┐
YES  NO
 │    │
 │    ▼
 │  Timeout
 │    ↓
 │  Pump OFF
 │    ↓
 │  Alert
 │
 ▼
Normal Operation
```

This should be implemented locally on the ESP32 where practical.

---

# 46. pH Sensor Troubleshooting

If pH readings are unstable:

```text
Check:
    Sensor interface
    Power noise
    Grounding
    Pump state
    Cable routing
    Probe condition
    Calibration
```

First test with the pump OFF.

If the reading becomes stable:

```text
Investigate actuator-induced electrical noise.
```

---

# 47. TDS Sensor Troubleshooting

If TDS/EC readings are unstable:

```text
Check:
    Probe
    Interface board
    Supply
    Ground
    Calibration
    Water conditions
    Pump noise
    Electrical interference
```

Avoid assuming that unstable readings are purely software problems.

---

# 48. Camera Failure

If the camera is unavailable:

```text
Check:
    Camera power
    Cable
    USB/CSI connection
    Device detection
    Camera service
    Permissions
    Storage
```

Core telemetry should continue independently.

---

# 49. Computer Vision Failure

If CV fails:

```text
Camera
    ✓

Telemetry
    ✓

CV
    ✗
```

The system should remain operational.

Restart the CV service rather than the entire gateway if possible.

---

# 50. Camera Storage Failure

Check:

```text
df -h
```

If storage is full:

```text
Stop unnecessary image capture
Rotate/delete according to retention policy
Investigate storage growth
```

Do not blindly delete all historical images.

---

# 51. High CPU Usage on Raspberry Pi

Check:

```text
top
```

or:

```bash
htop
```

Identify:

```text
Gateway
Camera
CV
Other processes
```

If CV consumes excessive CPU:

```text
Reduce inference frequency
Reduce image resolution
Use hardware acceleration where appropriate
Restart affected service
```

Do not disable the gateway or safety-critical services just to make
the CPU graph look normal.

---

# 52. High Memory Usage

Check:

```bash
free -h
```

Then identify the process:

```bash
top
```

Potential causes:

```text
Memory leak
CV model
Camera buffering
Gateway issue
Container issue
```

Restart the affected non-critical service if appropriate.

---

# 53. Disk Full

Check:

```bash
df -h
```

Then:

```bash
du -sh <directory>
```

Potential causes:

```text
Logs
Images
CV outputs
Docker layers
Temporary files
Database growth
```

Do not delete database files manually.

---

# 54. Raspberry Pi Overheating

Check:

```bash
vcgencmd measure_temp
```

if available on the installed Raspberry Pi OS environment.

Investigate:

```text
Cooling
Enclosure airflow
CPU load
CV workload
Power supply
Ambient temperature
```

Reduce workload if required.

---

# 55. Power Failure Recovery

After power restoration:

```text
1. Verify power supply.
2. Verify Raspberry Pi boot.
3. Verify ESP32 boot.
4. Verify safe actuator state.
5. Verify network.
6. Verify MQTT.
7. Verify backend.
8. Verify telemetry.
9. Verify actuator state.
```

Do not assume actuators returned to their previous state safely.

---

# 56. Emergency Shutdown

If an unsafe condition occurs:

```text
1. Stop actuator operation.
2. Disconnect actuator power if necessary.
3. Keep logic power if safe.
4. Preserve logs.
5. Identify failure.
6. Do not restart actuator automatically.
7. Fix root cause.
8. Perform controlled restart.
```

Examples:

```text
Uncontrolled pump
Uncontrolled valve
Electrical overheating
Water leak
Smoke
Burning smell
Unexpected actuator behavior
```

---

# 57. Water Leak Response

If water reaches electrical equipment:

```text
1. Do not touch exposed electrical equipment.
2. Disconnect power using a safe upstream method.
3. Stop water source if safely possible.
4. Isolate affected hardware.
5. Inspect for damage.
6. Dry and inspect before re-energizing.
```

Do not power wet electronics merely to determine whether they still
work.

---

# 58. Electrical Fault Response

If there is:

```text
Smoke
Burning smell
Sparking
Excessive heat
Repeated fuse failure
```

immediately:

```text
Power OFF
```

Do not repeatedly reset the system.

Investigate the electrical cause before re-energizing.

---

# 59. Security Incident

If unauthorized activity is suspected:

```text
1. Disable affected credentials.
2. Stop remote actuator commands if necessary.
3. Isolate affected device.
4. Preserve logs.
5. Inspect MQTT activity.
6. Inspect backend audit logs.
7. Rotate credentials.
8. Reflash compromised ESP32 if necessary.
9. Restore trusted configuration.
```

See:

```text
docs/SECURITY.md
```

for security architecture.

---

# 60. Compromised ESP32

If an ESP32 is suspected to be compromised:

```text
1. Disconnect device from network.
2. Revoke its credentials.
3. Preserve relevant logs.
4. Inspect firmware.
5. Flash trusted firmware.
6. Provision new credentials.
7. Verify hardware safety.
8. Reconnect.
```

Never simply reconnect a compromised device with the same credentials.

---

# 61. Compromised Raspberry Pi

If the Raspberry Pi is suspected to be compromised:

```text
1. Isolate it from the network.
2. Stop physical actuator access if required.
3. Preserve logs/images where appropriate.
4. Revoke gateway credentials.
5. Inspect system.
6. Reinstall from a trusted image if necessary.
7. Patch the system.
8. Restore configuration from trusted sources.
9. Provision new credentials.
10. Reconnect.
```

Do not trust an obviously compromised operating system merely because
its services appear normal.

---

# 62. Credential Rotation

Rotate credentials when:

```text
Credential leaked
Device compromised
Employee/team member loses access
Production environment changes
Security incident occurs
```

After rotation:

```text
Old credential
    ↓
Revoked

New credential
    ↓
Provisioned
```

Verify connectivity after rotation.

---

# 63. Deployment Procedure

Before deployment:

```text
[ ] Tests pass
[ ] Security checks pass
[ ] Environment variables configured
[ ] Database migrations reviewed
[ ] MQTT configuration reviewed
[ ] TLS configured
[ ] Backup available
[ ] Rollback plan available
```

Then:

```text
Build
  ↓
Deploy
  ↓
Health check
  ↓
Database migration if required
  ↓
MQTT check
  ↓
Telemetry check
  ↓
Dashboard check
```

---

# 64. Database Migration

Before applying a production migration:

```text
1. Confirm backup.
2. Review migration.
3. Test migration.
4. Check expected downtime.
5. Apply migration.
6. Verify schema.
7. Verify backend.
8. Verify telemetry.
```

Do not manually modify production schema unless the change is
controlled and documented.

---

# 65. Rollback

If a deployment fails:

```text
1. Stop rollout.
2. Determine failure scope.
3. Restore previous application version if appropriate.
4. Preserve logs.
5. Verify database compatibility.
6. Verify MQTT compatibility.
7. Verify telemetry.
8. Verify frontend.
```

Do not blindly roll back a database migration that has already changed
persistent data.

---

# 66. Firmware Deployment

Before flashing:

```text
[ ] Correct device
[ ] Correct firmware version
[ ] Correct environment
[ ] Safe actuator state
[ ] Backup configuration
[ ] Device connected
```

After flashing:

```text
[ ] Device boots
[ ] Safe outputs
[ ] Sensors work
[ ] Wi-Fi works
[ ] MQTT works
[ ] Telemetry works
[ ] Commands work
```

---

# 67. Firmware Rollback

If new firmware causes instability:

```text
1. Disconnect actuators if necessary.
2. Flash previous known-good firmware.
3. Verify sensor operation.
4. Verify network.
5. Verify safety.
6. Investigate new firmware separately.
```

Never test unstable firmware with uncontrolled pumps or valves.

---

# 68. Configuration Changes

Configuration changes should be:

```text
Documented
Version controlled where appropriate
Validated
Tested
Reversible
```

Examples:

```text
Sensor interval
MQTT topic
Device ID
Actuator limits
Safety thresholds
Camera settings
CV inference frequency
```

Safety-critical configuration requires extra validation.

---

# 69. Sensor Calibration

When a sensor requires calibration:

```text
1. Stop affected automation.
2. Put relevant actuator in safe state.
3. Follow sensor manufacturer's calibration procedure.
4. Record calibration values.
5. Verify reading.
6. Restore automation.
```

Do not calibrate a sensor while unrelated automation can cause unsafe
physical behavior.

---

# 70. Maintenance Schedule

The following maintenance should eventually be scheduled.

## Daily / Before Operation

```text
Check dashboard
Check device status
Check sensor readings
Check alerts
Check water level
Check pump/valve behavior
Check visible leaks
```

---

## Weekly

```text
Review logs
Review device uptime
Review sensor errors
Review actuator events
Check camera
Check storage
Check Raspberry Pi health
```

---

## Monthly

```text
Review dependencies
Review security events
Review backups
Check credentials
Inspect wiring
Inspect connectors
Inspect power supplies
Inspect pump/valve
```

Exact maintenance intervals should be adapted to the physical
installation and manufacturer requirements.

---

# 71. Health Dashboard

The production dashboard should eventually show:

```text
System
    ONLINE / OFFLINE

Raspberry Pi
    ONLINE / OFFLINE

ESP32
    ONLINE / OFFLINE

MQTT
    HEALTHY / ERROR

Backend
    HEALTHY / ERROR

Database
    HEALTHY / ERROR

Sensors
    HEALTHY / ERROR

Actuators
    SAFE / ACTIVE / ERROR

Camera
    ONLINE / OFFLINE

Computer Vision
    HEALTHY / ERROR
```

---

# 72. Useful Metrics

Track:

```text
Device uptime
Last heartbeat
Last telemetry
Telemetry rate
MQTT connection state
Command success rate
Command failure rate
API latency
WebSocket connections
Database latency
Raspberry Pi CPU
Raspberry Pi memory
Raspberry Pi temperature
Disk usage
Camera FPS
CV inference time
```

---

# 73. Logs

Important logs include:

```text
ESP32
    Sensor errors
    Wi-Fi
    MQTT
    Safety events
    Actuator events

Raspberry Pi
    Gateway
    Network
    MQTT
    Camera
    CV

Backend
    API
    Authentication
    Authorization
    MQTT
    Database
    Commands

Frontend
    API errors
    WebSocket errors
```

Never include secrets in logs.

---

# 74. Incident Classification

Use the following severity levels.

## SEV-1 — Physical Safety

Examples:

```text
Uncontrolled pump
Uncontrolled valve
Electrical hazard
Water contacting dangerous electrical equipment
Smoke / fire risk
```

Action:

```text
Immediately stop affected hardware.
```

---

## SEV-2 — System Critical

Examples:

```text
ESP32 unavailable
Raspberry Pi unavailable
MQTT unavailable
Backend unavailable
Database unavailable
```

Action:

```text
Restore core monitoring/control path.
```

---

## SEV-3 — Degraded

Examples:

```text
One sensor unavailable
Camera unavailable
CV unavailable
Dashboard visualization issue
```

Action:

```text
Core system may continue while issue is investigated.
```

---

## SEV-4 — Cosmetic / Non-Critical

Examples:

```text
Chart formatting
UI issue
Non-critical logging issue
```

Action:

```text
Fix during normal development cycle.
```

---

# 75. Incident Response Template

For every significant incident record:

```text
Incident ID:
Date:
Time:
Severity:
Affected Component:
Detected By:

Symptoms:

Immediate Action:

Root Cause:

Resolution:

Data Loss:

Physical Impact:

Security Impact:

Preventive Action:

Follow-up:
```

---

# 76. Troubleshooting Decision Tree

Use this decision tree:

```text
Is the system powered?
        │
      NO
        │
        ▼
   Fix power
        │
       YES
        ▼
Is ESP32 online?
        │
      NO
        │
        ▼
Check ESP32
        │
       YES
        ▼
Is sensor data valid?
        │
      NO
        │
        ▼
Check sensor
        │
       YES
        ▼
Is Raspberry Pi online?
        │
      NO
        │
        ▼
Check Pi
        │
       YES
        ▼
Is MQTT working?
        │
      NO
        │
        ▼
Check broker/network
        │
       YES
        ▼
Is backend receiving data?
        │
      NO
        │
        ▼
Check backend/MQTT
        │
       YES
        ▼
Is database storing data?
        │
      NO
        │
        ▼
Check PostgreSQL
        │
       YES
        ▼
Is dashboard updating?
        │
      NO
        │
        ▼
Check API/WebSocket
        │
       YES
        ▼
SYSTEM HEALTHY
```

---

# 77. Telemetry Incident Checklist

If telemetry stops:

```text
[ ] ESP32 powered
[ ] ESP32 sensor reading valid
[ ] ESP32 Wi-Fi connected
[ ] Raspberry Pi online
[ ] Raspberry Pi gateway running
[ ] MQTT broker reachable
[ ] MQTT credentials valid
[ ] MQTT topic correct
[ ] Backend connected to MQTT
[ ] Backend validation succeeds
[ ] PostgreSQL available
[ ] WebSocket connected
[ ] Frontend receiving events
```

---

# 78. Command Incident Checklist

If actuator control fails:

```text
[ ] User authenticated
[ ] User authorized
[ ] Device authorized
[ ] Actuator authorized
[ ] API accepted command
[ ] Command created
[ ] MQTT published
[ ] Raspberry Pi received command
[ ] ESP32 received command
[ ] Command validated
[ ] Local safety passed
[ ] Driver activated
[ ] Actuator physically operated
[ ] Actual state reported
```

---

# 79. If the Command Is Blocked

If the dashboard reports:

```text
Command BLOCKED
```

check the ESP32 safety reason.

Possible causes:

```text
LOW_WATER
SENSOR_FAILURE
MAX_RUNTIME
INVALID_COMMAND
STALE_COMMAND
ACTUATOR_LOCKED
EMERGENCY_STOP
OTHER_SAFETY_RULE
```

Do not override the safety rule remotely.

Fix the underlying condition.

---

# 80. If Dashboard Says ON but Hardware Is OFF

Distinguish:

```text
Requested State
```

from:

```text
Actual State
```

Check:

```text
Command result
ESP32 state
Driver state
Physical actuator
Feedback sensor
```

If no feedback sensor exists, the dashboard must not falsely imply that
physical operation has been verified.

---

# 81. If Dashboard Says OFF but Hardware Is ON

Treat this as a potentially serious physical fault.

Immediately:

```text
Stop actuator power if necessary.
```

Then inspect:

```text
Relay
MOSFET
GPIO
Firmware
Command queue
Electrical wiring
```

Do not rely on the dashboard's displayed state until physical state is
verified.

---

# 82. Safe Recovery Philosophy

When recovery is uncertain:

```text
Hardware
    ↓
Safe state
    ↓
Communication
    ↓
Monitoring
    ↓
Automation
```

Do not restore automation before confirming:

```text
Sensors
Power
Communication
Safety
```

---

# 83. Full Recovery Procedure

After a serious failure:

```text
1. Put physical system in safe state.
2. Disconnect or disable actuators.
3. Inspect hardware.
4. Verify power.
5. Boot Raspberry Pi.
6. Verify local network.
7. Boot ESP32.
8. Verify local safety.
9. Verify sensors.
10. Verify MQTT.
11. Verify backend.
12. Verify database.
13. Verify frontend.
14. Verify telemetry.
15. Verify command path without actual actuator.
16. Test actuator briefly.
17. Verify feedback.
18. Resume normal operation.
```

---

# 84. Backup and Restore

Back up at minimum:

```text
Database
Application configuration
MQTT configuration
Device configuration
Deployment configuration
Important camera/CV metadata
```

Do not assume that source code alone is sufficient to restore the
system.

---

# 85. Restore Verification

After restoring:

```text
[ ] Backend starts
[ ] Database starts
[ ] MQTT starts
[ ] Raspberry Pi gateway connects
[ ] ESP32 connects
[ ] Telemetry arrives
[ ] Historical data accessible
[ ] Dashboard works
[ ] Commands work
[ ] Safety rules work
```

---

# 86. Production Deployment Checklist

Before declaring production ready:

```text
SECURITY
[ ] HTTPS
[ ] WSS
[ ] Authentication
[ ] Authorization
[ ] MQTT authentication
[ ] MQTT ACLs
[ ] Secrets protected
[ ] Database protected
[ ] Rate limiting
[ ] Audit logging

HARDWARE
[ ] Safe actuator defaults
[ ] Correct power
[ ] Correct wiring
[ ] Protection
[ ] Water isolation
[ ] Emergency shutdown

SOFTWARE
[ ] Backend healthy
[ ] Database healthy
[ ] MQTT healthy
[ ] Frontend healthy
[ ] Gateway healthy
[ ] Firmware verified

MONITORING
[ ] Device heartbeat
[ ] Telemetry monitoring
[ ] Error logging
[ ] Storage monitoring
[ ] Backup
```

---

# 87. Shutdown Procedure

For a planned shutdown:

```text
1. Stop automation.
2. Turn actuators OFF.
3. Verify actual actuator state.
4. Stop camera/CV services.
5. Stop Raspberry Pi gateway.
6. Stop cloud services if required.
7. Power down Raspberry Pi.
8. Power down ESP32.
9. Disconnect main power if required.
```

Do not shut down the Raspberry Pi while the pump is running unless the
hardware has an independent safe shutdown mechanism.

---

# 88. Maintenance Shutdown

Before hardware maintenance:

```text
1. Stop all automation.
2. Disable remote commands.
3. Turn actuators OFF.
4. Verify physical state.
5. Disconnect actuator power.
6. Disconnect logic power if required.
7. Perform maintenance.
8. Inspect wiring.
9. Restore power.
10. Perform startup checklist.
```

---

# 89. Development Shutdown

For development:

```text
Stop:
    Frontend
    Backend
    MQTT
    Database
```

The exact commands depend on the development environment.

Do not stop the Raspberry Pi gateway while an actuator is operating.

---

# 90. Known-Good State

Maintain a known-good configuration containing:

```text
Firmware version
Backend version
Frontend version
Database schema version
MQTT configuration
Gateway version
Hardware revision
Pinout revision
```

This allows rapid rollback.

---

# 91. Version Compatibility

The following components must remain protocol-compatible:

```text
ESP32 firmware
Raspberry Pi gateway
MQTT broker
Backend
Frontend
```

Protocol changes should update:

```text
docs/protocols/MQTT.md
docs/protocols/TELEMETRY.md
docs/protocols/COMMANDS.md
docs/protocols/API.md
```

where applicable.

---

# 92. Change Management

Before changing a core component:

```text
1. Identify affected layers.
2. Update documentation.
3. Test locally.
4. Test hardware.
5. Test telemetry.
6. Test commands.
7. Test failure behavior.
8. Deploy.
9. Monitor.
```

---

# 93. Hardware Replacement

When replacing a sensor:

```text
1. Verify electrical compatibility.
2. Update HARDWARE.md.
3. Update PINOUT.md if required.
4. Update WIRING.md.
5. Update POWER.md if required.
6. Update firmware.
7. Test sensor.
8. Test telemetry.
9. Update dashboard configuration.
```

---

# 94. ESP32 Replacement

When replacing an ESP32:

```text
1. Record old device ID.
2. Provision new device ID.
3. Configure credentials.
4. Flash firmware.
5. Verify hardware.
6. Verify Wi-Fi.
7. Verify MQTT.
8. Verify telemetry.
9. Verify command handling.
10. Retire old credentials.
```

---

# 95. Raspberry Pi Replacement

When replacing the Pi:

```text
1. Install supported OS.
2. Apply updates.
3. Configure network/AP.
4. Install gateway.
5. Configure MQTT.
6. Configure camera/CV.
7. Provision credentials.
8. Test ESP32 connection.
9. Test cloud connectivity.
10. Verify telemetry.
```

---

# 96. Incident Priority

When multiple issues occur, prioritize:

```text
1. Physical safety
2. Electrical safety
3. Water damage
4. Unauthorized actuator control
5. Device connectivity
6. Telemetry
7. Database
8. Dashboard
9. Camera/CV
10. Cosmetic UI
```

---

# 97. MVP Operational Scope

The first operational MVP should support:

```text
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
Frontend
```

Operational checks should focus on:

```text
Temperature
Humidity
Device status
Last update
Connectivity
```

---

# 98. Future Operational Scope

Future runbook procedures will be added for:

```text
pH calibration
TDS/EC calibration
Flow calibration
Pump maintenance
Valve maintenance
Nutrient dosing
Water-level automation
Camera maintenance
AI model deployment
OTA firmware updates
Multi-device management
Multi-system deployments
```

---

# 99. Runbook Invariants

The following rules must always remain true.

### Invariant 1

Never operate an actuator whose safety state is unknown.

### Invariant 2

Never bypass local ESP32 safety to restore functionality.

### Invariant 3

Never expose production secrets during troubleshooting.

### Invariant 4

Never assume dashboard state equals physical state.

### Invariant 5

Verify actual actuator state after every significant recovery.

### Invariant 6

Do not debug multiple independent layers simultaneously.

### Invariant 7

Do not repeatedly power-cycle a system with an unresolved electrical
fault.

### Invariant 8

Do not expose PostgreSQL directly to the public internet.

### Invariant 9

Do not expose MQTT anonymously to the public internet.

### Invariant 10

Do not reconnect a potentially compromised device using unchanged
credentials.

### Invariant 11

Do not treat invalid sensor values as valid measurements.

### Invariant 12

Do not allow optional camera/CV failures to disable core monitoring.

---

# 100. Quick Recovery Reference

## System completely offline

```text
Power
  ↓
Raspberry Pi
  ↓
ESP32
  ↓
Network
  ↓
MQTT
  ↓
Backend
  ↓
Database
  ↓
Frontend
```

---

## Telemetry missing

```text
ESP32
  ↓
Sensor
  ↓
Wi-Fi
  ↓
Raspberry Pi
  ↓
MQTT
  ↓
Backend
  ↓
Database
```

---

## Dashboard stale

```text
Backend
  ↓
WebSocket
  ↓
Frontend
```

---

## Actuator not responding

```text
API
  ↓
Command
  ↓
MQTT
  ↓
Raspberry Pi
  ↓
ESP32
  ↓
Safety
  ↓
Driver
  ↓
Actuator
```

---

## Physical actuator behaving unexpectedly

```text
STOP ACTUATOR
      ↓
REMOVE ACTUATOR POWER IF SAFE
      ↓
VERIFY HARDWARE
      ↓
VERIFY DRIVER
      ↓
VERIFY ESP32
      ↓
VERIFY COMMAND PATH
      ↓
ONLY THEN RESTORE OPERATION
```

---

# 101. Final Operational Model

The Hydroponics Platform should be operated according to:

```text
              OBSERVE
                 │
                 ▼
              VERIFY
                 │
                 ▼
               ACT
                 │
                 ▼
             MEASURE
                 │
                 ▼
              VERIFY
                 │
                 ▼
              RECORD
```

For physical control:

```text
REQUEST
   ↓
AUTHORIZE
   ↓
VALIDATE
   ↓
EXECUTE
   ↓
VERIFY ACTUAL STATE
   ↓
RECORD RESULT
```

For failures:

```text
DETECT
   ↓
MAKE SAFE
   ↓
ISOLATE
   ↓
DIAGNOSE
   ↓
REPAIR
   ↓
VERIFY
   ↓
RESTORE
   ↓
MONITOR
```

The system is considered operational only when both software state and
physical state have been verified.

The fundamental operating principle is:

> Never restore automation before restoring safety, connectivity,
> telemetry, and verified physical state.
```