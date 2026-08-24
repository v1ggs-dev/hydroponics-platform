#pragma once

#include <Arduino.h>

class RelayActuator {
public:
    explicit RelayActuator(uint8_t relayPin,
                           const char* actuatorId = "pump-01",
                           const char* actuatorType = "pump",
                           bool activeLow = true);
    ~RelayActuator() = default;

    void begin();
    void turnOn();
    void turnOff();
    void toggle();
    void setState(bool on);
    void setPolarity(bool activeLow);
    void togglePolarity();

    // Getters
    bool isOn() const { return _isOn; }
    bool isActiveLow() const { return _activeLow; }
    const char* getActuatorId() const { return _actuatorId; }
    const char* getType() const { return _actuatorType; }
    const char* getStateString() const { return _isOn ? "ON" : "OFF"; }
    unsigned long getActiveDurationMs() const;

private:
    uint8_t _relayPin;
    const char* _actuatorId;
    const char* _actuatorType;
    bool _activeLow;
    bool _isOn;
    unsigned long _turnOnTimeMs;

    void applyPhysicalState();
};
