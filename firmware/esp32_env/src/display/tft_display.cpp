#include "tft_display.h"
#include <SPI.h>

// High-contrast 16-bit RGB565 Color Palette
#define COLOR_BG        0x0841  // Deep slate background
#define COLOR_CARD_BG   0x18E3  // Dark surface container
#define COLOR_HEADER_BG 0x0287  // Header band
#define COLOR_TEXT_MAIN 0xFFFF  // Crisp white
#define COLOR_TEXT_MUTED 0xAD55 // Subtle grey
#define COLOR_TEMP      0xFA08  // Coral Orange (Temperature)
#define COLOR_HUMIDITY  0x07FF  // Sky Blue (Humidity)
#define COLOR_FLOW      0x07FD  // Cyan (Flow Rate)
#define COLOR_VOLUME    0x73DF  // Indigo / Purple (Water Volume)
#define COLOR_BORDER    0x39E7  // Card border
#define COLOR_ALERT     0xF800  // Bright Red (Fault)
#define COLOR_PUMP_ON   0x07E0  // Bright Green

TFTDisplayManager::TFTDisplayManager(int8_t csPin, int8_t dcPin, int8_t rstPin, int8_t blPin)
    : _csPin(csPin),
      _dcPin(dcPin),
      _rstPin(rstPin),
      _blPin(blPin),
      _tft35(nullptr),
      _gfx(nullptr),
      _driverType(TFTDriverType::ST7735_128x160),
      _lastTemp(-999.0f),
      _lastHum(-999.0f),
      _lastFlow(-999.0f),
      _lastVol(-999.0f),
      _lastPump(false),
      _lastFault(false),
      _lastUptime(0) {}

bool TFTDisplayManager::begin(TFTDriverType driver) {
    _driverType = driver;

    if (_blPin >= 0) {
        pinMode(_blPin, OUTPUT);
        digitalWrite(_blPin, HIGH);
    }

    // Hardware reset pulse to guarantee controller wake-up
    if (_rstPin >= 0) {
        pinMode(_rstPin, OUTPUT);
        digitalWrite(_rstPin, HIGH);
        delay(10);
        digitalWrite(_rstPin, LOW);
        delay(50);
        digitalWrite(_rstPin, HIGH);
        delay(100);
    }

    // Explicitly initialize ESP32 VSPI bus (SCK=18, MISO=-1, MOSI=23, CS=_csPin)
    SPI.begin(18, -1, 23, _csPin);

    _tft35 = new Adafruit_ST7735(&SPI, _csPin, _dcPin, _rstPin);
    _tft35->initR(INITR_BLACKTAB); // Standard 1.8" 128x160 TFT SPI
    _tft35->setRotation(3);        // Landscape 160x128
    _tft35->fillScreen(COLOR_BG);
    _gfx = _tft35;

    return (_gfx != nullptr);
}

void TFTDisplayManager::showWelcomeScreen(const char* deviceId, const char* version, int8_t buzzerPin, uint16_t durationMs) {
    if (!_gfx) return;

    int16_t w = _gfx->width();
    int16_t h = _gfx->height();

    _gfx->fillScreen(COLOR_BG);

    // Header Box
    _gfx->fillRoundRect(8, 8, w - 16, 44, 4, COLOR_CARD_BG);
    _gfx->drawRoundRect(8, 8, w - 16, 44, 4, COLOR_FLOW);

    _gfx->setTextSize(1);
    _gfx->setTextColor(COLOR_TEXT_MAIN);
    _gfx->setCursor(18, 14);
    _gfx->print("HYDROPONICS PLATFORM");

    _gfx->setTextColor(COLOR_HUMIDITY);
    _gfx->setCursor(18, 26);
    _gfx->print("Node 1: Env & Actuator");

    _gfx->setTextColor(COLOR_TEXT_MUTED);
    _gfx->setCursor(18, 38);
    _gfx->printf("ID: %s | v%s", deviceId, version);

    // Progress Bar
    int barX = 14, barY = 75, barW = w - 28, barH = 8;
    _gfx->drawRect(barX - 1, barY - 1, barW + 2, barH + 2, COLOR_TEXT_MUTED);

    unsigned long start = millis();
    while (millis() - start < durationMs) {
        float progress = (float)(millis() - start) / (float)durationMs;
        int fillW = (int)(progress * barW);
        _gfx->fillRect(barX, barY, fillW, barH, COLOR_FLOW);

        if (buzzerPin >= 0 && (millis() - start) < 150) {
            digitalWrite(buzzerPin, HIGH);
        } else if (buzzerPin >= 0) {
            digitalWrite(buzzerPin, LOW);
        }
        delay(30);
    }
    if (buzzerPin >= 0) digitalWrite(buzzerPin, LOW);
}

void TFTDisplayManager::updateDashboard(float temperatureC, float humidityPercent, float flowRateLpm, float totalVolumeL, bool pumpOn, bool autoWater, bool faultActive, uint32_t uptimeSeconds) {
    if (!_gfx) return;

    int16_t w = _gfx->width();
    int16_t h = _gfx->height();

    // 1. Initial full layout draw if first run
    if (_lastTemp < -900.0f) {
        _gfx->fillScreen(COLOR_BG);

        // Top Header
        _gfx->fillRect(0, 0, w, 16, COLOR_HEADER_BG);
        _gfx->drawFastHLine(0, 16, w, COLOR_BORDER);
        _gfx->setTextSize(1);
        _gfx->setTextColor(COLOR_TEXT_MAIN);
        _gfx->setCursor(4, 4);
        _gfx->print("HYDROPONICS | NODE 1: ENV");

        // 2x2 Grid Backgrounds
        // Card 1: Top-Left (Temp)
        _gfx->fillRoundRect(2, 19, 76, 44, 3, COLOR_CARD_BG);
        _gfx->drawRoundRect(2, 19, 76, 44, 3, COLOR_BORDER);
        _gfx->setTextColor(COLOR_TEMP);
        _gfx->setCursor(6, 23);
        _gfx->print("AIR TEMP");

        // Card 2: Top-Right (Humidity)
        _gfx->fillRoundRect(82, 19, 76, 44, 3, COLOR_CARD_BG);
        _gfx->drawRoundRect(82, 19, 76, 44, 3, COLOR_BORDER);
        _gfx->setTextColor(COLOR_HUMIDITY);
        _gfx->setCursor(86, 23);
        _gfx->print("HUMIDITY");

        // Card 3: Bottom-Left (Flow Rate)
        _gfx->fillRoundRect(2, 66, 76, 44, 3, COLOR_CARD_BG);
        _gfx->drawRoundRect(2, 66, 76, 44, 3, COLOR_BORDER);
        _gfx->setTextColor(COLOR_FLOW);
        _gfx->setCursor(6, 70);
        _gfx->print("FLOW L/M");

        // Card 4: Bottom-Right (Total Volume)
        _gfx->fillRoundRect(82, 66, 76, 44, 3, COLOR_CARD_BG);
        _gfx->drawRoundRect(82, 66, 76, 44, 3, COLOR_BORDER);
        _gfx->setTextColor(COLOR_VOLUME);
        _gfx->setCursor(86, 70);
        _gfx->print("VOLUME L");

        // Bottom Footer Bar
        _gfx->fillRect(0, 113, w, 15, COLOR_HEADER_BG);
        _gfx->drawFastHLine(0, 112, w, COLOR_BORDER);
    }

    // 2. Card 1: Air Temp
    if (temperatureC != _lastTemp) {
        _lastTemp = temperatureC;
        _gfx->fillRect(6, 36, 68, 22, COLOR_CARD_BG);
        _gfx->setTextSize(2);
        _gfx->setTextColor(COLOR_TEXT_MAIN);
        _gfx->setCursor(8, 38);
        if (isnan(temperatureC)) {
            _gfx->print("--.-");
        } else {
            _gfx->printf("%.1f", temperatureC);
        }
        _gfx->setTextSize(1);
        _gfx->print("C");
    }

    // 3. Card 2: Humidity
    if (humidityPercent != _lastHum) {
        _lastHum = humidityPercent;
        _gfx->fillRect(86, 36, 68, 22, COLOR_CARD_BG);
        _gfx->setTextSize(2);
        _gfx->setTextColor(COLOR_TEXT_MAIN);
        _gfx->setCursor(88, 38);
        if (isnan(humidityPercent)) {
            _gfx->print("--.-");
        } else {
            _gfx->printf("%.1f", humidityPercent);
        }
        _gfx->setTextSize(1);
        _gfx->print("%");
    }

    // 4. Card 3: Flow Rate
    if (flowRateLpm != _lastFlow) {
        _lastFlow = flowRateLpm;
        _gfx->fillRect(6, 83, 68, 22, COLOR_CARD_BG);
        _gfx->setTextSize(2);
        _gfx->setTextColor(COLOR_TEXT_MAIN);
        _gfx->setCursor(8, 85);
        _gfx->printf("%.2f", flowRateLpm);
    }

    // 5. Card 4: Total Volume
    if (totalVolumeL != _lastVol) {
        _lastVol = totalVolumeL;
        _gfx->fillRect(86, 83, 68, 22, COLOR_CARD_BG);
        _gfx->setTextSize(2);
        _gfx->setTextColor(COLOR_TEXT_MAIN);
        _gfx->setCursor(88, 85);
        _gfx->printf("%.2f", totalVolumeL);
    }

    // 6. Bottom Footer Status Bar
    if (pumpOn != _lastPump || faultActive != _lastFault || uptimeSeconds != _lastUptime) {
        _lastPump = pumpOn;
        _lastFault = faultActive;
        _lastUptime = uptimeSeconds;

        _gfx->fillRect(0, 113, w, 15, COLOR_HEADER_BG);
        _gfx->setTextSize(1);
        
        if (faultActive) {
            _gfx->setTextColor(COLOR_ALERT);
            _gfx->setCursor(4, 117);
            _gfx->print("! DRY-RUN LOCKOUT !");
        } else {
            // Pump status
            _gfx->setCursor(4, 117);
            if (pumpOn) {
                _gfx->setTextColor(COLOR_PUMP_ON);
                _gfx->print("PUMP: ON");
            } else {
                _gfx->setTextColor(COLOR_TEXT_MUTED);
                _gfx->print("PUMP: OFF");
            }

            // Auto mode
            _gfx->setCursor(72, 117);
            if (autoWater) {
                _gfx->setTextColor(COLOR_FLOW);
                _gfx->print("[AUTO]");
            } else {
                _gfx->setTextColor(COLOR_TEXT_MUTED);
                _gfx->print("[MANUAL]");
            }

            // Uptime
            _gfx->setCursor(120, 117);
            _gfx->setTextColor(COLOR_TEXT_MUTED);
            _gfx->printf("%lus", (unsigned long)uptimeSeconds);
        }
    }
}

void TFTDisplayManager::showStatusMessage(const char* message) {
    if (!_gfx) return;
    int16_t w = _gfx->width();
    _gfx->fillRect(0, 113, w, 15, COLOR_HEADER_BG);
    _gfx->setTextSize(1);
    _gfx->setTextColor(COLOR_TEMP);
    _gfx->setCursor(4, 117);
    _gfx->print(message);
}
