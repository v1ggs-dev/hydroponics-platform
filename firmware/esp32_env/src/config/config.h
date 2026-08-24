#pragma once

// =============================================================================
// Hydroponics Platform — ESP32 Node 1 (Environment & Actuation) Configuration
// =============================================================================

// Device Identity
#define DEVICE_ID               "esp32-env"
#define FIRMWARE_VERSION        "0.2.0"

// Sensor & Actuator Logical Identifiers
#define SENSOR_DHT11_ID         "dht11-01"
#define SENSOR_FLOW_ID          "flow-01"
#define ACTUATOR_PUMP_ID        "pump-01"

// Flow Sensor Calibration
#define FLOW_CALIBRATION_FACTOR 7.5f    // YF-S201: F = 7.5 * Q (Q in L/min)
#define FLOW_PULSES_PER_LITER   450.0f  // Standard YF-S201 pulses per Liter

// Relay Actuator Polarity (false = Active HIGH, true = Active LOW)
#define RELAY_ACTIVE_LOW        false

// Safety Interlock Limits
#define SAFETY_DRY_RUN_TIMEOUT_MS 8000   // Force pump off if 0 flow after 8 seconds
#define SAFETY_MAX_PUMP_RUN_MS    300000 // 5 minutes max continuous run time

// Network Mode (false = High-Speed Wired Serial Mode, true = Standalone Wi-Fi/MQTT)
#define ENABLE_WIFI             false
#define WIFI_SSID               "Your_WiFi_SSID"
#define WIFI_PASSWORD           "Your_WiFi_Password"
#define WIFI_CONNECT_TIMEOUT_MS 15000

// MQTT Configuration
#define MQTT_BROKER_HOST        "127.0.0.1"
#define MQTT_BROKER_PORT        1883
#define MQTT_CLIENT_ID          "esp32-env"

// MQTT Topics
#define MQTT_TOPIC_TELEMETRY    "hydroponics/esp32-env/telemetry"
#define MQTT_TOPIC_STATUS       "hydroponics/esp32-env/status"
#define MQTT_TOPIC_COMMANDS     "hydroponics/esp32-env/commands"
#define MQTT_TOPIC_EVENTS       "hydroponics/esp32-env/events"

// Timing & Intervals
#define SERIAL_BAUD_RATE        115200
#define SENSOR_POLL_INTERVAL_MS 2000
#define HEARTBEAT_INTERVAL_MS   30000
