#pragma once

// =============================================================================
// Hydroponics Platform — ESP32 Node 2 (Water Chemistry & Root Zone) Configuration
// =============================================================================

// Device Identity
#define DEVICE_ID               "esp32-chem"
#define FIRMWARE_VERSION        "0.2.0"

// Sensor Logical Identifiers
#define SENSOR_PH_ID            "ph-01"
#define SENSOR_TDS_ID           "tds-01"
#define SENSOR_MOISTURE_ID      "moisture-01"

// ADC & Voltage Calibration Settings
#define ADC_VREF_VOLTAGE        3.3f    // Operating reference voltage for ESP32 ADC
#define ADC_RESOLUTION          4095.0f // 12-bit ADC (0-4095)

// pH Calibration Defaults
#define PH_CALIBRATION_NEUTRAL_V 1.65f  // Neutral reference voltage (pH 7.0)
#define PH_CALIBRATION_SLOPE    0.18f   // Volts per pH unit (approx 180mV/pH)

// Network Mode (false = High-Speed Wired Serial Mode, true = Standalone Wi-Fi/MQTT)
#define ENABLE_WIFI             false
#define WIFI_SSID               "Your_WiFi_SSID"
#define WIFI_PASSWORD           "Your_WiFi_Password"
#define WIFI_CONNECT_TIMEOUT_MS 15000

// MQTT Configuration
#define MQTT_BROKER_HOST        "127.0.0.1"
#define MQTT_BROKER_PORT        1883
#define MQTT_CLIENT_ID          "esp32-chem"

// MQTT Topics
#define MQTT_TOPIC_TELEMETRY    "hydroponics/esp32-chem/telemetry"
#define MQTT_TOPIC_STATUS       "hydroponics/esp32-chem/status"
#define MQTT_TOPIC_COMMANDS     "hydroponics/esp32-chem/commands"
#define MQTT_TOPIC_EVENTS       "hydroponics/esp32-chem/events"

// Timing & Intervals
#define SERIAL_BAUD_RATE        115200
#define SENSOR_POLL_INTERVAL_MS 2000
#define HEARTBEAT_INTERVAL_MS   30000
