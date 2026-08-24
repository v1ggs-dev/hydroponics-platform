# Document 03 — Hardware & Electronics Specification

**Document Purpose:**  
Provide a deep, authoritative hardware engineering reference specifying the complete bill of materials, microcontroller pinout, exact point-to-point connection relationships, power distribution architecture, sensor acquisition electronics, actuator driver circuits, safety mechanisms, and physical electrical layout for the Dual-ESP32, Dual-Display & pH Sensor platform architecture.

**Status:** Updated & Approved  
**Source of Truth:** Repository codebase (`firmware/esp32_env/`, `firmware/esp32_chem/`, `firmware/esp32_cam/`) and `documentation/`

---

## 1. Hardware Inventory & Component Breakdown

The hardware tier consists of 2 dedicated, autonomous ESP32 microcontrollers, 1 dedicated ESP32-CAM node, precision analog/digital sensors including analog pH, 2 high-contrast ST7735 color displays, and galvanically isolated actuator switching modules.

```mermaid
graph TD
    subgraph POWER_DISTRIBUTION [Power Distribution Architecture]
        USB_5V[5V USB Dual Bus Supply] --> VCC_5V[5V Main Power Rail]
        EXT_12V[External 9V-12V DC Supply] --> PUMP_PWR[Isolated Pump Power Circuit]
        VCC_5V --> ESP32_ENV_VIN[ESP32 Node 1 VIN Pin]
        VCC_5V --> ESP32_CHEM_VIN[ESP32 Node 2 VIN Pin]
        ESP32_ENV_VIN --> ESP32_ENV_LDO[ESP32-1 Onboard 3.3V LDO]
        ESP32_CHEM_VIN --> ESP32_CHEM_LDO[ESP32-2 Onboard 3.3V LDO]
        ESP32_ENV_LDO --> VCC_3V3_1[3.3V Logic Bus 1]
        ESP32_CHEM_LDO --> VCC_3V3_2[3.3V Clean ADC Bus 2]
        VCC_5V --> COMMON_GND[Common Ground Plane]
    end

    subgraph NODE1 [ESP32 Node 1: Environment & Actuation Master (esp32-env)]
        E1_MCU[ESP32 DevKit V1 - COM6]
        E1_MCU --> DHT11_SENS[DHT11 Temp & Humidity - GPIO 4]
        E1_MCU --> FLOW_SENS[YF-S201 Flow Sensor - GPIO 13 ISR]
        E1_MCU --> RELAY_MOD[5V Relay: Pump Switch - GPIO 26]
        E1_MCU --> PIEZO_BUZZ[5V Buzzer + BC547 - GPIO 25]
        E1_MCU --> DISP1[Display #1: ST7735 1.8 TFT - VSPI]
        E1_MCU --> SAF1[8s Dry-Run & 300s Safety State Machine]
    end

    subgraph NODE2 [ESP32 Node 2: Water Chemistry & Root Specialist (esp32-chem)]
        E2_MCU[ESP32 DevKit V1 - COM8]
        E2_MCU --> PH_SENS[Analog pH Probe Module - GPIO 34 ADC1_6]
        E2_MCU --> TDS_SENS[Analog TDS Probe Module - GPIO 35 ADC1_7]
        E2_MCU --> MOIST_SENS[Substrate Moisture Probe - GPIO 32 ADC1_4]
        E2_MCU --> DISP2[Display #2: ST7735 1.8 TFT - VSPI]
    end

    subgraph CAMERA_NODE [Dedicated Vision Node]
        CAM_MCU[ESP32-CAM AI-Thinker + OV2640 2MP]
    end
```

### 1.1 Itemized Hardware Bill of Materials (BOM)

| Component | Part / Model | Operating Voltage | Interface Type | Primary Role |
|---|---|---|---|---|
| MCU Node 1 | ESP32 DevKit V1 (30-Pin, ESP-WROOM-32) | 5V VIN / 3.3V Logic | Wired USB UART / SPI / GPIO | Climate acquisition, fluid circulation, buzzer alarm, Display #1, local safety interlocks |
| MCU Node 2 | ESP32 DevKit V1 (30-Pin, ESP-WROOM-32) | 5V VIN / 3.3V Logic | Wired USB UART / SPI / ADC1 | Isolated high-impedance water chemistry (pH, TDS, Moisture) & Display #2 |
| Camera MCU | ESP32-CAM (AI-Thinker) + USB-MB Shield | 5V USB | Wired USB UART / DVP / SCCB | Dedicated 2MP canopy image capture node |
| Camera Sensor | Omnivision OV2640 | 3.3V (Internal LDO) | 8-bit Parallel DVP / I2C SCCB | Optical plant canopy image acquisition |
| pH Sensor | Analog pH Probe & Signal Board | 5V VCC / 0.0–3.3V Out | Analog Voltage ADC1_CH6 (GPIO 34) | Solution acidity / alkalinity ($0.00–14.00\text{ pH}$) |
| Nutrient Sensor | Analog TDS Sensor & Signal Board | 3.3V–5.5V (3.3V) | Analog Voltage ADC1_CH7 (GPIO 35) | Nutrient concentration / EC tracking ($0–2000\text{ ppm}$) |
| Moisture Sensor | Capacitive / Resistive Moisture Probe | 3.3V–5V (3.3V) | Analog Voltage ADC1_CH4 (GPIO 32) | Root zone substrate hydration tracking ($0–100\%$) |
| Temp & Humidity | DHT11 Digital Sensor Module | 3.3V Logic | Single-Wire Digital (GPIO 4) | Ambient microclimate monitoring |
| Water Flow Meter| YF-S201 Hall-Effect Turbine Meter | 5V VCC / 3.3V Signal | Digital Pulse Interrupt (GPIO 13)| Real-time circulation flow rate & volume |
| Pump Relay | 5V 1-Channel Relay Module (Optocoupled) | 5V VCC / 3.3V Logic In | Digital Output Active-LOW (GPIO 26)| High-current DC pump switching |
| Water Pump | 12V DC Submersible Mini Water Pump | 9V–12V DC External | Isolated Relay Dry Contacts | Hydroponic nutrient solution circulation |
| TFT Display #1 | 1.8-inch ST7735 TFT Color SPI LCD (160x128) | 5V VCC / 3.3V Logic | Hardware VSPI (Node 1) | Real-time Climate & Flow 2x2 cockpit |
| TFT Display #2 | 1.8-inch ST7735 TFT Color SPI LCD (160x128) | 5V VCC / 3.3V Logic | Hardware VSPI (Node 2) | Real-time Water Chemistry 2x2 cockpit |
| Piezo Buzzer | 5V Active / Passive Piezo Buzzer | 5V VCC / Transistor | BC547 NPN Switch (GPIO 25) | Boot fanfare & audible safety alarms |
| Switching BJT | BC547 NPN General Purpose Transistor | Up to 45V / 100mA | Base Driven via 1kΩ Resistor | Buzzer current amplifier & GPIO protection |

---

## 2. Master Microcontroller Pinout Matrices

### 2.1 ESP32 Node 1 (`esp32-env` — Environment & Actuation Master)

| ESP32 Pin | Primary Function | Direction | Electrical Characteristics | Connected Subsystem / Component |
|---|---|---|---|---|
| `GPIO 4` | Digital I/O | Input / Output | 3.3V Logic with 10kΩ External Pull-up | DHT11 Data Line (`DHTPIN`) |
| `GPIO 13` | Digital Input | Input (Interrupt) | 3.3V Logic (`FALLING` Edge ISR) | YF-S201 Flow Sensor Pulse Line (`FLOW_PIN`) |
| `GPIO 26` | Digital Output | Output | 3.3V Logic (Active-LOW Trigger) | 5V Relay Module Input (`RELAY_PIN`) |
| `GPIO 25` | Digital Output / PWM | Output | 3.3V Logic into 1kΩ Resistor to BJT Base | BC547 NPN Buzzer Driver (`BUZZER_PIN`) |
| `GPIO 18` | Hardware VSPI SCK | Output | 3.3V High-Speed SPI Serial Clock | ST7735 Display #1 Clock (`TFT_SCLK`) |
| `GPIO 23` | Hardware VSPI MOSI| Output | 3.3V High-Speed SPI Master-Out Data | ST7735 Display #1 Data / SDA (`TFT_MOSI`) |
| `GPIO 16` | Digital Output | Output | 3.3V Logic Data / Command Select | ST7735 Display #1 DC / A0 (`TFT_DC`) |
| `GPIO 17` | Digital Output | Output | 3.3V Logic Active-LOW Hardware Reset | ST7735 Display #1 Reset (`TFT_RST`) |
| `GPIO 5` | Hardware VSPI CS | Output | 3.3V Logic Active-LOW Chip Select | ST7735 Display #1 Chip Select (`TFT_CS`) |
| `VIN` | Power Input | Power | 5.0V DC Input (from Micro-USB or Rail) | Power input from 5V bus |
| `3V3` | Power Output | Power | 3.3V DC Regulated Output (max ~500mA) | Sensor logic power rail |
| `GND` | System Ground | Power | 0.0V Common Ground Reference | Common ground plane |

### 2.2 ESP32 Node 2 (`esp32-chem` — Water Chemistry & Root Zone)

| ESP32 Pin | Primary Function | Direction | Electrical Characteristics | Connected Subsystem / Component |
|---|---|---|---|---|
| `GPIO 34` | ADC1_CH6 | Analog Input Only | 0.0V–3.3V ADC Range (Input-Only Pin) | Analog pH Probe Signal Board Output |
| `GPIO 35` | ADC1_CH7 | Analog Input Only | 0.0V–3.3V ADC Range (Input-Only Pin) | Analog TDS Signal Board Output |
| `GPIO 32` | ADC1_CH4 | Analog Input Only | 0.0V–3.3V ADC Range (Input-Only Pin) | Substrate Moisture Probe Output |
| `GPIO 18` | Hardware VSPI SCK | Output | 3.3V High-Speed SPI Serial Clock | ST7735 Display #2 Clock (`TFT_SCLK`) |
| `GPIO 23` | Hardware VSPI MOSI| Output | 3.3V High-Speed SPI Master-Out Data | ST7735 Display #2 Data / SDA (`TFT_MOSI`) |
| `GPIO 16` | Digital Output | Output | 3.3V Logic Data / Command Select | ST7735 Display #2 DC / A0 (`TFT_DC`) |
| `GPIO 17` | Digital Output | Output | 3.3V Logic Active-LOW Hardware Reset | ST7735 Display #2 Reset (`TFT_RST`) |
| `GPIO 5` | Hardware VSPI CS | Output | 3.3V Logic Active-LOW Chip Select | ST7735 Display #2 Chip Select (`TFT_CS`) |
| `VIN` | Power Input | Power | 5.0V DC Input (from Micro-USB or Rail) | Power input from 5V bus |
| `3V3` | Power Output | Power | 3.3V DC Regulated Output (max ~500mA) | Clean ADC sensor logic power rail |
| `GND` | System Ground | Power | 0.0V Common Ground Reference | Common ground plane |

---

## 3. Analog pH Sensor Electronics & Mathematical Model

The analog pH module uses a high-impedance glass bulb electrode generating an electromotive force (EMF) described by the Nernst Equation. The signal conditioning board converts the high-impedance microvolt signal to a low-impedance $0.0\text{V}–3.3\text{V}$ analog output:

$$V_{\text{adc}} = \frac{\text{ADC}_{\text{raw}}}{4095.0} \times 3.3\text{ V}$$

$$\text{pH Value} = 7.00 + \frac{V_{\text{neutral}} - V_{\text{adc}}}{\text{Slope} \times \left(1.0 + 0.003 \times (T_{\text{water}} - 25.0)\right)}$$

- $V_{\text{neutral}} = 1.65\text{V}$ (Midpoint calibration voltage for neutral pH 7.00 at 3.3V operating reference).
- $\text{Slope} = 0.18\text{ V/pH}$ (Standard glass electrode sensitivity).
- Continuous 30-sample median filter in firmware eliminates mains hum and high-frequency RF ripple.
