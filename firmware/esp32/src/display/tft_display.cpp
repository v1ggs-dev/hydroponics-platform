#include "tft_display.h"

// High-contrast 16-bit RGB565 Color Palette
#define COLOR_BG        0x0841  // Deep slate background
#define COLOR_CARD_BG   0x18E3  // Dark surface container
#define COLOR_HEADER_BG 0x0287  // Header band
#define COLOR_TEXT_MAIN 0xFFFF  // Crisp white
#define COLOR_TEXT_MUTED 0xAD55 // Subtle grey
#define COLOR_TEMP      0xFA08  // Coral Orange (Temperature)
#define COLOR_HUMIDITY  0x07FF  // Sky Blue (Humidity)
#define COLOR_TDS       0x37E6  // Emerald Green (TDS)
#define COLOR_MOISTURE  0xFDC0  // Bright Amber / Gold (Moisture)
#define COLOR_BORDER    0x39E7  // Card border

TFTDisplayManager::TFTDisplayManager(int8_t csPin, int8_t dcPin, int8_t rstPin, int8_t blPin)
    : _csPin(csPin),
      _dcPin(dcPin),
      _rstPin(rstPin),
      _blPin(blPin),
      _tft89(nullptr),
      _tft35(nullptr),
      _gfx(nullptr),
      _driverType(TFTDriverType::ST7735_128x160),
      _lastTemp(-999.0f),
      _lastHum(-999.0f),
      _lastTds(-999.0f),
      _lastMoist(-999.0f),
      _lastUptime(0) {}

bool TFTDisplayManager::begin(TFTDriverType driver) {
    _driverType = driver;

    // Enable backlight if configured
    if (_blPin >= 0) {
        pinMode(_blPin, OUTPUT);
        digitalWrite(_blPin, HIGH);
    }

    switch (_driverType) {
        case TFTDriverType::ST7735_128x160:
            _tft35 = new Adafruit_ST7735(_csPin, _dcPin, _rstPin);
            _tft35->initR(INITR_BLACKTAB); // Standard 1.8" 128x160 TFT SPI V1.1
            _tft35->setRotation(3);        // Inverted Landscape 160x128 (pins on left side)
            _gfx = _tft35;
            break;

        case TFTDriverType::ST7735_128x128:
            _tft35 = new Adafruit_ST7735(_csPin, _dcPin, _rstPin);
            _tft35->initR(INITR_144GREENTAB);
            _tft35->setRotation(1);
            _gfx = _tft35;
            break;

        case TFTDriverType::ST7789_240x240:
            _tft89 = new Adafruit_ST7789(_csPin, _dcPin, _rstPin);
            _tft89->init(240, 240);
            _tft89->setRotation(2);
            _gfx = _tft89;
            break;

        case TFTDriverType::ST7789_135x240:
            _tft89 = new Adafruit_ST7789(_csPin, _dcPin, _rstPin);
            _tft89->init(135, 240);
            _tft89->setRotation(3);
            _gfx = _tft89;
            break;
    }

    if (!_gfx) return false;

    return true;
}

void TFTDisplayManager::showWelcomeScreen(const char* deviceId, const char* version, uint8_t ledPin, int8_t buzzerPin, uint16_t durationMs) {
    if (!_gfx) return;

    int16_t w = _gfx->width();
    int16_t h = _gfx->height();

    // 1. Splash Screen Background
    _gfx->fillScreen(COLOR_BG);

    // 2. Decorative System Badge
    _gfx->fillRoundRect(10, 8, w - 20, 44, 5, COLOR_CARD_BG);
    _gfx->drawRoundRect(10, 8, w - 20, 44, 5, COLOR_TDS);

    _gfx->setTextSize(1);
    _gfx->setTextColor(COLOR_TEXT_MAIN);
    _gfx->setCursor(20, 15);
    _gfx->print("HYDROPONICS PLATFORM");

    _gfx->setTextColor(COLOR_HUMIDITY);
    _gfx->setCursor(26, 28);
    _gfx->print("IoT Station Controller");

    _gfx->setTextColor(COLOR_MOISTURE);
    _gfx->setCursor(26, 40);
    _gfx->printf("Node: %s | %s", deviceId, version);

    // 3. Progress Bar Frame
    int16_t barX = 14;
    int16_t barY = 64;
    int16_t barW = w - 28;
    int16_t barH = 12;
    _gfx->fillRoundRect(barX, barY, barW, barH, 3, COLOR_CARD_BG);
    _gfx->drawRoundRect(barX, barY, barW, barH, 3, COLOR_BORDER);

    // 4. Animated Loading Loop with Musical Fanfare & Rapid LED Blinking
    pinMode(ledPin, OUTPUT);
    if (buzzerPin >= 0) {
        pinMode(buzzerPin, OUTPUT);
        digitalWrite(buzzerPin, LOW);
    }

    uint16_t stepCount = 60; // 60 steps * 100ms = 6000ms
    uint16_t stepDelay = durationMs / stepCount;
    bool ledState = false;

    for (uint16_t i = 0; i <= stepCount; ++i) {
        // Toggle LED rapidly (every 100ms)
        ledState = !ledState;
        digitalWrite(ledPin, ledState ? HIGH : LOW);

        // Musical Jingle at progress milestones
        if (buzzerPin >= 0) {
            if (i == 10) {
                // Note 1: C5 (523 Hz)
                tone(buzzerPin, 523, 100);
            } else if (i == 22) {
                // Note 2: E5 (659 Hz)
                tone(buzzerPin, 659, 100);
            } else if (i == 34) {
                // Note 3: G5 (784 Hz)
                tone(buzzerPin, 784, 100);
            } else if (i == 46) {
                // Note 4: A5 (880 Hz)
                tone(buzzerPin, 880, 120);
            } else if (i == 58) {
                // Note 5: C6 (1047 Hz) - Finale
                tone(buzzerPin, 1047, 250);
            }
        }

        // Update progress bar
        int16_t progressFill = (int32_t)(barW - 4) * i / stepCount;
        if (progressFill > 0) {
            _gfx->fillRect(barX + 2, barY + 2, progressFill, barH - 4, COLOR_TDS);
        }

        // Sub-text status
        _gfx->fillRect(barX, 84, barW, 14, COLOR_BG);
        _gfx->setTextColor(COLOR_TEXT_MUTED);
        _gfx->setCursor(barX + 10, 86);
        if (i < 18) {
            _gfx->print("Booting HAL...");
        } else if (i < 34) {
            _gfx->print("Calibrating ADC...");
        } else if (i < 48) {
            _gfx->print("Initializing VSPI");
        } else {
            _gfx->setTextColor(COLOR_TDS);
            _gfx->print("System Ready!");
        }

        delay(stepDelay);
    }

    // Turn LED & Buzzer OFF after splash
    digitalWrite(ledPin, LOW);
    if (buzzerPin >= 0) {
        noTone(buzzerPin);
        digitalWrite(buzzerPin, LOW);
    }

    // Transition to standard Dashboard
    _gfx->fillScreen(COLOR_BG);
    drawHeader(deviceId, version);
}

void TFTDisplayManager::drawHeader(const char* deviceId, const char* version, bool wifiOk, bool mqttOk) {
    if (!_gfx) return;

    int16_t w = _gfx->width();

    // Top Header Banner
    _gfx->fillRect(0, 0, w, 16, COLOR_HEADER_BG);
    _gfx->drawLine(0, 16, w, 16, COLOR_BORDER);

    _gfx->setTextSize(1);
    _gfx->setTextColor(COLOR_TEXT_MAIN);
    _gfx->setCursor(4, 4);
    _gfx->print("HYDRO: ");
    _gfx->setTextColor(COLOR_TDS);
    _gfx->print(deviceId);

    // Wireless Indicators: [W] = Wi-Fi, [M] = MQTT
    _gfx->setCursor(w - 60, 4);
    _gfx->setTextColor(wifiOk ? COLOR_TDS : COLOR_BORDER);
    _gfx->print("W");

    _gfx->setCursor(w - 48, 4);
    _gfx->setTextColor(mqttOk ? COLOR_HUMIDITY : COLOR_BORDER);
    _gfx->print("M");

    _gfx->setTextColor(COLOR_TEXT_MUTED);
    _gfx->setCursor(w - 34, 4);
    _gfx->print(version);
}

void TFTDisplayManager::updateDashboard(float tempC, float humPercent, float tdsPpm, float moistPercent, bool pumpOn, float flowRateLpm, bool wifiOk, bool mqttOk, uint32_t uptimeSeconds) {
    if (!_gfx) return;

    // Refresh header indicators if connection state changes
    drawHeader("esp32-01", "v0.1", wifiOk, mqttOk);

    int16_t w = _gfx->width();
    int16_t cardWidth = (w - 9) / 2; // 75px each
    int16_t cardHeight = 44;

    int16_t x1 = 3;
    int16_t x2 = x1 + cardWidth + 3; // 81px
    int16_t y1 = 19;
    int16_t y2 = y1 + cardHeight + 3; // 66px

    // -------------------------------------------------------------------------
    // Card 1: Air Temp (Top-Left)
    // -------------------------------------------------------------------------
    if (abs(tempC - _lastTemp) >= 0.1f) {
        _lastTemp = tempC;
        _gfx->fillRoundRect(x1, y1, cardWidth, cardHeight, 3, COLOR_CARD_BG);
        _gfx->drawRoundRect(x1, y1, cardWidth, cardHeight, 3, COLOR_BORDER);

        _gfx->setTextSize(1);
        _gfx->setTextColor(COLOR_TEXT_MUTED);
        _gfx->setCursor(x1 + 4, y1 + 4);
        _gfx->print("AIR TEMP");

        _gfx->setTextSize(2);
        _gfx->setTextColor(COLOR_TEMP);
        _gfx->setCursor(x1 + 4, y1 + 18);
        if (!isnan(tempC)) {
            _gfx->printf("%.1fC", tempC);
        } else {
            _gfx->print("--.-C");
        }
    }

    // -------------------------------------------------------------------------
    // Card 2: Humidity (Top-Right)
    // -------------------------------------------------------------------------
    if (abs(humPercent - _lastHum) >= 0.5f) {
        _lastHum = humPercent;
        _gfx->fillRoundRect(x2, y1, cardWidth, cardHeight, 3, COLOR_CARD_BG);
        _gfx->drawRoundRect(x2, y1, cardWidth, cardHeight, 3, COLOR_BORDER);

        _gfx->setTextSize(1);
        _gfx->setTextColor(COLOR_TEXT_MUTED);
        _gfx->setCursor(x2 + 4, y1 + 4);
        _gfx->print("HUMIDITY");

        _gfx->setTextSize(2);
        _gfx->setTextColor(COLOR_HUMIDITY);
        _gfx->setCursor(x2 + 4, y1 + 18);
        if (!isnan(humPercent)) {
            _gfx->printf("%.1f%%", humPercent);
        } else {
            _gfx->print("--.-%");
        }
    }

    // -------------------------------------------------------------------------
    // Card 3: Water TDS (Bottom-Left)
    // -------------------------------------------------------------------------
    if (abs(tdsPpm - _lastTds) >= 1.0f) {
        _lastTds = tdsPpm;
        _gfx->fillRoundRect(x1, y2, cardWidth, cardHeight, 3, COLOR_CARD_BG);
        _gfx->drawRoundRect(x1, y2, cardWidth, cardHeight, 3, COLOR_BORDER);

        _gfx->setTextSize(1);
        _gfx->setTextColor(COLOR_TEXT_MUTED);
        _gfx->setCursor(x1 + 4, y2 + 4);
        _gfx->print("WATER TDS");

        _gfx->setTextSize(2);
        _gfx->setTextColor(COLOR_TDS);
        _gfx->setCursor(x1 + 4, y2 + 18);
        if (!isnan(tdsPpm)) {
            _gfx->printf("%.0f", tdsPpm);
            _gfx->setTextSize(1);
            _gfx->print("ppm");
        } else {
            _gfx->print("---");
        }
    }

    // -------------------------------------------------------------------------
    // Card 4: Moisture (Bottom-Right)
    // -------------------------------------------------------------------------
    if (abs(moistPercent - _lastMoist) >= 0.5f) {
        _lastMoist = moistPercent;
        _gfx->fillRoundRect(x2, y2, cardWidth, cardHeight, 3, COLOR_CARD_BG);
        _gfx->drawRoundRect(x2, y2, cardWidth, cardHeight, 3, COLOR_BORDER);

        _gfx->setTextSize(1);
        _gfx->setTextColor(COLOR_TEXT_MUTED);
        _gfx->setCursor(x2 + 4, y2 + 4);
        _gfx->print("MOISTURE");

        _gfx->setTextSize(2);
        _gfx->setTextColor(COLOR_MOISTURE);
        _gfx->setCursor(x2 + 4, y2 + 18);
        if (!isnan(moistPercent)) {
            _gfx->printf("%.1f%%", moistPercent);
        } else {
            _gfx->print("--.-%");
        }
    }

    // -------------------------------------------------------------------------
    // Bottom Status Footer (y = 114) with Pump & Flow Indicators
    // -------------------------------------------------------------------------
    int16_t footerY = _gfx->height() - 14;
    _gfx->fillRect(0, footerY, w, 14, pumpOn ? COLOR_CARD_BG : COLOR_BG);
    
    _gfx->setTextSize(1);
    _gfx->setCursor(4, footerY + 3);

    if (pumpOn) {
        _gfx->setTextColor(COLOR_TDS);
        _gfx->print("PUMP:ON ");
        _gfx->setTextColor(COLOR_HUMIDITY);
        _gfx->printf("%.1fL/m ", flowRateLpm);
        _gfx->setTextColor(COLOR_TEXT_MUTED);
        _gfx->printf("| %lus", (unsigned long)uptimeSeconds);
    } else {
        _gfx->setTextColor(COLOR_TEXT_MUTED);
        if (flowRateLpm > 0.1f) {
            _gfx->setTextColor(COLOR_HUMIDITY);
            _gfx->printf("FLOW: %.1fL/m ", flowRateLpm);
            _gfx->setTextColor(COLOR_TEXT_MUTED);
            _gfx->printf("| %lus", (unsigned long)uptimeSeconds);
        } else {
            _gfx->printf("OK | PUMP:OFF | %lus", (unsigned long)uptimeSeconds);
        }
    }
}

void TFTDisplayManager::showStatusMessage(const char* message) {
    if (!_gfx) return;
    int16_t footerY = _gfx->height() - 14;
    _gfx->fillRect(0, footerY, _gfx->width(), 14, COLOR_HEADER_BG);
    _gfx->setTextSize(1);
    _gfx->setTextColor(COLOR_TEXT_MAIN);
    _gfx->setCursor(4, footerY + 3);
    _gfx->print(message);
}
