#include "dht11_sensor.h"

DHT11Sensor::DHT11Sensor(uint8_t pin, const char* sensorId)
    : _pin(pin),
      _sensorId(sensorId),
      _temperature(NAN),
      _humidity(NAN),
      _statusString("NOT_INITIALIZED"),
      _connected(false),
      _lastSampleTime(0) {}

bool DHT11Sensor::begin() {
    _dht.setup(_pin, DHTesp::DHT11);
    delay(50);
    // Perform initial reading
    return sample();
}

bool DHT11Sensor::sample() {
    _lastSampleTime = millis();
    
    TempAndHumidity reading = _dht.getTempAndHumidity();
    _statusString = _dht.getStatusString();
    
    if (_dht.getStatus() == DHTesp::ERROR_NONE) {
        if (!isnan(reading.temperature) && !isnan(reading.humidity) &&
            reading.temperature >= -20.0f && reading.temperature <= 80.0f &&
            reading.humidity >= 0.0f && reading.humidity <= 100.0f) {
            
            _temperature = reading.temperature;
            _humidity = reading.humidity;
            _connected = true;
            return true;
        }
    }

    _temperature = NAN;
    _humidity = NAN;
    _connected = false;
    return false;
}

size_t DHT11Sensor::getMeasurements(Measurement outMeasurements[], size_t maxCount) const {
    if (maxCount < 2) {
        return 0;
    }

    bool valid = _connected && !isnan(_temperature) && !isnan(_humidity);

    // Metric 1: air_temperature (DHT11 is strictly air temp, not water temp)
    outMeasurements[0] = {
        .sensorId = _sensorId,
        .metric = "air_temperature",
        .value = _temperature,
        .unit = "C",
        .quality = valid ? Quality::GOOD : Quality::BAD,
        .isValid = valid
    };

    // Metric 2: humidity
    outMeasurements[1] = {
        .sensorId = _sensorId,
        .metric = "humidity",
        .value = _humidity,
        .unit = "%",
        .quality = valid ? Quality::GOOD : Quality::BAD,
        .isValid = valid
    };

    return 2;
}
