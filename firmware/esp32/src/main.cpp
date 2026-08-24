// =============================================================================
// Hydroponics Monitoring & Control Platform — ESP32 Firmware Entrypoint
// Phase 1 + Phase 9 + Phase 10 + Phase 11:
// Sensors: DHT11, TDS (ppm), Moisture (%), YF-S201 Flow Sensor (L/min & L)
// Actuators: DC Pump Relay (GPIO 26) + BC547 Buzzer (GPIO 25) + 5mm LED (GPIO 2)
// UI: 1.8" TFT ST7735 160x128 SPI Display (Landscape, pins on left)
// Safety: Autonomous Local Dry-Run Interlock & Max Runtime Cutoff
// =============================================================================

#include <Arduino.h>
#include "config/pins.h"
#include "config/config.h"
#include "sensors/dht11_sensor.h"
#include "sensors/tds_sensor.h"
#include "sensors/moisture_sensor.h"
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
static TDSSensor          tds(PIN_TDS_ADC, SENSOR_TDS_ID, ADC_VREF_VOLTAGE);
static MoistureSensor     moisture(PIN_SOIL_MOISTURE_ADC, SENSOR_MOISTURE_ID, ADC_VREF_VOLTAGE);
static FlowSensor         flow(PIN_FLOW_SENSOR, SENSOR_FLOW_ID, FLOW_CALIBRATION_FACTOR, FLOW_PULSES_PER_LITER);
static RelayActuator      pump(PIN_PUMP_RELAY, ACTUATOR_PUMP_ID, "pump", RELAY_ACTIVE_LOW);
static SafetyManager      safety(pump, flow, SAFETY_DRY_RUN_TIMEOUT_MS, SAFETY_MAX_PUMP_RUN_MS);
static TFTDisplayManager  tft(PIN_TFT_CS, PIN_TFT_DC, PIN_TFT_RST, PIN_TFT_BL);
static AlertManager       alerts(PIN_BUZZER, PIN_STATUS_LED);

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
    Serial.println(F("  HYDROPONICS MONITORING & CONTROL PLATFORM"));
    Serial.print  (F("  Device ID:        ")); Serial.println(DEVICE_ID);
    Serial.print  (F("  Firmware Version: ")); Serial.println(FIRMWARE_VERSION);
    Serial.print  (F("  Target Chip:      ESP32 (Core: ")); Serial.print(ESP.getSdkVersion()); Serial.println(F(")"));
    Serial.print  (F("  DHT11 Data Pin:   GPIO ")); Serial.println(PIN_DHT11_DATA);
    Serial.print  (F("  TDS ADC Pin:      GPIO ")); Serial.println(PIN_TDS_ADC);
    Serial.print  (F("  Moisture ADC Pin: GPIO ")); Serial.println(PIN_SOIL_MOISTURE_ADC);
    Serial.print  (F("  Flow Sensor Pin:  GPIO ")); Serial.println(PIN_FLOW_SENSOR);
    Serial.print  (F("  Pump Relay Pin:   GPIO ")); Serial.println(PIN_PUMP_RELAY);
    Serial.print  (F("  Buzzer Driver Pin:GPIO ")); Serial.println(PIN_BUZZER);
    Serial.print  (F("  Status LED Pin:   GPIO ")); Serial.println(PIN_STATUS_LED);
    Serial.print  (F("  TFT Display:      1.8\" ST7735 SPI (160x128)")); Serial.println();
    Serial.println(F("=================================================="));
    Serial.println(F("[SYSTEM] Control Commands & Single-Key Shortcuts:"));
    Serial.println(F("  [1] or 'PUMP ON'       : Start water pump"));
    Serial.println(F("  [0] or 'PUMP OFF'      : Stop water pump"));
    Serial.println(F("  [t] or 'PUMP TOGGLE'   : Toggle pump ON/OFF"));
    Serial.println(F("  [a] or 'AUTO ON'       : Enable auto-irrigation"));
    Serial.println(F("  [d] or 'AUTO OFF'      : Disable auto-irrigation"));
    Serial.println(F("  [r] or 'RESET FAULT'   : Clear safety fault lockout"));
    Serial.println(F("=================================================="));
    Serial.println(F("[SYSTEM] Initializing hardware peripherals..."));
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
            Serial.println(F("[PUMP] ⚠️ Cannot start pump: Safety Fault active! Send 'r' or 'RESET FAULT' first."));
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
                Serial.println(F("[PUMP] ⚠️ Cannot start pump: Safety Fault active! Send 'r' or 'RESET FAULT' first."));
            } else {
                pump.turnOn();
                Serial.println(F("[PUMP] 🟢 -> Pump toggled to ON."));
            }
        }
    } else if (cmd == "A" || cmd == "AUTO ON" || cmd == "AUTO WATER ON") {
        safety.setAutoIrrigation(true);
        Serial.println(F("[SAFETY] 🌱 -> Auto-irrigation ENABLED (triggers when moisture < 25%)."));
    } else if (cmd == "D" || cmd == "AUTO OFF" || cmd == "AUTO WATER OFF") {
        safety.setAutoIrrigation(false);
        Serial.println(F("[SAFETY] ⏸️ -> Auto-irrigation DISABLED."));
    } else if (cmd == "P" || cmd == "POL" || cmd == "POLARITY") {
        pump.togglePolarity();
        Serial.printf("[RELAY] ⚙️ Polarity switched to: %s\n", pump.isActiveLow() ? "Active LOW" : "Active HIGH");
    } else if (cmd == "R" || cmd == "RESET" || cmd == "RESET FAULT") {
        safety.clearFaults();
        Serial.println(F("[SAFETY] 🔓 -> Faults cleared. System ready."));
    } else if (cmd == "H" || cmd == "?" || cmd == "HELP") {
        Serial.println(F("Keys: [1]=ON, [0]=OFF, [t]=TOGGLE, [p]=TOGGLE POLARITY, [a]=AUTO ON, [d]=AUTO OFF, [r]=RESET FAULT"));
    } else {
        Serial.printf("[CMD] Unknown command: '%s'. Type 'HELP' or press '?'\n", cmd.c_str());
    }
}

void processSerialCommands() {
    while (Serial.available()) {
        char c = (char)Serial.read();

        // Handle immediate single-character keys
        if (c == '1' || c == '0' || c == 't' || c == 'T' || c == 'p' || c == 'P' || c == 'r' || c == 'R' || c == 'a' || c == 'A' || c == 'd' || c == 'D' || c == '?' || c == 'h' || c == 'H') {
            if (serialInputBuffer.length() == 0) {
                String singleCmd = "";
                singleCmd += c;
                executeCommand(singleCmd);
                continue;
            }
        }

        // Buffer full lines
        if (c == '\r' || c == '\n') {
            if (serialInputBuffer.length() > 0) {
                executeCommand(serialInputBuffer);
                serialInputBuffer = "";
            }
        } else {
            if (serialInputBuffer.length() < 64) {
                serialInputBuffer += c;
            }
        }
    }
}

void setup() {
    // 1. Initialize Serial Communication
    Serial.begin(SERIAL_BAUD_RATE);
    delay(1000); // Allow UART bridge to settle

    printBanner();

    // 2. Setup Audio & LED Alert Manager
    alerts.begin();

    // 3. Initialize Pump Relay (Defaults to OFF immediately)
    pump.begin();
    Serial.println(F("[ACTUATOR] Pump relay initialized (Safe startup state: OFF)."));

    // 4. Initialize Flow Sensor (Pulse Interrupt on GPIO 13)
    Serial.print(F("[FLOW]  Initializing YF-S201 on GPIO "));
    Serial.print(PIN_FLOW_SENSOR);
    Serial.println(F("..."));
    flow.begin();
    Serial.println(F("[FLOW]  Hardware interrupt ISR attached and ready."));

    // 5. Initialize TFT Display (1.8" ST7735 160x128 Landscape)
    Serial.println(F("[TFT]   Initializing 1.8\" ST7735 SPI Display..."));
    if (tft.begin(TFTDriverType::ST7735_128x160)) {
        Serial.println(F("[TFT]   Display initialized successfully."));
    } else {
        Serial.println(F("[TFT]   Display initialization failed/pending."));
    }

    // 6. Initialize DHT11 Environmental Sensor
    Serial.print(F("[DHT11] Initializing on GPIO "));
    Serial.print(PIN_DHT11_DATA);
    Serial.println(F("..."));
    if (dht11.begin()) {
        Serial.println(F("[DHT11] Sensor detected and ready."));
    } else {
        Serial.println(F("[DHT11] Initial reading pending/failed."));
    }

    // 7. Initialize Analog TDS Sensor
    Serial.print(F("[TDS]   Initializing on ADC Pin GPIO "));
    Serial.print(PIN_TDS_ADC);
    Serial.println(F("..."));
    tds.begin();

    // 8. Initialize Analog Moisture Sensor
    Serial.print(F("[MOIST] Initializing on ADC Pin GPIO "));
    Serial.print(PIN_SOIL_MOISTURE_ADC);
    Serial.println(F("..."));
    moisture.begin();

    // 9. Display 6-Second Animated Welcome Screen with Musical Fanfare & Rapid LED Strobe
    Serial.println(F("[SYSTEM] Displaying 6-second animated Welcome Screen with musical fanfare..."));
    tft.showWelcomeScreen(DEVICE_ID, FIRMWARE_VERSION, PIN_STATUS_LED, PIN_BUZZER, 6000);

    // 10. Initialize Wireless Wi-Fi & MQTT Transport (Only if ENABLE_WIFI is true)
    if (ENABLE_WIFI) {
        Serial.println(F("[NETWORK] Initializing Wi-Fi & MQTT..."));
        wifi.begin();

        mqtt.begin([](const String& action, const String& target, const String& value) {
            String fullCmd = action;
            if (value.length() > 0) {
                fullCmd += " " + value;
            }
            executeCommand(fullCmd);
        });
    } else {
        Serial.println(F("[NETWORK] High-Speed Wired Serial Mode Active (Wi-Fi Radio Disabled for Max Stability)."));
    }

    Serial.println(F("[SYSTEM] Initialization complete. Starting multi-sensor, pump & safety loop.\n"));
}

void loop() {
    unsigned long now = millis();

    // -------------------------------------------------------------------------
    // Continuous Task 1: Non-blocking Audio & LED Alert Engine (Every ms)
    // -------------------------------------------------------------------------
    alerts.update(now);

    // -------------------------------------------------------------------------
    // Continuous Task 2: Process Serial Terminal Commands (Instant)
    // -------------------------------------------------------------------------
    processSerialCommands();

    // -------------------------------------------------------------------------
    // Continuous Task 3: Wireless Network & MQTT Loops (Only when enabled)
    // -------------------------------------------------------------------------
    if (ENABLE_WIFI) {
        wifi.update(now);
        mqtt.update(now, wifi.isConnected());
    }

    // -------------------------------------------------------------------------
    // Continuous Task 4: Autonomous Local Safety Interlocks (Every ms)
    // -------------------------------------------------------------------------
    const char* safetyFault = safety.evaluateSafety(moisture.getMoisturePercent());

    // -------------------------------------------------------------------------
    // Task 5: Periodic Multi-Sensor Acquisition & Telemetry (Every 2s)
    // -------------------------------------------------------------------------
    if (now - lastSensorPollTime >= SENSOR_POLL_INTERVAL_MS) {
        lastSensorPollTime = now;
        messageSequence++;

        // 1. Sample Flow Sensor
        flow.sample();

        // 2. Sample DHT11
        bool dhtOk = dht11.sample();
        if (dhtOk && !isnan(dht11.getTemperature())) {
            tds.setWaterTemperature(dht11.getTemperature());
        }

        // 3. Sample TDS Sensor
        tds.sample();

        // 4. Sample Moisture Sensor
        moisture.sample();

        // 5. Evaluate Multi-Modal Alerts (Dry-Run / Low Moisture / Temp / TDS)
        const char* alertMsg = alerts.evaluate(
            dht11.getTemperature(),
            dht11.getHumidity(),
            tds.getTdsPpm(),
            moisture.getMoisturePercent(),
            safetyFault
        );

        // 6. Update Local TFT Color Display Dashboard
        uint32_t uptimeSeconds = now / 1000;
        tft.updateDashboard(
            dht11.getTemperature(),
            dht11.getHumidity(),
            tds.getTdsPpm(),
            moisture.getMoisturePercent(),
            pump.isOn(),
            flow.getFlowRateLpm(),
            wifi.isConnected(),
            mqtt.isConnected(),
            uptimeSeconds
        );

        if (alertMsg != nullptr) {
            tft.showStatusMessage(alertMsg);
        }

        // 7. Collect all normalized measurements into unified envelope
        Measurement allMeasurements[7];
        size_t totalCount = 0;

        // Add DHT11 measurements (air_temperature, humidity)
        totalCount += dht11.getMeasurements(&allMeasurements[totalCount], 2);

        // Add TDS measurement (tds)
        totalCount += tds.getMeasurements(&allMeasurements[totalCount], 1);

        // Add Moisture measurement (substrate_moisture)
        totalCount += moisture.getMeasurements(&allMeasurements[totalCount], 1);

        // Add Flow Sensor measurements (flow_rate, water_volume)
        totalCount += flow.getMeasurements(&allMeasurements[totalCount], 2);

        // Human-readable diagnostic log
        Serial.printf("[SYSTEM] Temp: %.1fC | Hum: %.1f%% | TDS: %.0f ppm | Moist: %.1f%% | Flow: %.2f L/m | Vol: %.2fL | Pump: %s | WiFi: %s | MQTT: %s | Alarm: %s\n",
                      dht11.getTemperature(),
                      dht11.getHumidity(),
                      tds.getTdsPpm(),
                      moisture.getMoisturePercent(),
                      flow.getFlowRateLpm(),
                      flow.getTotalLiters(),
                      pump.getStateString(),
                      wifi.isConnected() ? "CONNECTED" : "DISCONNECTED",
                      mqtt.isConnected() ? "CONNECTED" : "DISCONNECTED",
                      alertMsg ? alertMsg : "NONE");

        // Generate and stream canonical JSON telemetry envelope
        String jsonTelemetry = TelemetryFormatter::formatTelemetryJson(
            DEVICE_ID,
            messageSequence,
            uptimeSeconds,
            allMeasurements,
            totalCount
        );

        Serial.print(F("[TELEMETRY_JSON] "));
        Serial.println(jsonTelemetry);

        // Publish over MQTT wirelessly
        if (mqtt.isConnected()) {
            mqtt.publishTelemetry(jsonTelemetry);
        }
    }

    // -------------------------------------------------------------------------
    // Task 5: System Health & Heartbeat (Every 30s)
    // -------------------------------------------------------------------------
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
