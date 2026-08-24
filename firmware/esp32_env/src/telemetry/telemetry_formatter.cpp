#include "telemetry_formatter.h"
#include <ArduinoJson.h>

String TelemetryFormatter::formatTelemetryJson(
    const char* deviceId,
    uint32_t messageSequence,
    uint32_t uptimeSeconds,
    const Measurement measurements[],
    size_t measurementCount
) {
    JsonDocument doc;

    doc["version"] = 1;
    
    char msgIdBuffer[32];
    snprintf(msgIdBuffer, sizeof(msgIdBuffer), "msg-%s-%lu", deviceId, (unsigned long)messageSequence);
    doc["messageId"] = msgIdBuffer;
    
    doc["deviceId"] = deviceId;
    doc["type"] = "telemetry";
    doc["uptimeSeconds"] = uptimeSeconds;

    JsonArray measArray = doc["measurements"].to<JsonArray>();

    for (size_t i = 0; i < measurementCount; ++i) {
        const Measurement& m = measurements[i];
        JsonObject obj = measArray.add<JsonObject>();
        obj["sensorId"] = m.sensorId;
        obj["metric"] = m.metric;
        
        if (m.isValid) {
            obj["value"] = serialized(String(m.value, 1)); // 1 decimal place precision
        } else {
            obj["value"] = nullptr;
        }

        obj["unit"] = m.unit;
        obj["quality"] = qualityToString(m.quality);
    }

    String output;
    serializeJson(doc, output);
    return output;
}

String TelemetryFormatter::formatHeartbeatJson(
    const char* deviceId,
    const char* firmwareVersion,
    uint32_t uptimeSeconds,
    uint32_t freeHeapBytes
) {
    JsonDocument doc;

    doc["version"] = 1;
    doc["deviceId"] = deviceId;
    doc["type"] = "status";
    doc["status"] = "ONLINE";
    doc["firmwareVersion"] = firmwareVersion;
    doc["uptimeSeconds"] = uptimeSeconds;
    doc["freeHeap"] = freeHeapBytes;

    String output;
    serializeJson(doc, output);
    return output;
}
