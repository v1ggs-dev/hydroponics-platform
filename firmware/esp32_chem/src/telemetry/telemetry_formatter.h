#pragma once

#include <Arduino.h>
#include "../sensors/sensor_interface.h"

class TelemetryFormatter {
public:
    static String formatTelemetryJson(
        const char* deviceId,
        uint32_t messageSequence,
        uint32_t uptimeSeconds,
        const Measurement measurements[],
        size_t measurementCount
    );

    static String formatHeartbeatJson(
        const char* deviceId,
        const char* firmwareVersion,
        uint32_t uptimeSeconds,
        uint32_t freeHeapBytes
    );
};
