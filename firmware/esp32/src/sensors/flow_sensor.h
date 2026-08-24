#pragma once

#include "sensor_interface.h"

class FlowSensor : public ISensor {
public:
    explicit FlowSensor(uint8_t pulsePin,
                        const char* sensorId = "flow-01",
                        float calibrationFactor = 7.5f,
                        float pulsesPerLiter = 450.0f);
    ~FlowSensor() override = default;

    bool begin() override;
    bool sample() override;
    const char* getSensorId() const override { return _sensorId; }
    bool isConnected() const override { return _connected; }

    // Flow getters
    float getFlowRateLpm() const { return _flowRateLpm; }
    float getTotalLiters() const { return _totalLiters; }
    uint32_t getTotalPulses() const { return _totalPulses; }

    // Reset accumulated volume
    void resetTotalVolume();

    // Populate normalized measurements into output array
    size_t getMeasurements(Measurement outMeasurements[], size_t maxCount) const;

    // Static ISR routine
    static void IRAM_ATTR handlePulseInterrupt();

private:
    uint8_t _pulsePin;
    const char* _sensorId;
    float _calibrationFactor;
    float _pulsesPerLiter;

    float _flowRateLpm;
    float _totalLiters;
    uint32_t _totalPulses;
    unsigned long _lastSampleTime;
    bool _connected;

    static volatile uint32_t _isrPulseCount;
    static volatile unsigned long _lastIsrMicros;
    static portMUX_TYPE _mux;
};
