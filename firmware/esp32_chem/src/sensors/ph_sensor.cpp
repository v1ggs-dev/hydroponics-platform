#include "ph_sensor.h"
#include <algorithm>

PHSensor::PHSensor(uint8_t adcPin, const char* sensorId, float vref, float neutralV, float slope)
    : _adcPin(adcPin),
      _sensorId(sensorId),
      _vref(vref),
      _neutralV(neutralV),
      _slope(slope),
      _waterTemperature(25.0f),
      _rawAdc(0),
      _voltage(0.0f),
      _phValue(7.0f),
      _connected(false) {}

bool PHSensor::begin() {
    pinMode(_adcPin, INPUT);
    // Initial sample
    return sample();
}

void PHSensor::setWaterTemperature(float temperatureC) {
    if (!isnan(temperatureC) && temperatureC > 0.0f && temperatureC < 60.0f) {
        _waterTemperature = temperatureC;
    }
}

uint16_t PHSensor::readMedianAdc(uint8_t sampleCount) {
    if (sampleCount == 0) return 0;
    
    uint16_t samples[sampleCount];
    for (uint8_t i = 0; i < sampleCount; i++) {
        samples[i] = analogRead(_adcPin);
        delayMicroseconds(500);
    }

    std::sort(samples, samples + sampleCount);
    return samples[sampleCount / 2];
}

bool PHSensor::sample() {
    _rawAdc = readMedianAdc(30);

    // Convert raw 12-bit ADC reading (0-4095) to voltage (0-3.3V)
    _voltage = ((float)_rawAdc / 4095.0f) * _vref;

    // Standard Nernst Slope with Temperature Compensation
    // Slope changes by ~0.1984 mV/pH per degree C deviation from 25C
    float tempCorrectedSlope = _slope * (1.0f + 0.003f * (_waterTemperature - 25.0f));
    if (tempCorrectedSlope < 0.05f) tempCorrectedSlope = _slope;

    // Calculate pH: pH = 7.0 + (V_neutral - V_adc) / Slope
    float calculatedPH = 7.0f + ((_neutralV - _voltage) / tempCorrectedSlope);

    // Constrain to physical pH boundaries (0.00 to 14.00)
    _phValue = constrain(calculatedPH, 0.0f, 14.0f);

    _connected = (_rawAdc > 50 && _rawAdc < 4050); // Connected if not pegged to rail

    return _connected;
}

size_t PHSensor::getMeasurements(Measurement outMeasurements[], size_t maxCount) const {
    if (maxCount < 1) return 0;

    outMeasurements[0].sensorId = _sensorId;
    outMeasurements[0].metric = "ph";
    outMeasurements[0].value = _phValue;
    outMeasurements[0].unit = "pH";
    outMeasurements[0].quality = _connected ? Quality::GOOD : Quality::BAD;
    outMeasurements[0].isValid = _connected;

    return 1;
}
