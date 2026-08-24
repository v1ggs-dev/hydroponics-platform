#include "flow_sensor.h"

volatile uint32_t FlowSensor::_isrPulseCount = 0;
volatile unsigned long FlowSensor::_lastIsrMicros = 0;
portMUX_TYPE FlowSensor::_mux = portMUX_INITIALIZER_UNLOCKED;

void IRAM_ATTR FlowSensor::handlePulseInterrupt() {
    unsigned long nowMicros = micros();
    // Debounce filter: minimum 1500us between pulses (max ~660Hz = 88 L/min)
    if (nowMicros - _lastIsrMicros >= 1500) {
        _lastIsrMicros = nowMicros;
        portENTER_CRITICAL_ISR(&_mux);
        _isrPulseCount++;
        portEXIT_CRITICAL_ISR(&_mux);
    }
}

FlowSensor::FlowSensor(uint8_t pulsePin, const char* sensorId, float calibrationFactor, float pulsesPerLiter)
    : _pulsePin(pulsePin),
      _sensorId(sensorId),
      _calibrationFactor(calibrationFactor),
      _pulsesPerLiter(pulsesPerLiter),
      _flowRateLpm(0.0f),
      _totalLiters(0.0f),
      _totalPulses(0),
      _lastSampleTime(0),
      _connected(false) {}

bool FlowSensor::begin() {
    pinMode(_pulsePin, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(_pulsePin), FlowSensor::handlePulseInterrupt, RISING);
    _lastSampleTime = millis();
    _connected = true;
    return true;
}

void FlowSensor::resetTotalVolume() {
    _totalLiters = 0.0f;
    _totalPulses = 0;
}

bool FlowSensor::sample() {
    unsigned long now = millis();
    unsigned long elapsedMs = now - _lastSampleTime;

    if (elapsedMs < 500) {
        return true; // Too short interval, preserve current rate
    }

    uint32_t pulses = 0;
    portENTER_CRITICAL(&_mux);
    pulses = _isrPulseCount;
    _isrPulseCount = 0;
    portEXIT_CRITICAL(&_mux);

    _lastSampleTime = now;
    _totalPulses += pulses;

    float elapsedSeconds = (float)elapsedMs / 1000.0f;

    // Flow rate in L/min: Frequency (Hz) / CalibrationFactor
    // Frequency = pulses / elapsedSeconds
    float pulseFrequency = (float)pulses / elapsedSeconds;
    _flowRateLpm = pulseFrequency / _calibrationFactor;

    if (_flowRateLpm < 0.05f) {
        _flowRateLpm = 0.0f;
    }

    // Accumulated volume in Liters: pulses / pulsesPerLiter
    float addedVolume = (float)pulses / _pulsesPerLiter;
    _totalLiters += addedVolume;

    return true;
}

size_t FlowSensor::getMeasurements(Measurement outMeasurements[], size_t maxCount) const {
    if (maxCount < 2) {
        if (maxCount == 1) {
            outMeasurements[0] = {
                .sensorId = _sensorId,
                .metric = "flow_rate",
                .value = _flowRateLpm,
                .unit = "L/min",
                .quality = Quality::GOOD,
                .isValid = true
            };
            return 1;
        }
        return 0;
    }

    // 1. Flow Rate (L/min)
    outMeasurements[0] = {
        .sensorId = _sensorId,
        .metric = "flow_rate",
        .value = _flowRateLpm,
        .unit = "L/min",
        .quality = Quality::GOOD,
        .isValid = true
    };

    // 2. Accumulated Volume (L)
    outMeasurements[1] = {
        .sensorId = _sensorId,
        .metric = "water_volume",
        .value = _totalLiters,
        .unit = "L",
        .quality = Quality::GOOD,
        .isValid = true
    };

    return 2;
}
