#include "safety_manager.h"

SafetyManager::SafetyManager(RelayActuator& pump,
                             FlowSensor& flow,
                             unsigned long dryRunTimeoutMs,
                             unsigned long maxRunTimeMs)
    : _pump(pump),
      _flow(flow),
      _dryRunTimeoutMs(dryRunTimeoutMs),
      _maxRunTimeMs(maxRunTimeMs),
      _autoIrrigationEnabled(false),
      _dryRunFault(false),
      _maxRuntimeFault(false) {}

void SafetyManager::clearFaults() {
    _dryRunFault = false;
    _maxRuntimeFault = false;
}

const char* SafetyManager::evaluateSafety(float currentMoisturePercent) {
    // -------------------------------------------------------------------------
    // Rule 1: Pump Burnout Dry-Run Protection
    // If pump is ON for > timeout and detected flow is essentially 0 -> SHUTDOWN
    // -------------------------------------------------------------------------
    if (_pump.isOn()) {
        unsigned long activeDuration = _pump.getActiveDurationMs();

        if (activeDuration >= _dryRunTimeoutMs) {
            if (_flow.getFlowRateLpm() < 0.1f) {
                _pump.turnOff();
                _dryRunFault = true;
                return "! DRY RUN FAULT !";
            }
        }

        // ---------------------------------------------------------------------
        // Rule 2: Max Runtime Limit (Flood Protection)
        // ---------------------------------------------------------------------
        if (activeDuration >= _maxRunTimeMs) {
            _pump.turnOff();
            _maxRuntimeFault = true;
            return "! MAX RUNTIME !";
        }
    }

    // Return current fault message if already in fault state
    if (_dryRunFault) return "! DRY RUN FAULT !";
    if (_maxRuntimeFault) return "! MAX RUNTIME !";

    // -------------------------------------------------------------------------
    // Rule 3: Smart Auto-Irrigation Logic (When enabled and no faults)
    // -------------------------------------------------------------------------
    if (_autoIrrigationEnabled) {
        if (!_pump.isOn() && currentMoisturePercent < 25.0f && currentMoisturePercent >= 0.0f) {
            _pump.turnOn();
        } else if (_pump.isOn() && currentMoisturePercent >= 75.0f) {
            _pump.turnOff();
        }
    }

    return nullptr;
}
