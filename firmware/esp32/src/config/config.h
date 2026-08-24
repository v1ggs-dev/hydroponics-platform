#pragma once

// =============================================================================
// Hydroponics Platform — Global Firmware Configuration
// =============================================================================

// Device Identity
#define DEVICE_ID               "esp32-01"
#define FIRMWARE_VERSION        "0.1.0"

// Sensor & Actuator Logical Identifiers
#define SENSOR_DHT11_ID         "dht11-01"
#define SENSOR_TDS_ID           "tds-01"
#define SENSOR_MOISTURE_ID      "moisture-01"
#define SENSOR_FLOW_ID          "flow-01"
#define ACTUATOR_PUMP_ID        "pump-01"

// Flow Sensor Calibration
#define FLOW_CALIBRATION_FACTOR 7.5f    // YF-S201: F = 7.5 * Q (Q in L/min)
#define FLOW_PULSES_PER_LITER   450.0f  // Standard YF-S201 pulses per Liter

// Relay Actuator Polarity (false = Active HIGH [0V=OFF, 3.3V=ON], true = Active LOW)
#define RELAY_ACTIVE_LOW        false

// Safety Interlock Limits
#define SAFETY_DRY_RUN_TIMEOUT_MS 8000   // Force pump off if 0 flow after 8 seconds
#define SAFETY_MAX_PUMP_RUN_MS    300000 // 5 minutes max continuous run time

// ADC & Voltage Calibration Settings
#define ADC_VREF_VOLTAGE        3.3f    // Operating reference voltage for ESP32 ADC
#define ADC_RESOLUTION          4095.0f // 12-bit ADC (0-4095)

// Network Mode (false = High-Speed Wired Serial Mode, true = Standalone Wi-Fi/MQTT)
#define ENABLE_WIFI             false
#define WIFI_SSID               "Your_WiFi_SSID"        // 2.4GHz Wi-Fi SSID
#define WIFI_PASSWORD           "Your_WiFi_Password"    // Wi-Fi Password
#define WIFI_CONNECT_TIMEOUT_MS 15000                   // 15 seconds connection timeout

// MQTT Message Broker Configuration
#define MQTT_BROKER_HOST        "192.168.1.6"           // Local PC IP running MQTT broker
#define MQTT_BROKER_PORT        1883                    // Standard MQTT TCP Port
#define MQTT_CLIENT_ID          "esp32-01"

// MQTT Topics (Conforming to docs/protocols/MQTT.md)
#define MQTT_TOPIC_TELEMETRY    "hydroponics/esp32-01/telemetry"
#define MQTT_TOPIC_STATUS       "hydroponics/esp32-01/status"
#define MQTT_TOPIC_COMMANDS     "hydroponics/esp32-01/commands"
#define MQTT_TOPIC_EVENTS       "hydroponics/esp32-01/events"

// Timing & Intervals
#define SERIAL_BAUD_RATE        115200
#define SENSOR_POLL_INTERVAL_MS 2000    // Minimum 2 seconds between sensor samples
#define HEARTBEAT_INTERVAL_MS   30000   // 30 seconds status heartbeat
