#pragma once

#include "sensor_interface.h"

class PHSensor : public ISensor {
public:
    explicit PHSensor(uint8_t adcPin, const char* sensorId = "ph-01", float vref = 3.3f, float neutralV = 1.65f, float slope = 0.18f);
    ~PHSensor() override = default;

    bool begin() override;
    bool sample() override;
    const char* getSensorId() const override { return _sensorId; }
    bool isConnected() const override { return _connected; }

    // Temperature compensation
    void setWaterTemperature(float temperatureC);
    float getWaterTemperature() const { return _waterTemperature; }

    // Measurement getters
    float getPH() const { return _phValue; }
    float getRawVoltage() const { return _voltage; }
    uint16_t getRawAdc() const { return _rawAdc; }

    // Populate normalized measurements into output array
    size_t getMeasurements(Measurement outMeasurements[], size_t maxCount) const;

private:
    uint8_t _adcPin;
    const char* _sensorId;
    float _vref;
    float _neutralV;
    float _slope;

    float _waterTemperature;
    uint16_t _rawAdc;
    float _voltage;
    float _phValue;
    bool _connected;

    // Helper: median filter for stable ADC acquisition
    uint16_t readMedianAdc(uint8_t sampleCount = 30);
};
