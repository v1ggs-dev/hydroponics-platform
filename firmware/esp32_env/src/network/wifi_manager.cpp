#include "wifi_manager.h"

WiFiManager::WiFiManager(const char* ssid, const char* password, unsigned long reconnectIntervalMs)
    : _ssid(ssid),
      _password(password),
      _reconnectIntervalMs(reconnectIntervalMs),
      _lastReconnectAttempt(0),
      _connected(false),
      _connecting(false) {}

void WiFiManager::begin() {
    WiFi.mode(WIFI_STA);
    WiFi.disconnect(true);
    delay(100);

    Serial.printf("[WIFI]  Connecting to SSID '%s'...\n", _ssid);
    WiFi.begin(_ssid, _password);
    _lastReconnectAttempt = millis();
    _connecting = true;
}

void WiFiManager::update(unsigned long nowMs) {
    bool currentlyConnected = (WiFi.status() == WL_CONNECTED);

    if (currentlyConnected && !_connected) {
        // Just transitioned to connected
        _connected = true;
        _connecting = false;
        Serial.printf("[WIFI]  Connected successfully! IP: %s | RSSI: %d dBm\n",
                      WiFi.localIP().toString().c_str(), WiFi.RSSI());
    } else if (!currentlyConnected && _connected) {
        // Lost connection
        _connected = false;
        Serial.println(F("[WIFI]  Connection lost. Entering non-blocking auto-reconnect mode..."));
    }

    // Auto-reconnect every interval if disconnected
    if (!_connected && (nowMs - _lastReconnectAttempt >= _reconnectIntervalMs)) {
        _lastReconnectAttempt = nowMs;
        Serial.printf("[WIFI]  Attempting reconnection to '%s'...\n", _ssid);
        WiFi.disconnect();
        WiFi.begin(_ssid, _password);
    }
}
