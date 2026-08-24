# Hydroponics Platform — Complete Master Wiring & Pinout Guide

**Document Version:** 2.0.0 (Dual-ESP32, Dual-Display & pH Architecture)  
**Target Hardware:** 2x ESP32 DevKit V1 (30-Pin / 38-Pin WROOM-32) + 1x ESP32-CAM  
**Displays:** 2x 1.8" ST7735 SPI TFT Color Displays (160x128)  
**Status:** Validated on Hardware & Codebase

---

## 1. System Hardware Partitioning Overview

To completely isolate sensitive, high-impedance analog probes from electrical motor switching noise and relay inductive spikes, the system is split across two dedicated microcontrollers:

```mermaid
graph TD
    subgraph NODE1 [ESP32 Node 1: Environment & Actuation Master (esp32-env)]
        E1[ESP32 DevKit V1 - COM6]
        E1 --> DHT11[DHT11: Air Temp & Humidity - GPIO 4]
        E1 --> FLOW[YF-S201: Flow Sensor - GPIO 13 ISR]
        E1 --> RELAY[5V Relay: Submersible Pump - GPIO 26]
        E1 --> BUZZER[Piezo Buzzer + BC547 - GPIO 25]
        E1 --> DISP1[Display #1: ST7735 1.8 TFT - VSPI]
    end

    subgraph NODE2 [ESP32 Node 2: Water Chemistry & Root Specialist (esp32-chem)]
        E2[ESP32 DevKit V1 - COM8]
        E2 --> PH_SENS[Analog pH Probe Module - GPIO 34 ADC1_6]
        E2 --> TDS_SENS[Analog TDS Probe Module - GPIO 35 ADC1_7]
        E2 --> MOIST_SENS[Substrate Moisture Probe - GPIO 32 ADC1_4]
        E2 --> DISP2[Display #2: ST7735 1.8 TFT - VSPI]
    end

    subgraph CAM_NODE [Vision Node: Optical Canopy Node]
        CAM[ESP32-CAM AI-Thinker + OV2640 2MP]
    end
```

---

## 2. ESP32 Node 1 (`esp32-env` — Climate, Flow, Relay & Display #1)

### 2.1 Master Pin Mapping Table

| ESP32 Pin | Signal / Interface | Connected Hardware Component | Module Pin | Voltage Level | Purpose / Function |
|---|---|---|---|---|---|
| **VIN (5V)**| 5.0V Power Input | Breadboard `+` (Red) 5V Power Rail | `VCC` | 5.0V DC | Main 5V rail for Relay, Flow meter, Buzzer, Display 1 |
| **3V3** | 3.3V Power Out | Clean 3.3V Logic Rail | `VCC` / `+` | 3.3V DC | Regulated 3.3V for DHT11 & TFT Backlight |
| **GND** | System Ground | Common Ground Bus Rail | `GND` / `-` | 0.0V | **Common System Ground Reference** |
| **GPIO 4** | Digital I/O | **DHT11 Air Temp & Humidity** | `DATA` / `OUT` | 3.3V Logic | Ambient microclimate reading (10kΩ pullup) |
| **GPIO 13**| Digital Pulse ISR | **YF-S201 Flow Sensor** | `Signal` (Yellow) | 3.3V / 5V Logic| Real-time flow rate (L/min) & cumulative liters |
| **GPIO 26**| Digital Output | **5V 1-Channel Relay Module** | `IN` Signal | 3.3V / 5V Logic| Submersible pump switching (Active LOW) |
| **GPIO 25**| Digital Output | **BC547 NPN Buzzer Driver** | Base via 1kΩ | 3.3V Logic | Boot fanfare & audible safety alarms |
| **GPIO 18**| Hardware VSPI SCK | **ST7735 Display #1 (1.8" TFT)** | `SCL` / `SCK` | 3.3V Logic | SPI Clock |
| **GPIO 23**| Hardware VSPI MOSI| **ST7735 Display #1 (1.8" TFT)** | `SDA` / `MOSI` | 3.3V Logic | SPI Master-Out Slave-In |
| **GPIO 16**| Digital Output | **ST7735 Display #1 (1.8" TFT)** | `DC` / `RS` / `A0` | 3.3V Logic | Data / Command Select |
| **GPIO 17**| Digital Output | **ST7735 Display #1 (1.8" TFT)** | `RES` / `RST` | 3.3V Logic | Hardware Display Reset |
| **GPIO 5** | Hardware VSPI CS | **ST7735 Display #1 (1.8" TFT)** | `CS` | 3.3V Logic | Chip Select |

*(Note: Status LED is completely removed from Node 1 to eliminate visual blinking and free GPIO 2).*

---

### 2.2 Detailed Node 1 Wiring Schematics

#### 🌡️ A. DHT11 Temperature & Humidity Sensor
```text
ESP32 3.3V   ──────────────────────────> DHT11 Pin 1 (VCC / +)
ESP32 GPIO 4 ────────┬─────────────────> DHT11 Pin 2 (DATA / OUT)
                     └──[ 10kΩ Pullup ]──> (tied to 3.3V)
ESP32 GND    ──────────────────────────> DHT11 Pin 4 (GND / -)
```

#### 🌊 B. YF-S201 Hall-Effect Flow Sensor
```text
ESP32 VIN (5V) ────────────────────────> Flow Sensor RED Wire (VCC 5V)
ESP32 GND      ────────────────────────> Flow Sensor BLACK Wire (GND)
ESP32 GPIO 13  ────────────────────────> Flow Sensor YELLOW Wire (Pulse Signal)
```

#### 🔌 C. 5V Relay Actuator (Submersible Pump)
```text
ESP32 VIN (5V) ────────────────────────> Relay VCC
ESP32 GND      ────────────────────────> Relay GND
ESP32 GPIO 26  ────────────────────────> Relay IN (Active LOW Trigger)

[ ISOLATED HIGH CURRENT PUMP CIRCUIT ]
12V DC Adapter (+) ───> Relay COM Terminal
Relay NO Terminal  ───> Submersible Pump (+) Red Wire
Submersible Pump (-) ──> 12V DC Adapter (-) Ground
```

#### 🔊 D. BC547 NPN Buzzer Driver Circuit
```text
                  +5V DC Rail (VIN)
                         │
                         ▼
                 [ + Piezo Buzzer - ]
                         │
                         ▼ Collector (Pin 1)
   ESP32 GPIO 25 ──[ 1kΩ ]──► Base (Pin 2) [ BC547 NPN ]
                         │
                         ▼ Emitter (Pin 3)
                    Common GND
```

#### 🖥️ E. ST7735 1.8" SPI TFT Color Display #1 (Climate & Hydraulics Cockpit)
```text
Display #1 Pin Label     ESP32 Node 1 Pin     Wire / Signal Function
────────────────────────────────────────────────────────────────────
GND                      GND                  Common Ground
VCC                      VIN (5V)             Display Power Supply
SCL / SCK                GPIO 18              VSPI Serial Clock
SDA / MOSI               GPIO 23              VSPI Master Out Data
RES / RST                GPIO 17              Hardware Reset
DC / RS / A0             GPIO 16              Data / Command Mode
CS                       GPIO 5               Chip Select
BLK / LED                3.3V                 Backlight Power (Always ON)
```

---

## 3. ESP32 Node 2 (`esp32-chem` — Water Chemistry & Root Zone)

### 3.1 Master Pin Mapping Table

| ESP32 Pin | Signal / Interface | Connected Hardware Component | Module Pin | Voltage Level | Purpose / Function |
|---|---|---|---|---|---|
| **VIN (5V)**| 5.0V Power Input | Breadboard `+` (Red) 5V Power Rail | `VCC` | 5.0V DC | Main 5V rail for pH board & Display 2 |
| **3V3** | 3.3V Clean Out | Clean ADC Reference Rail | `VCC` / `+` | 3.3V DC | Ultra-clean power for TDS & Moisture probes |
| **GND** | System Ground | Common Ground Bus Rail | `GND` / `-` | 0.0V | **Common System Ground Reference** |
| **GPIO 34**| Analog Input (ADC1_CH6) | **Analog pH Sensor Board** | `Po` / `OUT` | 0.0V–3.3V ADC | Solution Acidity / Alkalinity ($0.00–14.00\text{ pH}$) |
| **GPIO 35**| Analog Input (ADC1_CH7) | **Analog TDS Sensor Board**| `A` / `SIG` | 0.0V–2.3V ADC | Nutrient Concentration ($0–2000\text{ ppm}$) |
| **GPIO 32**| Analog Input (ADC1_CH4) | **Substrate Moisture Probe**| `AO` (Analog Out) | 0.0V–3.3V ADC | Root Zone Hydration ($0.0–100.0\%$) |
| **GPIO 18**| Hardware VSPI SCK | **ST7735 Display #2 (1.8" TFT)** | `SCL` / `SCK` | 3.3V Logic | SPI Clock |
| **GPIO 23**| Hardware VSPI MOSI| **ST7735 Display #2 (1.8" TFT)** | `SDA` / `MOSI` | 3.3V Logic | SPI Master-Out Slave-In |
| **GPIO 16**| Digital Output | **ST7735 Display #2 (1.8" TFT)** | `DC` / `RS` / `A0` | 3.3V Logic | Data / Command Select |
| **GPIO 17**| Digital Output | **ST7735 Display #2 (1.8" TFT)** | `RES` / `RST` | 3.3V Logic | Hardware Display Reset |
| **GPIO 5** | Hardware VSPI CS | **ST7735 Display #2 (1.8" TFT)** | `CS` | 3.3V Logic | Chip Select |

---

### 3.2 Detailed Node 2 Wiring Schematics

#### 🧪 A. Analog pH Sensor Probe & Signal Board
- **Module**: Glass electrode BNC probe + LM358 / Op-Amp Signal Board
- **Measurement Range**: $0.00–14.00\text{ pH}$
- **Neutral Voltage**: $1.65\text{V}$ (Midpoint on 3.3V scale)

```text
ESP32 VIN (5V)  ───────────────────────> pH Board VCC
ESP32 GND       ───────────────────────> pH Board GND
ESP32 GPIO 34   ───────────────────────> pH Board Po (Analog pH Output)
BNC Connector   ───────────────────────> Glass Bulb pH Electrode
Do Pin          ───────────────────────> (LEAVE UNCONNECTED)
```

#### ⚡ B. Analog TDS Nutrient Probe
```text
ESP32 3.3V      ───────────────────────> TDS Board VCC (+)
ESP32 GND       ───────────────────────> TDS Board GND (-)
ESP32 GPIO 35   ───────────────────────> TDS Board Analog Output (A / SIG)
2-Pin Terminal  ───────────────────────> Submerged TDS Titanium Probe
```

#### 🌱 C. Analog Substrate Moisture Sensor (4-Pin Board)
```text
ESP32 3.3V      ───────────────────────> Moisture Board VCC (+)
ESP32 GND       ───────────────────────> Moisture Board GND (-)
ESP32 GPIO 32   ───────────────────────> Moisture Board AO (Analog Out)
DO Pin          ───────────────────────> (LEAVE UNCONNECTED)
2-Pin Header    ───────────────────────> Moisture Fork Prongs
```

#### 🖥️ D. ST7735 1.8" SPI TFT Color Display #2 (Water Chemistry & Roots Cockpit)
```text
Display #2 Pin Label     ESP32 Node 2 Pin     Wire / Signal Function
────────────────────────────────────────────────────────────────────
GND                      GND                  Common Ground
VCC                      VIN (5V)             Display Power Supply
SCL / SCK                GPIO 18              VSPI Serial Clock
SDA / MOSI               GPIO 23              VSPI Master Out Data
RES / RST                GPIO 17              Hardware Reset
DC / RS / A0             GPIO 16              Data / Command Mode
CS                       GPIO 5               Chip Select
BLK / LED                3.3V                 Backlight Power (Always ON)
```

---

## 4. Vision Node (`esp32-cam` — Canopy Imaging)

| Camera MCU Pin | Connection | Function |
|---|---|---|
| **5V** | 5V USB Bus / External 5V Power Supply | Power |
| **GND** | System Ground Bus | Ground Reference |
| **U0R (GPIO 3)**| USB-Serial Rx (for Flashing/Logging) | UART Receive |
| **U0T (GPIO 1)**| USB-Serial Tx (for Flashing/Logging) | UART Transmit |
| **GPIO 0** | Tied to GND during Flash; Floating during Run | Boot Mode Selection |

---

## 5. Breadboard Assembly & Power Distribution Checklist

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       PHYSICAL ASSEMBLY & POWER RAILS                       │
└─────────────────────────────────────────────────────────────────────────────┘

 [ BREADBOARD 1: NODE 1 (ENV & PUMP) ]
   • Red Rail (+): Connected to ESP32 Node 1 VIN (5.0V from USB).
   • Blue Rail (-): Common System Ground Bus.
   • Sub-Rail: 3.3V from ESP32 Node 1 3V3 pin for DHT11 & Display 1 Backlight.

 [ BREADBOARD 2: NODE 2 (CHEMISTRY & ROOTS) ]
   • Red Rail (+): Connected to ESP32 Node 2 VIN (5.0V from USB).
   • Blue Rail (-): Tied to Common Ground Bus.
   • Clean ADC Sub-Rail: 3.3V from ESP32 Node 2 for TDS, Moisture & Display 2.

 [ ELECTRICAL ISOLATION RULE ]
   • The 12V DC pump power supply must NEVER directly touch any ESP32 pin.
   • It must pass exclusively through the Relay mechanical dry contacts.
```
