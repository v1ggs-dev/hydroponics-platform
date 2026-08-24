#pragma once

#include <Arduino.h>
#include "../actuators/relay_actuator.h"
#include "../sensors/flow_sensor.h"

class SafetyManager {
public:
    SafetyManager(RelayActuator& pump,
                  FlowSensor& flow,
                  unsigned long dryRunTimeoutMs = 8000,
                  unsigned long maxRunTimeMs = 300000);
    ~SafetyManager() = default;

    // Evaluates safety rules every loop cycle (non-blocking)
    // Returns a fault message if a safety rule was violated, or nullptr if safe
    const char* evaluateSafety(float currentMoisturePercent);

    // Auto-irrigation toggle
    void setAutoIrrigation(bool enabled) { _autoIrrigationEnabled = enabled; }
    bool isAutoIrrigationEnabled() const { return _autoIrrigationEnabled; }

    // Fault state inspection and reset
    bool hasDryRunFault() const { return _dryRunFault; }
    bool hasMaxRuntimeFault() const { return _maxRuntimeFault; }
    bool hasFault() const { return _dryRunFault || _maxRuntimeFault; }
    void clearFaults();

private:
    RelayActuator& _pump;
    FlowSensor&    _flow;
    unsigned long  _dryRunTimeoutMs;
    unsigned long  _maxRunTimeMs;

    bool _autoIrrigationEnabled;
    bool _dryRunFault;
    bool _maxRuntimeFault;
};
