#include "tft_display.h"
#include <SPI.h>

// High-contrast 16-bit RGB565 Color Palette
#define COLOR_BG        0x0841  // Deep slate background
#define COLOR_CARD_BG   0x18E3  // Dark surface container
#define COLOR_HEADER_BG 0x0287  // Header band
#define COLOR_TEXT_MAIN 0xFFFF  // Crisp white
#define COLOR_TEXT_MUTED 0xAD55 // Subtle grey
#define COLOR_PH        0xF81F  // Fuchsia / Magenta (pH Level)
#define COLOR_TDS       0x37E6  // Emerald Green (TDS)
#define COLOR_MOISTURE  0xFDC0  // Bright Amber / Gold (Moisture)
#define COLOR_VOLTS     0x07FD  // Cyan (Voltage)
#define COLOR_BORDER    0x39E7  // Card border
#define COLOR_ALERT     0xF800  // Bright Red (Fault)
#define COLOR_OPTIMAL   0x07E0  // Bright Green

TFTDisplayManager::TFTDisplayManager(int8_t csPin, int8_t dcPin, int8_t rstPin, int8_t blPin)
    : _csPin(csPin),
      _dcPin(dcPin),
      _rstPin(rstPin),
      _blPin(blPin),
      _tft35(nullptr),
      _gfx(nullptr),
      _driverType(TFTDriverType::ST7735_128x160),
      _lastPH(-999.0f),
      _lastTds(-999.0f),
      _lastMoist(-999.0f),
      _lastPhVolts(-999.0f),
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
    _tft35->initR(INITR_BLACKTAB);
    _tft35->setRotation(1); // Landscape 160x128 (Pins on Right side)
    _tft35->fillScreen(COLOR_BG);
    _gfx = _tft35;

    return (_gfx != nullptr);
}

void TFTDisplayManager::showWelcomeScreen(const char* deviceId, const char* version, uint16_t durationMs) {
    if (!_gfx) return;

    int16_t w = _gfx->width();
    int16_t h = _gfx->height();

    _gfx->fillScreen(COLOR_BG);

    // Header Box
    _gfx->fillRoundRect(8, 8, w - 16, 44, 4, COLOR_CARD_BG);
    _gfx->drawRoundRect(8, 8, w - 16, 44, 4, COLOR_PH);

    _gfx->setTextSize(1);
    _gfx->setTextColor(COLOR_TEXT_MAIN);
    _gfx->setCursor(18, 14);
    _gfx->print("HYDROPONICS PLATFORM");

    _gfx->setTextColor(COLOR_PH);
    _gfx->setCursor(18, 26);
    _gfx->print("Node 2: Water Chemistry");

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
        _gfx->fillRect(barX, barY, fillW, barH, COLOR_PH);
        delay(30);
    }
}

void TFTDisplayManager::updateDashboard(float phValue, float tdsPpm, float moisturePercent, float phVoltage, uint32_t uptimeSeconds) {
    if (!_gfx) return;

    int16_t w = _gfx->width();
    int16_t h = _gfx->height();

    // 1. Initial full layout draw if first run
    if (_lastPH < -900.0f) {
        _gfx->fillScreen(COLOR_BG);

        // Top Header
        _gfx->fillRect(0, 0, w, 16, COLOR_HEADER_BG);
        _gfx->drawFastHLine(0, 16, w, COLOR_BORDER);
        _gfx->setTextSize(1);
        _gfx->setTextColor(COLOR_TEXT_MAIN);
        _gfx->setCursor(4, 4);
        _gfx->print("HYDROPONICS | NODE 2: CHEM");

        // 2x2 Grid Backgrounds
        // Card 1: Top-Left (pH)
        _gfx->fillRoundRect(2, 19, 76, 44, 3, COLOR_CARD_BG);
        _gfx->drawRoundRect(2, 19, 76, 44, 3, COLOR_BORDER);
        _gfx->setTextColor(COLOR_PH);
        _gfx->setCursor(6, 23);
        _gfx->print("PH LEVEL");

        // Card 2: Top-Right (TDS)
        _gfx->fillRoundRect(82, 19, 76, 44, 3, COLOR_CARD_BG);
        _gfx->drawRoundRect(82, 19, 76, 44, 3, COLOR_BORDER);
        _gfx->setTextColor(COLOR_TDS);
        _gfx->setCursor(86, 23);
        _gfx->print("TDS PPM");

        // Card 3: Bottom-Left (Moisture)
        _gfx->fillRoundRect(2, 66, 76, 44, 3, COLOR_CARD_BG);
        _gfx->drawRoundRect(2, 66, 76, 44, 3, COLOR_BORDER);
        _gfx->setTextColor(COLOR_MOISTURE);
        _gfx->setCursor(6, 70);
        _gfx->print("MOISTURE");

        // Card 4: Bottom-Right (pH Sensor Raw Volts)
        _gfx->fillRoundRect(82, 66, 76, 44, 3, COLOR_CARD_BG);
        _gfx->drawRoundRect(82, 66, 76, 44, 3, COLOR_BORDER);
        _gfx->setTextColor(COLOR_VOLTS);
        _gfx->setCursor(86, 70);
        _gfx->print("PH VOLTS");

        // Bottom Footer Bar
        _gfx->fillRect(0, 113, w, 15, COLOR_HEADER_BG);
        _gfx->drawFastHLine(0, 112, w, COLOR_BORDER);
    }

    // 2. Card 1: pH Level
    if (phValue != _lastPH) {
        _lastPH = phValue;
        _gfx->fillRect(6, 36, 68, 22, COLOR_CARD_BG);
        _gfx->setTextSize(2);
        _gfx->setTextColor(COLOR_TEXT_MAIN);
        _gfx->setCursor(8, 38);
        if (isnan(phValue)) {
            _gfx->print("--.-");
        } else {
            _gfx->printf("%.2f", phValue);
        }
        _gfx->setTextSize(1);
        _gfx->print("pH");
    }

    // 3. Card 2: TDS ppm
    if (tdsPpm != _lastTds) {
        _lastTds = tdsPpm;
        _gfx->fillRect(86, 36, 68, 22, COLOR_CARD_BG);
        _gfx->setTextSize(2);
        _gfx->setTextColor(COLOR_TEXT_MAIN);
        _gfx->setCursor(88, 38);
        _gfx->printf("%.0f", tdsPpm);
        _gfx->setTextSize(1);
        _gfx->print("p");
    }

    // 4. Card 3: Moisture
    if (moisturePercent != _lastMoist) {
        _lastMoist = moisturePercent;
        _gfx->fillRect(6, 83, 68, 22, COLOR_CARD_BG);
        _gfx->setTextSize(2);
        _gfx->setTextColor(COLOR_TEXT_MAIN);
        _gfx->setCursor(8, 85);
        _gfx->printf("%.1f", moisturePercent);
        _gfx->setTextSize(1);
        _gfx->print("%");
    }

    // 5. Card 4: pH Volts
    if (phVoltage != _lastPhVolts) {
        _lastPhVolts = phVoltage;
        _gfx->fillRect(86, 83, 68, 22, COLOR_CARD_BG);
        _gfx->setTextSize(2);
        _gfx->setTextColor(COLOR_TEXT_MAIN);
        _gfx->setCursor(88, 85);
        _gfx->printf("%.2f", phVoltage);
        _gfx->setTextSize(1);
        _gfx->print("V");
    }

    // 6. Bottom Footer Status Bar
    if (phValue != _lastPH || uptimeSeconds != _lastUptime) {
        _lastUptime = uptimeSeconds;

        _gfx->fillRect(0, 113, w, 15, COLOR_HEADER_BG);
        _gfx->setTextSize(1);

        // Evaluate pH status text
        if (phValue < 5.5f) {
            _gfx->setTextColor(COLOR_ALERT);
            _gfx->setCursor(4, 117);
            _gfx->print("[PH: ACIDIC]");
        } else if (phValue > 6.8f) {
            _gfx->setTextColor(COLOR_VOLTS);
            _gfx->setCursor(4, 117);
            _gfx->print("[PH: ALKALINE]");
        } else {
            _gfx->setTextColor(COLOR_OPTIMAL);
            _gfx->setCursor(4, 117);
            _gfx->print("[PH: OPTIMAL]");
        }

        // Uptime
        _gfx->setCursor(110, 117);
        _gfx->setTextColor(COLOR_TEXT_MUTED);
        _gfx->printf("Up:%lus", (unsigned long)uptimeSeconds);
    }
}

void TFTDisplayManager::showStatusMessage(const char* message) {
    if (!_gfx) return;
    int16_t w = _gfx->width();
    _gfx->fillRect(0, 113, w, 15, COLOR_HEADER_BG);
    _gfx->setTextSize(1);
    _gfx->setTextColor(COLOR_PH);
    _gfx->setCursor(4, 117);
    _gfx->print(message);
}
