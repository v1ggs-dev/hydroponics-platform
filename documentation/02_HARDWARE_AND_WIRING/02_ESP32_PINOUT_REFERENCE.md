# Hydroponics Platform — Master Dual-ESP32 Pinout Reference

## 1. Purpose & Architecture

This document is the authoritative hardware reference for the Dual-ESP32, Dual-ST7735 Display, and Analog pH sensor architecture.

To eliminate motor switching noise on sensitive analog readings, hardware is partitioned across two specialized, autonomous microcontrollers:
1. **ESP32 Node 1 (`esp32-env`)**: Environment, Fluid Circulation, Audio Alarms, Local Display #1, and Hardware Safety Interlocks.
2. **ESP32 Node 2 (`esp32-chem`)**: High-Impedance Water Chemistry (pH, TDS, Moisture) and Local Display #2.
3. **Dedicated Camera Node (`esp32-cam`)**: 2MP Optical Canopy Image Capture.

---

## 2. ESP32 Node 1 (`esp32-env`) — Pinout Reference

**Role**: Climate acquisition, fluid circulation, buzzer alarm, Display #1, local safety interlocks.  
**Firmware Location**: `firmware/esp32_env/`  
**Default Serial Port**: `COM6` (or auto-detected via `manager.py`)

| ESP32 Pin | Function | Direction | Electrical Specs | Connected Subsystem | Firmware Definition |
|---|---|---|---|---|---|
| `GPIO 4` | Digital I/O | Bidirectional | 3.3V Logic, 10kΩ Pull-up | DHT11 Air Temp & Humidity | `PIN_DHT11_DATA` |
| `GPIO 13` | Digital Input | Input (ISR) | 3.3V Logic (`FALLING` Edge) | YF-S201 Flow Sensor Pulse | `PIN_FLOW_SENSOR` |
| `GPIO 26` | Digital Output | Output | 3.3V Logic (Active LOW) | 5V Relay (Submersible Pump) | `PIN_PUMP_RELAY` |
| `GPIO 25` | Digital Output | Output | 3.3V Logic to BC547 Base (1kΩ)| 5V Piezo Buzzer Alarm | `PIN_BUZZER` |
| `GPIO 18` | VSPI SCK | Output | 3.3V SPI Serial Clock | ST7735 Display #1 SCL/SCK | `PIN_TFT_SCLK` |
| `GPIO 23` | VSPI MOSI | Output | 3.3V SPI Master Out | ST7735 Display #1 SDA/MOSI | `PIN_TFT_MOSI` |
| `GPIO 16` | Digital Output | Output | 3.3V Logic Data/Command | ST7735 Display #1 DC/A0 | `PIN_TFT_DC` |
| `GPIO 17` | Digital Output | Output | 3.3V Logic Active LOW Reset | ST7735 Display #1 RES/RST | `PIN_TFT_RST` |
| `GPIO 5` | VSPI CS | Output | 3.3V Logic Active LOW CS | ST7735 Display #1 CS | `PIN_TFT_CS` |
| `VIN / 5V`| Power Input | Power | 5.0V DC Input from USB/Rail| 5V Bus (Relay, Flow, Buzzer, TFT) | `VCC_5V` |
| `3V3` | Power Output | Power | 3.3V DC Regulated (max ~500mA)| DHT11, TFT Backlight | `VCC_3V3` |
| `GND` | System Ground | Power | 0.0V Common Ground | Ground Bus | `GND` |

*Note: Status LED on GPIO 2 is completely removed to free pin overhead and prevent blinking distraction.*

---

## 3. ESP32 Node 2 (`esp32-chem`) — Pinout Reference

**Role**: High-impedance analog sensor acquisition (pH, TDS, Moisture) and Display #2.  
**Firmware Location**: `firmware/esp32_chem/`  
**Default Serial Port**: `COM8` (or auto-detected via `manager.py`)

| ESP32 Pin | Function | Direction | Electrical Specs | Connected Subsystem | Firmware Definition |
|---|---|---|---|---|---|
| `GPIO 34` | ADC1_CH6 | Input Only | 0.0V–3.3V Analog Input | Analog pH Probe Signal Board | `PIN_PH_ADC` |
| `GPIO 35` | ADC1_CH7 | Input Only | 0.0V–3.3V Analog Input | Analog TDS Probe Signal Board | `PIN_TDS_ADC` |
| `GPIO 32` | ADC1_CH4 | Input Only | 0.0V–3.3V Analog Input | Analog Moisture Probe | `PIN_SOIL_MOISTURE_ADC` |
| `GPIO 18` | VSPI SCK | Output | 3.3V SPI Serial Clock | ST7735 Display #2 SCL/SCK | `PIN_TFT_SCLK` |
| `GPIO 23` | VSPI MOSI | Output | 3.3V SPI Master Out | ST7735 Display #2 SDA/MOSI | `PIN_TFT_MOSI` |
| `GPIO 16` | Digital Output | Output | 3.3V Logic Data/Command | ST7735 Display #2 DC/A0 | `PIN_TFT_DC` |
| `GPIO 17` | Digital Output | Output | 3.3V Logic Active LOW Reset | ST7735 Display #2 RES/RST | `PIN_TFT_RST` |
| `GPIO 5` | VSPI CS | Output | 3.3V Logic Active LOW CS | ST7735 Display #2 CS | `PIN_TFT_CS` |
| `VIN / 5V`| Power Input | Power | 5.0V DC Input from USB/Rail| 5V Bus (TFT VCC, pH Board VCC) | `VCC_5V` |
| `3V3` | Power Output | Power | 3.3V DC Clean ADC Rail | TDS VCC, Moisture VCC, TFT BL | `VCC_3V3` |
| `GND` | System Ground | Power | 0.0V Common Ground | Ground Bus | `GND` |

---

## 4. Vision Node (`esp32-cam`) — Pinout Reference

**Role**: Optical plant canopy imaging and HTTP/MJPEG streaming.  
**Firmware Location**: `firmware/esp32_cam/`  
**Camera Sensor**: Omnivision OV2640 2MP

| Camera Pin | Connected GPIO | Function |
|---|---|---|
| `Y2 - Y9` | `GPIO 5, 18, 19, 21, 36, 39, 34, 35` | 8-Bit Parallel DVP Video Bus |
| `XCLK` | `GPIO 0` | Master Sensor Clock |
| `PCLK` | `GPIO 22` | Pixel Clock |
| `VSYNC` | `GPIO 25` | Vertical Sync |
| `HREF` | `GPIO 23` | Horizontal Reference |
| `SIOD (SDA)`| `GPIO 26` | I2C SCCB Data |
| `SIOC (SCL)`| `GPIO 27` | I2C SCCB Clock |
| `PWDN` | `GPIO 32` | Power Down (Active HIGH) |
| `RESET` | `-1` (Software Reset) | Hardware Reset |