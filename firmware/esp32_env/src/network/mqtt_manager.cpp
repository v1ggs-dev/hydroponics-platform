#include "mqtt_manager.h"
#include <ArduinoJson.h>

MQTTManager::MQTTManager(const char* brokerHost,
                         uint16_t brokerPort,
                         const char* clientId,
                         const char* topicTelemetry,
                         const char* topicStatus,
                         const char* topicCommands,
                         const char* topicEvents)
    : _brokerHost(brokerHost),
      _brokerPort(brokerPort),
      _clientId(clientId),
      _topicTelemetry(topicTelemetry),
      _topicStatus(topicStatus),
      _topicCommands(topicCommands),
      _topicEvents(topicEvents),
      _wifiClient(),
      _mqttClient(_wifiClient),
      _commandCallback(nullptr),
      _lastReconnectAttempt(0),
      _wasConnected(false) {}

void MQTTManager::begin(MQTTCommandCallback commandCallback) {
    _commandCallback = commandCallback;
    _mqttClient.setServer(_brokerHost, _brokerPort);
    _mqttClient.setBufferSize(1024); // Ensure large JSON envelopes fit in packet buffer

    _mqttClient.setCallback([this](char* topic, uint8_t* payload, unsigned int length) {
        this->onMessageReceived(topic, payload, length);
    });
}

bool MQTTManager::isConnected() {
    return _mqttClient.connected();
}

bool MQTTManager::reconnect() {
    Serial.printf("[MQTT]  Attempting connection to broker at %s:%d...\n", _brokerHost, _brokerPort);

    // Prepare Last Will and Testament (LWT)
    const char* willTopic = _topicStatus;
    const char* willMessage = "{\"deviceId\":\"esp32-01\",\"status\":\"OFFLINE\"}";
    int willQos = 1;
    bool willRetain = true;

    if (_mqttClient.connect(_clientId, willTopic, willQos, willRetain, willMessage)) {
        Serial.println(F("[MQTT]  Connected to broker successfully!"));

        // Publish online status
        publishStatus("ONLINE");

        // Subscribe to commands
        _mqttClient.subscribe(_topicCommands, 1);
        Serial.printf("[MQTT]  Subscribed to topic: %s\n", _topicCommands);

        return true;
    } else {
        Serial.printf("[MQTT]  Connect failed, rc=%d. Will retry...\n", _mqttClient.state());
        return false;
    }
}

void MQTTManager::update(unsigned long nowMs, bool isWifiConnected) {
    if (!isWifiConnected) return;

    if (_mqttClient.connected()) {
        _mqttClient.loop();
        if (!_wasConnected) {
            _wasConnected = true;
        }
    } else {
        if (_wasConnected) {
            _wasConnected = false;
            Serial.println(F("[MQTT]  Disconnected from broker. Entering auto-reconnect mode..."));
        }

        // Retry connection every 5 seconds non-blockingly
        if (nowMs - _lastReconnectAttempt >= 5000) {
            _lastReconnectAttempt = nowMs;
            reconnect();
        }
    }
}

bool MQTTManager::publishTelemetry(const String& jsonPayload) {
    if (!_mqttClient.connected()) return false;
    return _mqttClient.publish(_topicTelemetry, jsonPayload.c_str(), false);
}

bool MQTTManager::publishEvent(const String& jsonPayload) {
    if (!_mqttClient.connected()) return false;
    return _mqttClient.publish(_topicEvents, jsonPayload.c_str(), true);
}

bool MQTTManager::publishStatus(const char* status) {
    if (!_mqttClient.connected()) return false;
    JsonDocument doc;
    doc["deviceId"] = _clientId;
    doc["status"] = status;
    doc["uptimeSeconds"] = millis() / 1000;
    
    String output;
    serializeJson(doc, output);
    return _mqttClient.publish(_topicStatus, output.c_str(), true);
}

void MQTTManager::onMessageReceived(char* topic, uint8_t* payload, unsigned int length) {
    String message = "";
    for (unsigned int i = 0; i < length; i++) {
        message += (char)payload[i];
    }

    Serial.printf("[MQTT_RECV] Topic '%s' -> %s\n", topic, message.c_str());

    if (_commandCallback) {
        JsonDocument doc;
        DeserializationError err = deserializeJson(doc, message);

        if (!err) {
            String action = doc["action"] | "";
            String target = doc["actuatorId"] | doc["target"] | "";
            String value  = doc["value"] | "";
            _commandCallback(action, target, value);
        } else {
            // Raw text command fallback
            _commandCallback(message, "", "");
        }
    }
}
