// =============================================================================
// Hydroponics Monitoring & Control Platform — ESP32 Node 1 (Environment & Actuation)
// Sensors: DHT11 (Air Temp & Humidity), YF-S201 Flow Sensor (L/min & Volume L)
// Actuators: DC Pump Relay (GPIO 26) + BC547 Buzzer (GPIO 25)
// UI: 1.8" TFT ST7735 160x128 SPI Display #1 (Landscape)
// Safety: Autonomous Local Dry-Run Interlock & Max Runtime Cutoff
// =============================================================================

#include <Arduino.h>
#include "config/pins.h"
#include "config/config.h"
#include "sensors/dht11_sensor.h"
#include "sensors/flow_sensor.h"
#include "actuators/relay_actuator.h"
#include "safety/safety_manager.h"
#include "display/tft_display.h"
#include "alerts/alert_manager.h"
#include "telemetry/telemetry_formatter.h"
#include "network/wifi_manager.h"
#include "network/mqtt_manager.h"

// Instantiate Hardware Modules
static DHT11Sensor        dht11(PIN_DHT11_DATA, SENSOR_DHT11_ID);
static FlowSensor         flow(PIN_FLOW_SENSOR, SENSOR_FLOW_ID, FLOW_CALIBRATION_FACTOR, FLOW_PULSES_PER_LITER);
static RelayActuator      pump(PIN_PUMP_RELAY, ACTUATOR_PUMP_ID, "pump", RELAY_ACTIVE_LOW);
static SafetyManager      safety(pump, flow, SAFETY_DRY_RUN_TIMEOUT_MS, SAFETY_MAX_PUMP_RUN_MS);
static TFTDisplayManager  tft(PIN_TFT_CS, PIN_TFT_DC, PIN_TFT_RST, PIN_TFT_BL);
static AlertManager       alerts(PIN_BUZZER);

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
    Serial.println(F("  HYDROPONICS PLATFORM — NODE 1: ENV & ACTUATOR"));
    Serial.print  (F("  Device ID:        ")); Serial.println(DEVICE_ID);
    Serial.print  (F("  Firmware Version: ")); Serial.println(FIRMWARE_VERSION);
    Serial.print  (F("  Target Chip:      ESP32 (Core: ")); Serial.print(ESP.getSdkVersion()); Serial.println(F(")"));
    Serial.print  (F("  DHT11 Data Pin:   GPIO ")); Serial.println(PIN_DHT11_DATA);
    Serial.print  (F("  Flow Sensor Pin:  GPIO ")); Serial.println(PIN_FLOW_SENSOR);
    Serial.print  (F("  Pump Relay Pin:   GPIO ")); Serial.println(PIN_PUMP_RELAY);
    Serial.print  (F("  Buzzer Driver Pin:GPIO ")); Serial.println(PIN_BUZZER);
    Serial.print  (F("  TFT Display #1:   1.8\" ST7735 SPI (160x128)")); Serial.println();
    Serial.println(F("=================================================="));
    Serial.println(F("[SYSTEM] Commands: 1 (ON), 0 (OFF), t (TOGGLE), r (RESET FAULT), a (AUTO ON), d (AUTO OFF)"));
    Serial.println(F("=================================================="));
}

static String serialInputBuffer = "";

void executeCommand(String cmd) {
    cmd.trim();
    cmd.toUpperCase();
    if (cmd.length() == 0) return;

    Serial.print(F("[CMD_EXEC] \""));
    Serial.print(cmd);
    Serial.println(F("\""));

    if (cmd == "1" || cmd == "PUMP ON" || cmd == "ON") {
        if (safety.hasFault()) {
            Serial.println(F("[PUMP] ⚠️ Cannot start pump: Safety Fault active! Send 'r' to reset."));
        } else {
            pump.turnOn();
            Serial.println(F("[PUMP] 🟢 -> Pump state set to ON."));
        }
    } else if (cmd == "0" || cmd == "PUMP OFF" || cmd == "OFF") {
        pump.turnOff();
        Serial.println(F("[PUMP] 🔴 -> Pump state set to OFF."));
    } else if (cmd == "T" || cmd == "PUMP TOGGLE" || cmd == "TOGGLE") {
        if (pump.isOn()) {
            pump.turnOff();
            Serial.println(F("[PUMP] 🔴 -> Pump toggled to OFF."));
        } else {
            if (safety.hasFault()) {
                Serial.println(F("[PUMP] ⚠️ Cannot start pump: Safety Fault active! Send 'r' to reset."));
            } else {
                pump.turnOn();
                Serial.println(F("[PUMP] 🟢 -> Pump toggled to ON."));
            }
        }
    } else if (cmd == "R" || cmd == "RESET" || cmd == "RESET FAULT") {
        safety.clearFaults();
        Serial.println(F("[SAFETY] 🛡️ Fault status cleared. Actuators unlocked."));
    } else if (cmd == "A" || cmd == "AUTO ON") {
        safety.setAutoIrrigation(true);
        Serial.println(F("[SAFETY] 🤖 Auto-watering mode ENABLED."));
    } else if (cmd == "D" || cmd == "AUTO OFF") {
        safety.setAutoIrrigation(false);
        Serial.println(F("[SAFETY] 🤖 Auto-watering mode DISABLED."));
    } else {
        Serial.print(F("[CMD_EXEC] ❓ Unknown command: "));
        Serial.println(cmd);
    }
}

void processSerialCommands() {
    while (Serial.available() > 0) {
        char inChar = (char)Serial.read();
        if (inChar == '\n' || inChar == '\r') {
            if (serialInputBuffer.length() > 0) {
                executeCommand(serialInputBuffer);
                serialInputBuffer = "";
            }
        } else {
            serialInputBuffer += inChar;
        }
    }
}

void setup() {
    Serial.begin(SERIAL_BAUD_RATE);
    delay(500);

    printBanner();

    // 1. Initialize Alerts
    alerts.begin();
    alerts.triggerBootChime();

    // 2. Initialize Display #1
    tft.begin(TFTDriverType::ST7735_128x160);
    tft.showWelcomeScreen(DEVICE_ID, FIRMWARE_VERSION, PIN_BUZZER, 2500);

    // 3. Initialize Sensors
    dht11.begin();
    flow.begin();

    // 4. Initialize Actuators
    pump.begin();

    #if ENABLE_WIFI
    wifi.begin();
    mqtt.begin();
    #endif

    Serial.println(F("[SYSTEM] Node 1 initialization complete. Entering main control loop."));
}

void loop() {
    unsigned long now = millis();

    // 1. Non-blocking Audio pattern updates
    alerts.update(now);

    // 2. Process incoming serial commands
    processSerialCommands();

    // 3. Evaluate safety rules continuously
    const char* safetyFault = safety.evaluateSafety(50.0f); // Default safe moisture value

    #if ENABLE_WIFI
    wifi.update(now);
    mqtt.update(now, wifi.isConnected());
    #endif

    // 4. Regular Telemetry Tick (2000ms)
    if (now - lastSensorPollTime >= SENSOR_POLL_INTERVAL_MS) {
        lastSensorPollTime = now;
        messageSequence++;

        // Sample sensors
        flow.sample();
        dht11.sample();

        float tempC = dht11.getTemperature();
        float humPct = dht11.getHumidity();
        float flowRateLpm = flow.getFlowRateLpm();
        float totalVolL = flow.getTotalLiters();

        // Evaluate Alerts
        alerts.evaluate(tempC, humPct, safetyFault);

        // Update Display #1
        uint32_t uptimeSeconds = now / 1000;
        tft.updateDashboard(tempC, humPct, flowRateLpm, totalVolL, pump.isOn(), safety.isAutoIrrigationEnabled(), safety.hasFault(), uptimeSeconds);

        // Collect measurements
        Measurement nodeMeasurements[4];
        size_t totalCount = 0;

        totalCount += dht11.getMeasurements(&nodeMeasurements[totalCount], 2);
        totalCount += flow.getMeasurements(&nodeMeasurements[totalCount], 2);

        // Human-readable diagnostic log
        Serial.printf("[SYSTEM] Temp: %.1fC | Hum: %.1f%% | Flow: %.2f L/m | Vol: %.2fL | Pump: %s | Alarm: %s\n",
                      tempC, humPct, flowRateLpm, totalVolL, pump.getStateString(), safetyFault ? safetyFault : "NONE");

        // Format and stream canonical JSON
        String jsonTelemetry = TelemetryFormatter::formatTelemetryJson(
            DEVICE_ID,
            messageSequence,
            uptimeSeconds,
            nodeMeasurements,
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
