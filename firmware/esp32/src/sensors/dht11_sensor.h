#pragma once

#include "sensor_interface.h"
#include <DHTesp.h>

class DHT11Sensor : public ISensor {
public:
    explicit DHT11Sensor(uint8_t pin, const char* sensorId = "dht11-01");
    ~DHT11Sensor() override = default;

    bool begin() override;
    bool sample() override;
    const char* getSensorId() const override { return _sensorId; }
    bool isConnected() const override { return _connected; }

    float getTemperature() const { return _temperature; }
    float getHumidity() const { return _humidity; }
    const char* getStatusString() const { return _statusString; }

    // Populate normalized measurements into output array
    size_t getMeasurements(Measurement outMeasurements[], size_t maxCount) const;

private:
    uint8_t _pin;
    const char* _sensorId;
    DHTesp _dht;

    float _temperature;
    float _humidity;
    const char* _statusString;
    bool _connected;
    unsigned long _lastSampleTime;
};
