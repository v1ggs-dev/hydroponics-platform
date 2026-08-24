// =============================================================================
// Hydroponics Monitoring & Control Platform — ESP32 Node 2 (Water Chemistry & Root Zone)
// Sensors: Analog pH Sensor (GPIO 34), Analog TDS Probe (GPIO 35), Moisture Probe (GPIO 32)
// UI: 1.8" TFT ST7735 160x128 SPI Display #2 (Landscape)
// =============================================================================

#include <Arduino.h>
#include "config/pins.h"
#include "config/config.h"
#include "sensors/ph_sensor.h"
#include "sensors/tds_sensor.h"
#include "sensors/moisture_sensor.h"
#include "display/tft_display.h"
#include "telemetry/telemetry_formatter.h"
#include "network/wifi_manager.h"
#include "network/mqtt_manager.h"

// Instantiate Hardware Modules
static PHSensor           ph(PIN_PH_ADC, SENSOR_PH_ID, ADC_VREF_VOLTAGE, PH_CALIBRATION_NEUTRAL_V, PH_CALIBRATION_SLOPE);
static TDSSensor          tds(PIN_TDS_ADC, SENSOR_TDS_ID, ADC_VREF_VOLTAGE);
static MoistureSensor     moisture(PIN_SOIL_MOISTURE_ADC, SENSOR_MOISTURE_ID, ADC_VREF_VOLTAGE);
static TFTDisplayManager  tft(PIN_TFT_CS, PIN_TFT_DC, PIN_TFT_RST, PIN_TFT_BL);

// Instantiate Network Managers
static WiFiManager        wifi(WIFI_SSID, WIFI_PASSWORD, 10000);
static MQTTManager        mqtt(MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_CLIENT_ID,
                               MQTT_TOPIC_TELEMETRY, MQTT_TOPIC_STATUS, MQTT_TOPIC_COMMANDS, MQTT_TOPIC_EVENTS);

// Loop timers and sequence counters
static unsigned long lastSensorPollTime = 0;
static unsigned long lastHeartbeatTime = 0;
static uint32_t messageSequence = 0;

void printBanner() {
    Serial.println();
    Serial.println(F("=================================================="));
    Serial.println(F("  HYDROPONICS PLATFORM — NODE 2: WATER CHEMISTRY"));
    Serial.print  (F("  Device ID:        ")); Serial.println(DEVICE_ID);
    Serial.print  (F("  Firmware Version: ")); Serial.println(FIRMWARE_VERSION);
    Serial.print  (F("  Target Chip:      ESP32 (Core: ")); Serial.print(ESP.getSdkVersion()); Serial.println(F(")"));
    Serial.print  (F("  pH ADC Pin:       GPIO ")); Serial.println(PIN_PH_ADC);
    Serial.print  (F("  TDS ADC Pin:      GPIO ")); Serial.println(PIN_TDS_ADC);
    Serial.print  (F("  Moisture ADC Pin: GPIO ")); Serial.println(PIN_SOIL_MOISTURE_ADC);
    Serial.print  (F("  TFT Display #2:   1.8\" ST7735 SPI (160x128)")); Serial.println();
    Serial.println(F("=================================================="));
}

void setup() {
    Serial.begin(SERIAL_BAUD_RATE);
    delay(500);

    printBanner();

    // 1. Initialize Display #2
    tft.begin(TFTDriverType::ST7735_128x160);
    tft.showWelcomeScreen(DEVICE_ID, FIRMWARE_VERSION, 2500);

    // 2. Initialize Analog Sensors
    ph.begin();
    tds.begin();
    moisture.begin();

    #if ENABLE_WIFI
    wifi.begin();
    mqtt.begin();
    #endif

    Serial.println(F("[SYSTEM] Node 2 initialization complete. Entering chemistry telemetry loop."));
}

void loop() {
    unsigned long now = millis();

    #if ENABLE_WIFI
    wifi.update(now);
    mqtt.update(now, wifi.isConnected());
    #endif

    // Regular Telemetry Tick (2000ms)
    if (now - lastSensorPollTime >= SENSOR_POLL_INTERVAL_MS) {
        lastSensorPollTime = now;
        messageSequence++;

        // 1. Sample Sensors
        ph.sample();
        tds.sample();
        moisture.sample();

        float phVal = ph.getPH();
        float tdsPpm = tds.getTdsPpm();
        float moistPct = moisture.getMoisturePercent();
        float phVolts = ph.getRawVoltage();

        // 2. Update Display #2
        uint32_t uptimeSeconds = now / 1000;
        tft.updateDashboard(phVal, tdsPpm, moistPct, phVolts, uptimeSeconds);

        // 3. Collect measurements
        Measurement chemMeasurements[3];
        size_t totalCount = 0;

        totalCount += ph.getMeasurements(&chemMeasurements[totalCount], 1);
        totalCount += tds.getMeasurements(&chemMeasurements[totalCount], 1);
        totalCount += moisture.getMeasurements(&chemMeasurements[totalCount], 1);

        // Human-readable diagnostic log
        Serial.printf("[CHEMISTRY] pH: %.2f (%.2fV) | TDS: %.0f ppm | Moisture: %.1f%%\n",
                      phVal, phVolts, tdsPpm, moistPct);

        // 4. Format and stream canonical JSON
        String jsonTelemetry = TelemetryFormatter::formatTelemetryJson(
            DEVICE_ID,
            messageSequence,
            uptimeSeconds,
            chemMeasurements,
            totalCount
        );

        Serial.print(F("[TELEMETRY_JSON] "));
        Serial.println(jsonTelemetry);

        #if ENABLE_WIFI
        if (mqtt.isConnected()) {
            mqtt.publishTelemetry(jsonTelemetry);
        }
        #endif
    }

    // 5. System Health & Heartbeat (Every 30s)
    if (now - lastHeartbeatTime >= HEARTBEAT_INTERVAL_MS) {
        lastHeartbeatTime = now;
        uint32_t uptimeSeconds = now / 1000;
        uint32_t freeHeap = ESP.getFreeHeap();

        String jsonHeartbeat = TelemetryFormatter::formatHeartbeatJson(
            DEVICE_ID,
            FIRMWARE_VERSION,
            uptimeSeconds,
            freeHeap
        );

        Serial.print(F("[HEARTBEAT_JSON] "));
        Serial.println(jsonHeartbeat);
    }
}
