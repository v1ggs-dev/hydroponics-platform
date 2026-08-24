# Hydroponics Platform — Master Hardware Bill of Materials (BOM)

## 1. System Inventory & Hardware Partitioning

The hardware tier is partitioned across two specialized, autonomous ESP32 microcontrollers, one dedicated ESP32-CAM optical node, and two 1.8" ST7735 SPI TFT color displays:

```mermaid
graph TD
    subgraph NODE1 [ESP32 Node 1: Environment & Actuation (esp32-env)]
        E1[ESP32 DevKit V1 - COM6]
        E1 --> DHT11[DHT11 Air Temp & Humidity - GPIO 4]
        E1 --> FLOW[YF-S201 Flow Sensor - GPIO 13 ISR]
        E1 --> RELAY[5V Relay: Submersible Pump - GPIO 26]
        E1 --> BUZZER[Piezo Buzzer + BC547 - GPIO 25]
        E1 --> DISP1[Display #1: ST7735 1.8 TFT - VSPI]
    end

    subgraph NODE2 [ESP32 Node 2: Water Chemistry & Root Zone (esp32-chem)]
        E2[ESP32 DevKit V1 - COM8]
        E2 --> PH[Analog pH Probe Module - GPIO 34 ADC1_6]
        E2 --> TDS[Analog TDS Probe Module - GPIO 35 ADC1_7]
        E2 --> MOIST[Substrate Moisture Probe - GPIO 32 ADC1_4]
        E2 --> DISP2[Display #2: ST7735 1.8 TFT - VSPI]
    end

    subgraph NODE_CAM [Vision Node: Optical Canopy Node]
        CAM[ESP32-CAM AI-Thinker + OV2640 2MP]
    end
```

---

## 2. Itemized Component Specification

| Component | Part / Model | Operating Voltage | Interface Type | Role / Metrics |
|---|---|---|---|---|
| **MCU Node 1** | ESP32 DevKit V1 (30-Pin, WROOM-32) | 5V VIN / 3.3V Logic | USB UART / SPI / GPIO | Climate, circulation, buzzer alarm, Display 1, dry-run safety |
| **MCU Node 2** | ESP32 DevKit V1 (30-Pin, WROOM-32) | 5V VIN / 3.3V Logic | USB UART / SPI / ADC1 | Isolated water chemistry (pH, TDS, Moisture) & Display 2 |
| **Camera MCU** | ESP32-CAM AI-Thinker + USB-MB Shield| 5V USB | USB UART / DVP / SCCB | Dedicated 2MP canopy image capture node |
| **Camera Sensor** | Omnivision OV2640 | 3.3V (Internal LDO) | 8-bit Parallel DVP / SCCB | Optical plant canopy image acquisition |
| **pH Sensor** | Analog pH Probe & Conditioning Board| 5V VCC / 0.0–3.3V Out | Analog Voltage ADC1_6 (GPIO 34)| Solution acidity / alkalinity ($0.00–14.00\text{ pH}$) |
| **Nutrient Sensor**| Analog TDS Sensor & Signal Board | 3.3V–5.5V (3.3V) | Analog Voltage ADC1_7 (GPIO 35)| Nutrient concentration / EC tracking ($0–2000\text{ ppm}$) |
| **Moisture Sensor**| Capacitive / Resistive Moisture Probe | 3.3V–5V (3.3V) | Analog Voltage ADC1_4 (GPIO 32)| Root zone substrate hydration tracking ($0–100\%$) |
| **Temp & Humidity**| DHT11 Digital Sensor Module | 3.3V Logic | Single-Wire Digital (GPIO 4) | Ambient microclimate monitoring |
| **Water Flow Meter**| YF-S201 Hall-Effect Turbine Meter | 5V VCC / 3.3V Signal | Digital Pulse Interrupt (GPIO 13)| Real-time circulation flow rate & volume |
| **Pump Relay** | 5V 1-Channel Relay Module (Optocoupled)| 5V VCC / 3.3V Logic In | Digital Output Active-LOW (GPIO 26)| High-current DC pump switching |
| **Water Pump** | 12V DC Submersible Mini Water Pump | 9V–12V DC External | Isolated Relay Dry Contacts | Hydroponic nutrient solution circulation |
| **TFT Display #1** | 1.8-inch ST7735 TFT Color SPI LCD (160x128)| 5V VCC / 3.3V Logic | Hardware VSPI (Node 1) | Real-time Climate & Flow 2x2 cockpit |
| **TFT Display #2** | 1.8-inch ST7735 TFT Color SPI LCD (160x128)| 5V VCC / 3.3V Logic | Hardware VSPI (Node 2) | Real-time Water Chemistry 2x2 cockpit |
| **Piezo Buzzer** | 5V Active / Passive Piezo Buzzer | 5V VCC / Transistor | BC547 NPN Switch (GPIO 25) | Boot fanfare & audible safety alarms |
| **Switching BJT** | BC547 NPN General Purpose Transistor | Up to 45V / 100mA | Base Driven via 1kΩ Resistor | Buzzer current amplifier & GPIO protection |

---

## 3. Power Distribution Architecture

- **5V Main USB / DC Rail**:
  - Powers ESP32 Node 1 VIN, ESP32 Node 2 VIN, ESP32-CAM 5V, Flow meter VCC, 5V Relay VCC, 5V Buzzer VCC, and both ST7735 TFT VCC pins.
- **3.3V Clean Logic & ADC Rails**:
  - ESP32-1 Onboard LDO $\rightarrow$ DHT11 VCC, TFT #1 Backlight.
  - ESP32-2 Onboard LDO $\rightarrow$ Clean ADC rail for TDS probe VCC, Moisture probe VCC, and TFT #2 Backlight.
- **12V External DC Isolated Power Rail**:
  - Independent 12V 2.0A DC power brick feeding pump through the optoisolated relay NO (Normally Open) contacts.
- **Common Ground Plane**:
  - All grounds (ESP32-1 GND, ESP32-2 GND, Sensors GND, Display GND, Relay DC GND) share a common low-impedance ground bus.