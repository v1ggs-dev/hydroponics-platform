#pragma once

#include <Arduino.h>
#include <WiFiClient.h>
#include <PubSubClient.h>
#include <functional>

typedef std::function<void(const String& action, const String& target, const String& value)> MQTTCommandCallback;

class MQTTManager {
public:
    MQTTManager(const char* brokerHost,
                uint16_t brokerPort,
                const char* clientId,
                const char* topicTelemetry,
                const char* topicStatus,
                const char* topicCommands,
                const char* topicEvents);
    ~MQTTManager() = default;

    void begin(MQTTCommandCallback commandCallback);
    void update(unsigned long nowMs, bool isWifiConnected);

    bool isConnected();
    bool publishTelemetry(const String& jsonPayload);
    bool publishEvent(const String& jsonPayload);
    bool publishStatus(const char* status);

private:
    const char* _brokerHost;
    uint16_t    _brokerPort;
    const char* _clientId;
    const char* _topicTelemetry;
    const char* _topicStatus;
    const char* _topicCommands;
    const char* _topicEvents;

    WiFiClient   _wifiClient;
    PubSubClient _mqttClient;
    MQTTCommandCallback _commandCallback;

    unsigned long _lastReconnectAttempt;
    bool _wasConnected;

    void onMessageReceived(char* topic, uint8_t* payload, unsigned int length);
    bool reconnect();
};
