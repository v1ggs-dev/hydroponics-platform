#pragma once

#include <Arduino.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ST7735.h>

enum class TFTDriverType {
    ST7735_128x160,
    ST7735_128x128
};

class TFTDisplayManager {
public:
    TFTDisplayManager(int8_t csPin, int8_t dcPin, int8_t rstPin, int8_t blPin = -1);
    ~TFTDisplayManager() = default;

    bool begin(TFTDriverType driver = TFTDriverType::ST7735_128x160);
    
    // UI Update functions
    void showWelcomeScreen(const char* deviceId, const char* version, int8_t buzzerPin = -1, uint16_t durationMs = 3000);
    void updateDashboard(float temperatureC, float humidityPercent, float flowRateLpm, float totalVolumeL, bool pumpOn, bool autoWater, bool faultActive, uint32_t uptimeSeconds);
    void showStatusMessage(const char* message);

private:
    int8_t _csPin;
    int8_t _dcPin;
    int8_t _rstPin;
    int8_t _blPin;
    
    Adafruit_ST7735* _tft35;
    Adafruit_GFX*    _gfx;
    TFTDriverType    _driverType;

    // Previous values to avoid flickering full redraws
    float _lastTemp;
    float _lastHum;
    float _lastFlow;
    float _lastVol;
    bool  _lastPump;
    bool  _lastFault;
    uint32_t _lastUptime;
};
