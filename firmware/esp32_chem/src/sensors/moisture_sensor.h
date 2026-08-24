#pragma once

#include "sensor_interface.h"

class MoistureSensor : public ISensor {
public:
    explicit MoistureSensor(uint8_t adcPin,
                            const char* sensorId = "moisture-01",
                            float vref = 3.3f,
                            uint16_t dryAdc = 3200,
                            uint16_t wetAdc = 1300);
    ~MoistureSensor() override = default;

    bool begin() override;
    bool sample() override;
    const char* getSensorId() const override { return _sensorId; }
    bool isConnected() const override { return _connected; }

    // Calibration setters
    void setCalibration(uint16_t dryAdc, uint16_t wetAdc);

    // Getters
    float getMoisturePercent() const { return _moisturePercent; }
    float getRawVoltage() const { return _voltage; }
    uint16_t getRawAdc() const { return _rawAdc; }

    // Populate normalized measurements into output array
    size_t getMeasurements(Measurement outMeasurements[], size_t maxCount) const;

private:
    uint8_t _adcPin;
    const char* _sensorId;
    float _vref;
    uint16_t _dryAdc;
    uint16_t _wetAdc;

    uint16_t _rawAdc;
    float _voltage;
    float _moisturePercent;
    bool _connected;

    // Helper: median filter for stable ADC acquisition
    uint16_t readMedianAdc(uint8_t sampleCount = 30);
};
