#pragma once

// =============================================================================
// Hydroponics Platform — ESP32 Node 1 (Environment & Actuation) Pinout
// =============================================================================

// -----------------------------------------------------------------------------
// Digital Environmental Sensors
// -----------------------------------------------------------------------------
#define PIN_DHT11_DATA      4       // DHT11 Air Temperature & Humidity data line

// -----------------------------------------------------------------------------
// Flow Sensors (Digital Pulse Interrupt)
// -----------------------------------------------------------------------------
#define PIN_FLOW_SENSOR     13      // YF-S201 Hall-effect Pulse Input (Interrupt)

// -----------------------------------------------------------------------------
// Actuators & Audio Alarms
// -----------------------------------------------------------------------------
#define PIN_BUZZER          25      // Buzzer Driver Output (NPN BC547 Base trigger)
#define PIN_PUMP_RELAY      26      // Water Pump Relay Driver Output (Active LOW)

// -----------------------------------------------------------------------------
// TFT SPI Color Display #1 (Hardware VSPI)
// -----------------------------------------------------------------------------
#define PIN_TFT_SCLK        18      // SPI Clock (SCL / SCK)
#define PIN_TFT_MOSI        23      // SPI Data / MOSI (SDA / MOSI)
#define PIN_TFT_CS           5      // Chip Select (CS)
#define PIN_TFT_DC          16      // Data / Command (DC / RS / A0)
#define PIN_TFT_RST         17      // Hardware Reset (RES / RST)
#define PIN_TFT_BL          -1      // Backlight (Tied to 3.3V)
