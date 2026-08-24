#pragma once

#include <Arduino.h>

// =============================================================================
// Measurement Quality Enum
// =============================================================================
enum class Quality {
    GOOD,
    DEGRADED,
    BAD
};

inline const char* qualityToString(Quality q) {
    switch (q) {
        case Quality::GOOD:     return "GOOD";
        case Quality::DEGRADED: return "DEGRADED";
        case Quality::BAD:      return "BAD";
        default:                return "BAD";
    }
}

// =============================================================================
// Normalized Measurement Struct
// Reference: docs/protocols/TELEMETRY.md
// =============================================================================
struct Measurement {
    const char* sensorId;
    const char* metric;
    float value;
    const char* unit;
    Quality quality;
    bool isValid;
};

// =============================================================================
// Base Sensor Interface
// =============================================================================
class ISensor {
public:
    virtual ~ISensor() = default;
    virtual bool begin() = 0;
    virtual bool sample() = 0;
    virtual const char* getSensorId() const = 0;
    virtual bool isConnected() const = 0;
};
