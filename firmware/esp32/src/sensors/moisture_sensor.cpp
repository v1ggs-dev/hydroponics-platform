#include "moisture_sensor.h"
#include <algorithm>

MoistureSensor::MoistureSensor(uint8_t adcPin, const char* sensorId, float vref, uint16_t dryAdc, uint16_t wetAdc)
    : _adcPin(adcPin),
      _sensorId(sensorId),
      _vref(vref),
      _dryAdc(dryAdc),
      _wetAdc(wetAdc),
      _rawAdc(0),
      _voltage(0.0f),
      _moisturePercent(0.0f),
      _connected(false) {}

bool MoistureSensor::begin() {
    pinMode(_adcPin, INPUT);
    analogReadResolution(12);
    analogSetAttenuation(ADC_11db);
    return sample();
}

void MoistureSensor::setCalibration(uint16_t dryAdc, uint16_t wetAdc) {
    _dryAdc = dryAdc;
    _wetAdc = wetAdc;
}

uint16_t MoistureSensor::readMedianAdc(uint8_t sampleCount) {
    if (sampleCount == 0) return 0;

    const uint8_t maxSamples = 30;
    uint8_t count = sampleCount > maxSamples ? maxSamples : sampleCount;
    uint16_t buffer[maxSamples];

    for (uint8_t i = 0; i < count; ++i) {
        buffer[i] = analogRead(_adcPin);
        delayMicroseconds(500);
    }

    std::sort(buffer, buffer + count);
    return buffer[count / 2];
}

bool MoistureSensor::sample() {
    _rawAdc = readMedianAdc(30);

    // Convert raw ADC (0-4095) to Voltage (0 - 3.3V)
    _voltage = ((float)_rawAdc / 4095.0f) * _vref;

    // Calculate percentage based on calibration points
    // Capacitive sensors output HIGH ADC when DRY, LOW ADC when WET
    float percent = 0.0f;
    if (_dryAdc > _wetAdc) {
        percent = ((float)(_dryAdc - _rawAdc) / (float)(_dryAdc - _wetAdc)) * 100.0f;
    } else if (_wetAdc > _dryAdc) {
        percent = ((float)(_rawAdc - _dryAdc) / (float)(_wetAdc - _dryAdc)) * 100.0f;
    }

    // Clamp to 0.0% - 100.0%
    if (percent < 0.0f) percent = 0.0f;
    if (percent > 100.0f) percent = 100.0f;

    _moisturePercent = percent;
    _connected = true;
    return true;
}

size_t MoistureSensor::getMeasurements(Measurement outMeasurements[], size_t maxCount) const {
    if (maxCount < 1) {
        return 0;
    }

    outMeasurements[0] = {
        .sensorId = _sensorId,
        .metric = "substrate_moisture",
        .value = _moisturePercent,
        .unit = "%",
        .quality = _connected ? Quality::GOOD : Quality::BAD,
        .isValid = _connected
    };

    return 1;
}
