#pragma once

#include <Arduino.h>

enum class AlertType {
    NONE,
    BOOT_READY,
    LOW_MOISTURE,
    HIGH_TEMP,
    TDS_OUT_OF_BOUNDS,
    DRY_RUN_FAULT
};

class AlertManager {
public:
    AlertManager(uint8_t buzzerPin, uint8_t ledPin);
    ~AlertManager() = default;

    void begin();

    // Trigger explicit chimes
    void triggerBootChime();

    // Evaluates thresholds and sets active alarm state
    // Returns a status string to display on TFT (e.g. "ALERT: LOW MOISTURE" or nullptr if OK)
    const char* evaluate(float tempC, float humPercent, float tdsPpm, float moistPercent, const char* safetyFault = nullptr);

    // Non-blocking update loop (call every cycle)
    void update(unsigned long nowMs);

    // State inspection
    bool isAlarmActive() const { return _activeAlert != AlertType::NONE && _activeAlert != AlertType::BOOT_READY; }
    AlertType getActiveAlertType() const { return _activeAlert; }

private:
    uint8_t _buzzerPin;
    uint8_t _ledPin;

    AlertType _activeAlert;
    unsigned long _lastPatternTriggerTime;
    unsigned long _patternStartTime;
    uint8_t _beepStep;
    bool _isBeeping;

    void setOutputState(bool state);
    void startPattern(AlertType type, unsigned long nowMs);
};
