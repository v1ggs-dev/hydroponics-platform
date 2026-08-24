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
    void showWelcomeScreen(const char* deviceId, const char* version, uint16_t durationMs = 2500);
    void updateDashboard(float phValue, float tdsPpm, float moisturePercent, float phVoltage, uint32_t uptimeSeconds);
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
    float _lastPH;
    float _lastTds;
    float _lastMoist;
    float _lastPhVolts;
    uint32_t _lastUptime;
};
