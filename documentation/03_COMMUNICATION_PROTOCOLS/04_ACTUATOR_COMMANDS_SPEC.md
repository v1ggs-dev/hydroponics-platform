# Hydroponics Platform — Command Protocol

## 1. Purpose

This document defines the canonical command protocol used to control
physical devices in the Hydroponics Platform.

Commands represent requests to change the state of physical actuators
or trigger supported device actions.

The command path is:

    Web Dashboard
          ↓
    Cloud Backend
          ↓
        MQTT
          ↓
    Raspberry Pi
          ↓
        Wi-Fi
          ↓
        ESP32
          ↓
    Local Safety Validation
          ↓
    Actuator / Device
          ↓
    Actual State
          ↓
    Telemetry / Event
          ↓
    Backend
          ↓
    Dashboard

The system must distinguish between:

    COMMAND REQUESTED

and:

    COMMAND EXECUTED

A command being accepted by the backend does NOT mean that the physical
hardware successfully changed state.

---

# 2. Core Command Principle

The cloud requests an action.

The edge delivers the request.

The ESP32 decides whether the action is safe.

The hardware performs the action.

The ESP32 reports the actual resulting state.

Therefore:

    Cloud = REQUEST

    ESP32 = SAFETY AUTHORITY

    Hardware = ACTUAL STATE

---

# 3. Command Flow

Example:

    User clicks:
        Pump ON

          ↓

    Frontend

          ↓

    Backend

          ↓

    Command created:
        cmd-123

          ↓

    MQTT

          ↓

    Raspberry Pi

          ↓

    ESP32

          ↓

    Safety validation

          ↓

    Pump ON

          ↓

    ESP32 reports:
        pump-01 = ON

          ↓

    Backend

          ↓

    Dashboard

---

# 4. Command MQTT Topic

Commands are published to:

    hydroponics/{deviceId}/commands

Example:

    hydroponics/esp32-01/commands

The command topic is device-specific.

A device must not accept commands intended for another device.

---

# 5. Command Result Topic

Command execution results should be published to:

    hydroponics/{deviceId}/events

The event should reference the original:

    commandId

This allows the backend to correlate:

    Command Request
        ↓
    Command Result

---

# 6. Canonical Command Envelope

All commands use a versioned envelope.

Example:

```json
{
  "version": 1,
  "commandId": "cmd-001",
  "deviceId": "esp32-01",
  "type": "command",
  "timestamp": "2026-08-14T10:35:00.000Z",
  "action": "SET_ACTUATOR_STATE",
  "target": {
    "actuatorId": "pump-01"
  },
  "parameters": {
    "state": "ON"
  }
}