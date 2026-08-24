#include "relay_actuator.h"

RelayActuator::RelayActuator(uint8_t relayPin, const char* actuatorId, const char* actuatorType, bool activeLow)
    : _relayPin(relayPin),
      _actuatorId(actuatorId),
      _actuatorType(actuatorType),
      _activeLow(activeLow),
      _isOn(false),
      _turnOnTimeMs(0) {}

void RelayActuator::applyPhysicalState() {
    pinMode(_relayPin, OUTPUT);
    bool pinState = _activeLow ? !_isOn : _isOn;
    digitalWrite(_relayPin, pinState ? HIGH : LOW);
}

void RelayActuator::begin() {
    _isOn = false;
    _turnOnTimeMs = 0;
    applyPhysicalState(); // Safe startup: guaranteed OFF
}

void RelayActuator::turnOn() {
    if (!_isOn) {
        _isOn = true;
        _turnOnTimeMs = millis();
        applyPhysicalState();
    }
}

void RelayActuator::turnOff() {
    if (_isOn) {
        _isOn = false;
        _turnOnTimeMs = 0;
        applyPhysicalState();
    }
}

void RelayActuator::toggle() {
    if (_isOn) {
        turnOff();
    } else {
        turnOn();
    }
}

void RelayActuator::setState(bool on) {
    if (on) {
        turnOn();
    } else {
        turnOff();
    }
}

void RelayActuator::setPolarity(bool activeLow) {
    _activeLow = activeLow;
    applyPhysicalState();
}

void RelayActuator::togglePolarity() {
    _activeLow = !_activeLow;
    applyPhysicalState();
}

unsigned long RelayActuator::getActiveDurationMs() const {
    if (!_isOn) return 0;
    return millis() - _turnOnTimeMs;
}
