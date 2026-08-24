#pragma once

// =============================================================================
// Hydroponics Platform — ESP32 Node 2 (Water Chemistry & Root Zone) Pinout
// =============================================================================

// -----------------------------------------------------------------------------
// Analog Chemistry & Root Zone Sensors (ADC1)
// -----------------------------------------------------------------------------
#define PIN_PH_ADC              34      // Analog pH Sensor Signal (ADC1 Channel 6)
#define PIN_TDS_ADC             35      // Analog TDS Sensor Signal (ADC1 Channel 7)
#define PIN_SOIL_MOISTURE_ADC   32      // Analog Moisture Sensor Signal (ADC1 Channel 4)

// -----------------------------------------------------------------------------
// TFT SPI Color Display #2 (Hardware VSPI)
// -----------------------------------------------------------------------------
#define PIN_TFT_SCLK        18      // SPI Clock (SCL / SCK)
#define PIN_TFT_MOSI        23      // SPI Data / MOSI (SDA / MOSI)
#define PIN_TFT_CS           5      // Chip Select (CS)
#define PIN_TFT_DC          16      // Data / Command (DC / RS / A0)
#define PIN_TFT_RST         17      // Hardware Reset (RES / RST)
#define PIN_TFT_BL          -1      // Backlight (Tied to 3.3V)
