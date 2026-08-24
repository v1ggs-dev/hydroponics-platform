# Hydroponics Platform — Canonical Telemetry Schema Specification

## 1. Overview & Protocol Principles

This document defines the canonical JSON telemetry contracts emitted by the dual ESP32 microcontroller nodes (`esp32-env` and `esp32-chem`) and ingested by the Edge Gateway and Cloud Backend.

### Key Principles:
1. **Device-Specific Partitioning**: Each MCU emits an identified envelope with its logical `deviceId` (`esp32-env` or `esp32-chem`).
2. **Normalized Metrics**: Measurement objects use standardized metric keys (`air_temperature`, `humidity`, `flow_rate`, `water_volume`, `ph`, `tds`, `substrate_moisture`).
3. **Quality Flagging**: Every measurement includes a `quality` enumeration (`GOOD`, `DEGRADED`, `BAD`).

---

## 2. ESP32 Node 1 (`esp32-env`) Telemetry Envelope

Published over USB Serial and forwarded to MQTT Topic: `hydroponics/esp32-env/telemetry`

```json
{
  "deviceId": "esp32-env",
  "sequence": 412,
  "uptimeSeconds": 824,
  "freeHeap": 284192,
  "pump": "OFF",
  "autoWater": true,
  "dryRunLockout": false,
  "measurements": [
    {
      "sensorId": "dht11-01",
      "metric": "air_temperature",
      "value": 24.5,
      "unit": "C",
      "quality": "GOOD"
    },
    {
      "sensorId": "dht11-01",
      "metric": "humidity",
      "value": 68.0,
      "unit": "%",
      "quality": "GOOD"
    },
    {
      "sensorId": "flow-01",
      "metric": "flow_rate",
      "value": 2.45,
      "unit": "L/min",
      "quality": "GOOD"
    },
    {
      "sensorId": "flow-01",
      "metric": "water_volume",
      "value": 14.80,
      "unit": "L",
      "quality": "GOOD"
    }
  ]
}
```

---

## 3. ESP32 Node 2 (`esp32-chem`) Telemetry Envelope

Published over USB Serial and forwarded to MQTT Topic: `hydroponics/esp32-chem/telemetry`

```json
{
  "deviceId": "esp32-chem",
  "sequence": 412,
  "uptimeSeconds": 824,
  "freeHeap": 288416,
  "measurements": [
    {
      "sensorId": "ph-01",
      "metric": "ph",
      "value": 6.25,
      "unit": "pH",
      "quality": "GOOD"
    },
    {
      "sensorId": "tds-01",
      "metric": "tds",
      "value": 580.0,
      "unit": "ppm",
      "quality": "GOOD"
    },
    {
      "sensorId": "moisture-01",
      "metric": "substrate_moisture",
      "value": 55.4,
      "unit": "%",
      "quality": "GOOD"
    }
  ]
}
```

---

## 4. Heartbeat Schema (Emitted Every 30s)

Published to MQTT Topic: `hydroponics/{deviceId}/heartbeat`

```json
{
  "deviceId": "esp32-env",
  "firmware": "0.2.0",
  "uptimeSeconds": 824,
  "freeHeap": 284192
}
```