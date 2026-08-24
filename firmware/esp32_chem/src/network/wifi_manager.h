#pragma once

#include <Arduino.h>
#include <WiFi.h>

class WiFiManager {
public:
    WiFiManager(const char* ssid, const char* password, unsigned long reconnectIntervalMs = 10000);
    ~WiFiManager() = default;

    void begin();
    void update(unsigned long nowMs);

    // State inspection
    bool isConnected() const { return _connected; }
    String getIpAddress() const { return _connected ? WiFi.localIP().toString() : "0.0.0.0"; }
    int getRssi() const { return _connected ? WiFi.RSSI() : 0; }
    const char* getSsid() const { return _ssid; }

private:
    const char*   _ssid;
    const char*   _password;
    unsigned long _reconnectIntervalMs;
    unsigned long _lastReconnectAttempt;
    bool          _connected;
    bool          _connecting;
};
