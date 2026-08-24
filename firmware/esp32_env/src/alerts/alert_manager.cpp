#include "alert_manager.h"

// Alert timing definitions (in milliseconds)
#define BOOT_BEEP_LEN           80
#define BOOT_PAUSE_LEN          60
#define HIGH_TEMP_REPEAT_MS     12000

AlertManager::AlertManager(uint8_t buzzerPin)
    : _buzzerPin(buzzerPin),
      _activeAlert(AlertType::NONE),
      _lastPatternTriggerTime(0),
      _patternStartTime(0),
      _beepStep(0),
      _isBeeping(false) {}

void AlertManager::begin() {
    pinMode(_buzzerPin, OUTPUT);
    setOutputState(false);
}

void AlertManager::setOutputState(bool state) {
    digitalWrite(_buzzerPin, state ? HIGH : LOW);
}

void AlertManager::triggerBootChime() {
    startPattern(AlertType::BOOT_READY, millis());
}

void AlertManager::startPattern(AlertType type, unsigned long nowMs) {
    _activeAlert = type;
    _patternStartTime = nowMs;
    _beepStep = 0;
    _isBeeping = true;
    setOutputState(true);
}

const char* AlertManager::evaluate(float tempC, float humPercent, const char* safetyFault) {
    unsigned long now = millis();
    AlertType newAlert = AlertType::NONE;
    const char* alertMessage = nullptr;

    // 0. Highest Priority: Safety Fault (Dry-Run / Max Runtime)
    if (safetyFault != nullptr) {
        newAlert = AlertType::DRY_RUN_FAULT;
        alertMessage = safetyFault;
    }
    // 1. High Temperature Heat Stress (> 34.0 C)
    else if (!isnan(tempC) && tempC > 34.0f) {
        newAlert = AlertType::HIGH_TEMP;
        alertMessage = "! HEAT STRESS !";
    }

    // Trigger repeating pattern when interval elapses
    if (newAlert != AlertType::NONE) {
        unsigned long repeatInterval = 10000;
        if (newAlert == AlertType::DRY_RUN_FAULT) repeatInterval = 5000;
        else if (newAlert == AlertType::HIGH_TEMP) repeatInterval = HIGH_TEMP_REPEAT_MS;

        if (_activeAlert != newAlert || (now - _lastPatternTriggerTime >= repeatInterval && !_isBeeping)) {
            _lastPatternTriggerTime = now;
            startPattern(newAlert, now);
        }
    } else {
        if (_activeAlert != AlertType::BOOT_READY) {
            _activeAlert = AlertType::NONE;
        }
    }

    return alertMessage;
}

void AlertManager::update(unsigned long nowMs) {
    if (!_isBeeping) return;

    unsigned long elapsed = nowMs - _patternStartTime;

    switch (_activeAlert) {
        case AlertType::BOOT_READY:
            // 2 Short ascending chirps: Beep(80ms) -> Pause(60ms) -> Beep(80ms) -> Done
            if (_beepStep == 0 && elapsed >= BOOT_BEEP_LEN) {
                setOutputState(false);
                _beepStep = 1;
            } else if (_beepStep == 1 && elapsed >= (BOOT_BEEP_LEN + BOOT_PAUSE_LEN)) {
                setOutputState(true);
                _beepStep = 2;
            } else if (_beepStep == 2 && elapsed >= (BOOT_BEEP_LEN * 2 + BOOT_PAUSE_LEN)) {
                setOutputState(false);
                _isBeeping = false;
                _activeAlert = AlertType::NONE;
            }
            break;

        case AlertType::DRY_RUN_FAULT:
            // 4 Rapid High-Urgency Beeps (50ms on, 50ms off)
            if (_beepStep == 0 && elapsed >= 50) {
                setOutputState(false);
                _beepStep = 1;
            } else if (_beepStep == 1 && elapsed >= 100) {
                setOutputState(true);
                _beepStep = 2;
            } else if (_beepStep == 2 && elapsed >= 150) {
                setOutputState(false);
                _beepStep = 3;
            } else if (_beepStep == 3 && elapsed >= 200) {
                setOutputState(true);
                _beepStep = 4;
            } else if (_beepStep == 4 && elapsed >= 250) {
                setOutputState(false);
                _beepStep = 5;
            } else if (_beepStep == 5 && elapsed >= 300) {
                setOutputState(true);
                _beepStep = 6;
            } else if (_beepStep == 6 && elapsed >= 350) {
                setOutputState(false);
                _isBeeping = false;
            }
            break;

        case AlertType::HIGH_TEMP:
            // 2 Medium Beeps: 180ms on, 100ms off (2 cycles)
            if (_beepStep == 0 && elapsed >= 180) {
                setOutputState(false);
                _beepStep = 1;
            } else if (_beepStep == 1 && elapsed >= 280) {
                setOutputState(true);
                _beepStep = 2;
            } else if (_beepStep == 2 && elapsed >= 460) {
                setOutputState(false);
                _isBeeping = false;
            }
            break;

        case AlertType::NONE:
        default:
            setOutputState(false);
            _isBeeping = false;
            break;
    }
}
