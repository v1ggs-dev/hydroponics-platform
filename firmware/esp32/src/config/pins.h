#pragma once

// =============================================================================
// Hydroponics Platform — Authoritative ESP32 Pinout Configuration
// Reference: docs/hardware/PINOUT.md
// =============================================================================

// -----------------------------------------------------------------------------
// Digital & Environmental Sensors
// -----------------------------------------------------------------------------
#define PIN_DHT11_DATA      4       // DHT11 Air Temperature & Humidity data line

// -----------------------------------------------------------------------------
// Status & Diagnostics
// -----------------------------------------------------------------------------
#define PIN_STATUS_LED      2       // Onboard blue LED (GPIO 2 on most ESP32 DevKit boards)

// -----------------------------------------------------------------------------
// Analog Sensors (ADC1: GPIOs 32-39 - Safe to use with Wi-Fi)
// -----------------------------------------------------------------------------
#define PIN_TDS_ADC             34  // Analog TDS Sensor Signal (ADC1 Channel 6)
#define PIN_SOIL_MOISTURE_ADC   35  // Analog Moisture Sensor Signal (ADC1 Channel 7)

// -----------------------------------------------------------------------------
// TFT SPI Color Display (Hardware VSPI)
// Reference: docs/hardware/PINOUT.md
// -----------------------------------------------------------------------------
#define PIN_TFT_SCLK        18      // SPI Clock (SCL / SCK / CLK)
#define PIN_TFT_MOSI        23      // SPI Data / MOSI (SDA / MOSI / DIN)
#define PIN_TFT_CS           5      // Chip Select (CS) - Set -1 if no CS pin on display
#define PIN_TFT_DC          16      // Data / Command (DC / RS / A0)
#define PIN_TFT_RST         17      // Hardware Reset (RES / RST) - Set -1 if connected to ESP32 EN
#define PIN_TFT_BL          22      // Backlight (BLK / BL / LED) - Connect to 3.3V or GPIO 22

// -----------------------------------------------------------------------------
// Flow Sensors (Digital Pulse Interrupt)
// -----------------------------------------------------------------------------
#define PIN_FLOW_SENSOR     13      // YF-S201 Hall-effect Pulse Input (Interrupt)

// -----------------------------------------------------------------------------
// Actuators & Relays
// -----------------------------------------------------------------------------
#define PIN_BUZZER          25      // Buzzer Driver Output (NPN BC547 Base trigger)
#define PIN_PUMP_RELAY      26      // Water Pump Relay Driver Output (Active LOW/HIGH)

// -----------------------------------------------------------------------------
// Future Reservations (from PINOUT.md)
// -----------------------------------------------------------------------------
// #define PIN_VALVE_RELAY  27      // Future Solenoid Valve Relay Driver
// #define PIN_WATER_LEVEL  14      // Future Water Level Sensor Input
