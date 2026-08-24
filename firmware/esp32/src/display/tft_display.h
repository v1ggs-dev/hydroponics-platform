#pragma once

#include <Arduino.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ST7789.h>
#include <Adafruit_ST7735.h>

enum class TFTDriverType {
    ST7789_240x240,
    ST7789_135x240,
    ST7735_128x160,
    ST7735_128x128
};

class TFTDisplayManager {
public:
    TFTDisplayManager(int8_t csPin, int8_t dcPin, int8_t rstPin, int8_t blPin = -1);
    ~TFTDisplayManager() = default;

    bool begin(TFTDriverType driver = TFTDriverType::ST7789_240x240);
    
    // UI Update functions
    void showWelcomeScreen(const char* deviceId, const char* version, uint8_t ledPin, int8_t buzzerPin = -1, uint16_t durationMs = 6000);
    void drawHeader(const char* deviceId, const char* version, bool wifiOk = false, bool mqttOk = false);
    void updateDashboard(float temperatureC, float humidityPercent, float tdsPpm, float moisturePercent, bool pumpOn, float flowRateLpm, bool wifiOk, bool mqttOk, uint32_t uptimeSeconds);
    void showStatusMessage(const char* message);

private:
    int8_t _csPin;
    int8_t _dcPin;
    int8_t _rstPin;
    int8_t _blPin;
    
    Adafruit_ST7789* _tft89;
    Adafruit_ST7735* _tft35;
    Adafruit_GFX*    _gfx;
    TFTDriverType    _driverType;

    // Previous values to avoid flickering full redraws
    float _lastTemp;
    float _lastHum;
    float _lastTds;
    float _lastMoist;
    uint32_t _lastUptime;
};
