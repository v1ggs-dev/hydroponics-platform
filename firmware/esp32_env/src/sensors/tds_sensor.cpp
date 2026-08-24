#include "tds_sensor.h"
#include <algorithm>

TDSSensor::TDSSensor(uint8_t adcPin, const char* sensorId, float vref)
    : _adcPin(adcPin),
      _sensorId(sensorId),
      _vref(vref),
      _waterTemperature(25.0f), // Default calibration temperature: 25.0 C
      _rawAdc(0),
      _voltage(0.0f),
      _tdsValue(0.0f),
      _connected(false) {}

bool TDSSensor::begin() {
    pinMode(_adcPin, INPUT);
    // Configure 12-bit resolution (0 - 4095)
    analogReadResolution(12);
    // 11dB attenuation gives full 0 - 3.3V range
    analogSetAttenuation(ADC_11db);
    return sample();
}

void TDSSensor::setWaterTemperature(float temperatureC) {
    if (!isnan(temperatureC) && temperatureC > 0.0f && temperatureC < 70.0f) {
        _waterTemperature = temperatureC;
    }
}

uint16_t TDSSensor::readMedianAdc(uint8_t sampleCount) {
    if (sampleCount == 0) return 0;
    
    // Static buffer to avoid dynamic heap allocation
    const uint8_t maxSamples = 30;
    uint8_t count = sampleCount > maxSamples ? maxSamples : sampleCount;
    uint16_t buffer[maxSamples];

    for (uint8_t i = 0; i < count; ++i) {
        buffer[i] = analogRead(_adcPin);
        delayMicroseconds(500); // 0.5ms interval between analog reads
    }

    std::sort(buffer, buffer + count);
    return buffer[count / 2];
}

bool TDSSensor::sample() {
    _rawAdc = readMedianAdc(30);

    // Convert ADC value (0-4095) to Voltage (0 - 3.3V)
    _voltage = ((float)_rawAdc / 4095.0f) * _vref;

    // If voltage is essentially zero (below 0.02V noise floor), TDS is 0
    if (_voltage < 0.02f) {
        _tdsValue = 0.0f;
        _connected = true;
        return true;
    }

    // Standard temperature compensation formula:
    // CompensationCoefficient = 1.0 + 0.02 * (temperature - 25.0)
    float compensationCoefficient = 1.0f + 0.02f * (_waterTemperature - 25.0f);
    if (compensationCoefficient <= 0.1f) {
        compensationCoefficient = 1.0f;
    }

    // Temperature-compensated voltage
    float compensationVoltage = _voltage / compensationCoefficient;

    // Standard TDS polynomial conversion curve:
    // TDS = (133.42 * V^3 - 255.86 * V^2 + 857.39 * V) * 0.5
    float v = compensationVoltage;
    float calculatedTds = (133.42f * v * v * v - 255.86f * v * v + 857.39f * v) * 0.5f;

    if (calculatedTds < 0.0f) {
        calculatedTds = 0.0f;
    }

    _tdsValue = calculatedTds;
    _connected = true;
    return true;
}

size_t TDSSensor::getMeasurements(Measurement outMeasurements[], size_t maxCount) const {
    if (maxCount < 1) {
        return 0;
    }

    outMeasurements[0] = {
        .sensorId = _sensorId,
        .metric = "tds",
        .value = _tdsValue,
        .unit = "ppm",
        .quality = _connected ? Quality::GOOD : Quality::BAD,
        .isValid = _connected
    };

    return 1;
}
