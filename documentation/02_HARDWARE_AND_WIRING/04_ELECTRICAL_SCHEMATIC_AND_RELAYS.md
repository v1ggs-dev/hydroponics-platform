```markdown
# Hydroponics Platform — Wiring Architecture

## 1. Purpose

This document defines the physical wiring architecture for the
Hydroponics Platform.

It describes how:

- ESP32
- Raspberry Pi 5
- Sensors
- TFT display
- Buzzer
- Relay / MOSFET drivers
- Pumps
- Solenoid valves
- Flow sensors
- Water-level sensors
- Cameras
- Power supplies
- DC/DC converters

should be electrically interconnected.

This document is an architectural wiring specification.

The exact pin assignments are maintained separately in:

    docs/hardware/PINOUT.md

The electrical power architecture is defined in:

    docs/hardware/POWER.md

The hardware inventory and component specifications are defined in:

    docs/hardware/HARDWARE.md

---

# 2. Critical Safety Notice

This document must not be treated as a substitute for the datasheet
of any specific component.

Before wiring a component, verify:

- Supply voltage
- Logic voltage
- Maximum current
- GPIO voltage requirements
- Pin functions
- Polarity
- Connector orientation
- Driver requirements
- Inductive-load requirements

Never connect unknown hardware directly to an ESP32 GPIO.

Never connect mains AC directly to:

- ESP32
- Raspberry Pi
- Breadboard
- Sensors
- GPIO
- Low-voltage relay inputs

Mains-powered equipment must use appropriate electrical protection,
enclosures, switching equipment, and qualified installation.

---

# 3. Wiring Philosophy

The system is divided into:

```text
LOGIC
  ↓
ESP32
  ↓
SENSORS / DISPLAY / LOW-POWER OUTPUTS

EDGE
  ↓
Raspberry Pi 5
  ↓
Camera / Gateway / Computer Vision

ACTUATOR
  ↓
Relay / MOSFET / Driver
  ↓
Pump / Valve
```

The ESP32 is the physical control boundary.

The Raspberry Pi is the edge-computing boundary.

The cloud has no direct electrical connection to the hardware.

---

# 4. High-Level Physical Architecture

```text
                       ┌──────────────────────┐
                       │      POWER INPUT     │
                       └──────────┬───────────┘
                                  │
                         Power Distribution
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
       Raspberry Pi 5           ESP32             Actuator
              │                   │                Supply
              │                   │                   │
          Camera(s)          ┌────┼────┐         ┌────┴────┐
                              │    │    │         │         │
                              ▼    ▼    ▼         ▼         ▼
                           DHT11  TFT Sensors    Pump     Valve
                                      │
                                      ▼
                                  Driver
                                      │
                                      ▼
                                  Buzzer
```

---

# 5. Physical System Layers

The wiring should be considered in five physical layers:

```text
Layer 1 — Power
Layer 2 — ESP32
Layer 3 — Sensors
Layer 4 — Actuator Drivers
Layer 5 — Edge / Camera
```

Each layer should be independently testable.

---

# 6. Layer 1 — Power

The power architecture should provide separate logical paths for:

```text
Raspberry Pi
ESP32 + sensors
Actuators
Cameras / peripherals
```

Conceptually:

```text
                    MAIN DC SOURCE
                          │
                   Protection
                          │
                    Distribution
                          │
          ┌───────────────┼────────────────┐
          │               │                │
          ▼               ▼                ▼
       Pi Supply      ESP32 Supply     Actuator Supply
          │               │                │
          ▼               ▼                ▼
     Raspberry Pi        ESP32          Pump / Valve
```

Exact voltages and current ratings must be determined from the actual
components.

---

# 7. Grounding Architecture

For non-isolated signal connections, an appropriate common reference
may be required.

Example:

```text
ESP32 GND
   │
   ├── DHT11 GND
   ├── Sensor GND
   ├── TFT GND
   └── Driver signal reference
```

However, high-current actuator return currents should not be routed
through sensitive sensor wiring.

Preferred concept:

```text
             POWER DISTRIBUTION
                    │
           ┌────────┴────────┐
           │                 │
       LOGIC RETURN      ACTUATOR RETURN
           │                 │
           ▼                 ▼
         ESP32            Pump/Valve
```

The exact grounding topology must be validated for the selected
hardware.

---

# 8. ESP32 Wiring Boundary

The ESP32 is the central embedded controller.

It interfaces with:

```text
Inputs:
    DHT11
    pH
    TDS
    Flow
    Water Level
    Future Sensors

Outputs:
    TFT
    Buzzer
    Relay
    MOSFET
    Valve Driver
    Pump Driver
```

The ESP32 should not directly drive high-current loads.

---

# 9. DHT11 Wiring

The DHT11 is the initial MVP sensor.

Conceptually:

```text
ESP32                    DHT11

3.3V  ------------------> VCC

GPIO_X -----------------> DATA

GND   ------------------> GND
```

Where:

```text
GPIO_X
```

is the GPIO assigned in:

```text
docs/hardware/PINOUT.md
```

Do not assume a GPIO from this document.

The exact GPIO must be taken from the authoritative pinout.

---

# 10. DHT11 Data Line

The DHT11 uses a single digital data line.

Depending on the specific DHT11 implementation, a pull-up resistor may
be required.

Some modules already contain the required resistor.

Verify the exact module before adding an additional resistor.

---

# 11. DHT11 Wiring Rules

Do not:

```text
DHT11 DATA → random GPIO
```

without checking the firmware pin configuration.

Do not:

```text
DHT11 VCC → unknown voltage
```

without checking the sensor/module specification.

The ESP32 GPIO voltage limits must always be respected.

---

# 12. TFT SPI Wiring

The TFT display communicates with the ESP32 using SPI and additional
control signals.

Typical logical connections:

```text
ESP32                     TFT

SPI SCK   --------------> SCK / CLK

SPI MOSI  --------------> MOSI / SDA

GPIO      --------------> CS

GPIO      --------------> DC / A0

GPIO      --------------> RST

GND       --------------> GND

Power     --------------> VCC
```

The exact pins are defined in:

```text
docs/hardware/PINOUT.md
```

The display's logic and backlight voltage must be verified.

---

# 13. TFT MISO

Some TFT displays do not require MISO for normal write-only operation.

If the selected display requires reading:

```text
TFT MISO
```

may also be connected to the ESP32 SPI input.

Do not connect unused signals unnecessarily.

---

# 14. TFT Backlight

The display backlight may have a higher current requirement than the
display logic.

Do not assume:

```text
TFT backlight → ESP32 GPIO
```

is safe.

If backlight control is required, use an appropriate driver.

Conceptually:

```text
ESP32 GPIO
    ↓
Transistor / MOSFET
    ↓
TFT Backlight
```

---

# 15. Buzzer Wiring

The buzzer should normally be driven through an appropriate transistor
or MOSFET when the required current exceeds the safe GPIO capability.

Conceptually:

```text
ESP32 GPIO
     │
     ▼
Driver
     │
     ▼
Buzzer
     │
     ▼
GND
```

Power must come from an appropriate supply rail.

---

# 16. Buzzer With Transistor Driver

Preferred concept:

```text
                    +V
                     │
                     │
                   Buzzer
                     │
                     ▼
                  Collector
                     │
ESP32 GPIO ──R──> Base/Gate
                     │
                  Transistor
                     │
                     ▼
                    GND
```

The exact circuit depends on whether the selected buzzer is:

- Active buzzer
- Passive buzzer
- Electromagnetic buzzer
- Other type

The component datasheet is authoritative.

---

# 17. Relay Wiring

A relay should be treated as a switching interface.

Conceptually:

```text
ESP32 GPIO
    │
    ▼
Relay Module Input
    │
    ▼
Relay Coil / Driver
    │
    ▼
Relay Contacts
    │
    ▼
Actuator
```

The ESP32 should only interface with the relay input/driver.

The actuator's operating current must not flow through the ESP32.

---

# 18. Relay Power

Some relay modules require a separate supply for the relay coil.

The exact module must be checked for:

```text
Coil voltage
Input logic voltage
Trigger polarity
Input current
Isolation
Contact rating
```

Do not assume a relay module is automatically 3.3V logic compatible.

---

# 19. Relay Active-Low Warning

Some relay modules activate when the input is LOW.

Others activate when the input is HIGH.

The firmware must explicitly define:

```text
ACTIVE_HIGH
```

or:

```text
ACTIVE_LOW
```

for the selected hardware.

Never assume:

```text
GPIO HIGH = relay ON
```

---

# 20. Pump Wiring

A pump should use a dedicated actuator power path.

Conceptually:

```text
                  ACTUATOR SUPPLY
                        │
                        ▼
                     FUSE/
                   PROTECTION
                        │
                        ▼
                  RELAY / MOSFET
                        │
                        ▼
                       PUMP
                        │
                        ▼
                 ACTUATOR RETURN
```

The exact wiring depends on whether the pump is:

```text
DC
```

or:

```text
AC
```

DC and AC loads require different switching/protection approaches.

---

# 21. DC Pump

For a DC pump:

```text
Supply +
   │
   ▼
Switching Device
   │
   ▼
Pump +
Pump -
   │
   ▼
Supply -
```

If the pump is an inductive DC load, appropriate transient suppression
must be installed.

---

# 22. AC Pump

If the pump is mains-powered:

```text
Mains
   ↓
Protection
   ↓
Properly Rated Switching Device
   ↓
Pump
```

The ESP32 must never directly interface with mains wiring.

Mains wiring must be enclosed and professionally installed.

This project should preferentially use a suitable low-voltage DC pump
for the early prototype where practical.

---

# 23. Solenoid Valve Wiring

A DC solenoid valve typically follows:

```text
Actuator Supply
      │
      ▼
Switching Driver
      │
      ▼
Solenoid Valve
      │
      ▼
Actuator Return
```

Because a solenoid is inductive, use appropriate transient protection.

---

# 24. MOSFET Wiring

For a suitable DC actuator, a low-side MOSFET arrangement may be used.

Conceptually:

```text
                 +V
                  │
                  │
               ACTUATOR
                  │
                  ▼
              Drain
ESP32 ─────── Gate
              MOSFET
              Source
                  │
                  ▼
                 GND
```

The actual MOSFET must be appropriate for:

- Load voltage
- Load current
- Gate voltage
- Switching frequency
- Thermal conditions

---

# 25. Flyback Protection

For DC inductive loads:

```text
Pump
Solenoid
Relay Coil
Motor
```

appropriate flyback/transient suppression may be required.

Conceptually:

```text
          +V
           │
       ┌───┴────┐
       │ Load   │
       └───┬────┘
           │
           ▼
       Switching
        Device
           │
          GND
```

The suppression component is connected according to the specific
switching topology.

Do not blindly use the same protection circuit for AC loads.

---

# 26. pH Sensor Wiring

A pH probe should not be connected directly to the ESP32.

Correct architecture:

```text
pH Probe
    │
    ▼
pH Interface Board
    │
    ├── Power
    ├── Ground
    └── Analog Output
             │
             ▼
           ESP32 ADC
```

The interface board must provide an ESP32-compatible signal.

---

# 27. pH Analog Signal

Before connecting:

```text
pH interface output
```

to an ESP32 ADC, verify:

```text
Minimum output voltage
Maximum output voltage
Signal conditioning
ADC compatibility
Ground reference
```

If required, use:

```text
Voltage divider
Op-amp
Level shifter
Other signal conditioning
```

as appropriate.

---

# 28. TDS Sensor Wiring

Typical architecture:

```text
TDS Probe
    │
    ▼
TDS Interface
    │
    ├── Power
    ├── Ground
    └── Signal
             │
             ▼
           ESP32
```

The exact interface depends on the selected TDS module.

Do not connect a raw probe directly to a GPIO.

---

# 29. Flow Sensor Wiring

A typical pulse-output flow sensor follows:

```text
Flow Sensor
    │
    ├── VCC
    ├── GND
    │
    └── Pulse Output
             │
             ▼
          ESP32 GPIO
```

The output voltage must be verified.

If necessary:

```text
Flow Sensor
    ↓
Level Shifter
    ↓
ESP32 GPIO
```

The ESP32 can count pulses to calculate flow.

---

# 30. Flow Sensor Placement

For reliable measurement, the flow sensor should be placed according
to the manufacturer's requirements.

Consider:

```text
Pipe orientation
Straight pipe length
Flow direction
Air bubbles
Maximum pressure
Maximum flow
Connector sealing
```

The sensor should not be mechanically stressed by the pipe.

---

# 31. Water-Level Sensor Wiring

Example using a digital float switch:

```text
Float Switch
    │
    ├── GND
    │
    └── ESP32 GPIO
```

The firmware may use an internal pull-up if appropriate.

Conceptually:

```text
HIGH = WATER OK
LOW  = LOW WATER
```

or the reverse depending on wiring.

The exact logic must be defined in firmware.

---

# 32. Water-Level Sensor Safety

For pump protection:

```text
Water Level Sensor
       ↓
ESP32
       ↓
Safety Rule
       ↓
Pump Allowed?
```

If the sensor reports an unsafe state:

```text
Pump = OFF
```

This decision must be local.

---

# 33. ESP32-CAM Wiring

If using a separate ESP32-CAM:

```text
ESP32-CAM
    │
    ├── Power
    └── Wi-Fi
          │
          ▼
      Raspberry Pi
```

It should normally be treated as a separate network device rather than
physically wiring it to the main ESP32.

---

# 34. Raspberry Pi Camera Wiring

For a Raspberry Pi camera module:

```text
Camera
   │
   ▼
Raspberry Pi Camera Interface
   │
   ▼
Raspberry Pi 5
```

For a USB camera:

```text
USB Camera
    │
    ▼
USB
    │
    ▼
Raspberry Pi 5
```

The camera must not share an inadequately sized power rail.

---

# 35. Raspberry Pi ↔ ESP32

The primary communication link is wireless.

Preferred architecture:

```text
ESP32
  │
 Wi-Fi
  │
  ▼
Raspberry Pi 5
```

No physical UART cable is required for normal operation if Wi-Fi is
used.

---

# 36. Raspberry Pi as Wi-Fi Access Point

The Raspberry Pi may provide the local Wi-Fi network.

Conceptually:

```text
                 RASPBERRY PI
                Wi-Fi Access Point
                       │
                ┌──────┴──────┐
                │             │
                ▼             ▼
              ESP32       ESP32-CAM
```

This allows the hardware system to operate without a separate
third-party Wi-Fi router.

---

# 37. Local Network Isolation

The local hardware network should ideally expose only the services
required for:

```text
ESP32
ESP32-CAM
Raspberry Pi Gateway
```

The ESP32 should not need unrestricted access to the Raspberry Pi OS.

---

# 38. Ethernet to Cloud

The Raspberry Pi may connect to the internet through:

```text
Ethernet
```

or:

```text
Wi-Fi
```

or another supported WAN connection.

Conceptually:

```text
ESP32
  │
Wi-Fi
  │
  ▼
Raspberry Pi
  │
WAN
  │
  ▼
Internet
```

---

# 39. Communication Separation

The physical wiring architecture is independent from cloud
communication.

The physical chain is:

```text
Sensor
   ↓
ESP32
   ↓
Wi-Fi
   ↓
Raspberry Pi
```

The cloud chain is:

```text
Raspberry Pi
   ↓
MQTT
   ↓
Cloud
```

This separation allows the ESP32 to remain functional during internet
failure.

---

# 40. Breadboard MVP Wiring

The initial DHT11 MVP should remain simple.

Recommended:

```text
ESP32 Dev Board
       │
       ├── 3.3V ────── DHT11 VCC
       │
       ├── GPIO_X ──── DHT11 DATA
       │
       └── GND ─────── DHT11 GND
```

Do not add the pump or valve to the same breadboard power rail.

---

# 41. MVP Development Wiring

The recommended development sequence is:

```text
STEP 1

ESP32
  │
  └── DHT11
```

Then:

```text
STEP 2

ESP32
  │
  ├── DHT11
  └── TFT
```

Then:

```text
STEP 3

ESP32
  │
  ├── DHT11
  ├── TFT
  └── Buzzer
```

Then:

```text
STEP 4

ESP32
  │
  ├── Sensors
  └── Actuator Driver
```

Then:

```text
STEP 5

Actuator Driver
       │
       ▼
     Pump
```

This minimizes troubleshooting complexity.

---

# 42. Do Not Introduce All Hardware at Once

Avoid this during the first bring-up:

```text
ESP32
 + DHT11
 + pH
 + TDS
 + TFT
 + Buzzer
 + Pump
 + Valve
 + Relay
 + Flow Sensor
 + Camera
```

If something fails, identifying the cause becomes difficult.

Instead, integrate one subsystem at a time.

---

# 43. Physical Separation

The final enclosure should separate:

```text
LOW-VOLTAGE LOGIC
```

from:

```text
HIGH-CURRENT ACTUATORS
```

and from:

```text
WATER / LIQUID PATH
```

Conceptually:

```text
┌──────────────────────────────┐
│ ELECTRONICS ENCLOSURE        │
│                              │
│ ESP32                        │
│ Raspberry Pi                 │
│ DC/DC Converters             │
│ Relay / MOSFET Drivers       │
│ Power Distribution           │
└──────────────────────────────┘

             │

             │ protected wiring

             ▼

┌──────────────────────────────┐
│ WATER / HYDRAULIC SYSTEM     │
│                              │
│ Reservoir                    │
│ Pump                         │
│ Valve                        │
│ Flow Sensor                  │
│ Hydroponic Channels          │
└──────────────────────────────┘
```

---

# 44. Cable Management

Use separate cable paths where practical for:

```text
Power
Digital signals
Analog signals
Actuator wiring
Camera cables
Network cables
```

Avoid running sensitive analog sensor wires immediately alongside
high-current motor wires for long distances.

---

# 45. Analog Signal Wiring

For pH and TDS/EC:

```text
Probe
  ↓
Interface
  ↓
Short / protected analog connection
  ↓
ESP32 ADC
```

Keep analog wiring:

- Short where possible.
- Away from motors.
- Away from relay switching wires.
- Properly referenced to ground.
- Mechanically secure.

---

# 46. Digital Signal Wiring

Digital sensor lines should use:

- Appropriate pull-up/pull-down resistors.
- Short connections where practical.
- Correct logic levels.
- Appropriate shielding for long/noisy connections.

---

# 47. SPI Wiring

SPI signals should be routed cleanly:

```text
SCK
MOSI
MISO
CS
DC
RST
```

Avoid excessively long breadboard jumper wires in the final design.

If multiple SPI peripherals are used:

```text
SCK  ─────────────┬── Device A
                  ├── Device B
                  └── Device C

MOSI ─────────────┬── Device A
                  ├── Device B
                  └── Device C

CS_A ───────────────── Device A
CS_B ───────────────── Device B
CS_C ───────────────── Device C
```

Each device should have an appropriate chip-select strategy.

---

# 48. ADC Wiring

Analog sensors should use designated ADC-capable ESP32 pins according
to the selected ESP32 variant.

The exact ADC pins must be maintained in:

```text
docs/hardware/PINOUT.md
```

Avoid assuming every ESP32 GPIO is equivalent for ADC use.

---

# 49. Pin Assignment Rule

No other document should independently invent GPIO mappings.

The authoritative mapping is:

```text
docs/hardware/PINOUT.md
```

If a wiring diagram conflicts with `PINOUT.md`, update the documentation
rather than silently choosing a different GPIO.

---

# 50. Logical vs Physical Names

Use logical names in software:

```text
dht11-01
pump-01
valve-01
flow-01
```

Use physical names in wiring documentation:

```text
ESP32 GPIO_X
5V rail
GND rail
Relay CH1
```

This separation allows the hardware implementation to change without
breaking the software API.

---

# 51. Wiring Documentation Convention

Every component should document:

```text
Component
Purpose
Supply
Ground
Signal
ESP32 GPIO
Driver
Protection
Notes
```

Example:

```text
DHT11
    VCC  → 3.3V
    GND  → GND
    DATA → GPIO_X
```

The actual `GPIO_X` must come from `PINOUT.md`.

---

# 52. Example Wiring Table

| Component | Power | Ground | Signal | Interface | Notes |
|---|---|---|---|---|---|
| DHT11 | Logic rail | Logic GND | GPIO | Digital | Verify pull-up |
| TFT | Spec-defined | Logic GND | SPI + control | SPI | Verify voltage |
| Buzzer | Appropriate rail | Appropriate GND | GPIO → driver | Digital | Don't overload GPIO |
| pH interface | Spec-defined | Analog GND | ADC | Analog | Verify output range |
| TDS interface | Spec-defined | Analog GND | ADC | Analog | Verify output range |
| Flow sensor | Spec-defined | GND | Pulse | Digital | Verify output voltage |
| Float switch | Logic rail/GND | GND | GPIO | Digital | Define fail-safe logic |
| Relay | Spec-defined | GND | GPIO/driver | Digital | Check trigger polarity |
| Pump | Actuator rail | Actuator return | Driver | Power | Dedicated supply |
| Valve | Actuator rail | Actuator return | Driver | Power | Inductive protection |
| Camera | Spec-defined | Spec-defined | CSI/USB/Wi-Fi | Camera | Check Pi power budget |

This table is an architectural reference.

The exact values belong in the final hardware configuration.

---

# 53. Safe Actuator Defaults

The hardware should be designed so that controller reset or power loss
does not unintentionally activate dangerous actuators.

Preferred:

```text
ESP32 OFF
    ↓
Pump OFF
Valve SAFE/CLOSED
Buzzer OFF
```

The actual default state must be validated against the driver circuit.

---

# 54. Relay Safety

A relay can be active during:

```text
ESP32 boot
GPIO initialization
Power-up
Power-down
```

The firmware must initialize outputs carefully.

The hardware should also be designed so that undefined GPIO states do
not unintentionally activate the actuator.

---

# 55. MOSFET Safety

MOSFET gates should not be left floating.

Where appropriate, use a defined gate state so that:

```text
ESP32 OFF
```

produces:

```text
MOSFET OFF
```

The exact pull-down/pull-up configuration depends on the switching
topology.

---

# 56. Sensor Disconnect Behavior

Every sensor should have defined behavior when disconnected.

Example:

```text
DHT11 disconnected
       ↓
ESP32 detects invalid reading
       ↓
Sensor status = ERROR
```

For safety-critical sensors:

```text
Sensor unavailable
       ↓
Assume unsafe
       ↓
Disable affected actuator
```

---

# 57. Pump Control Safety

The pump should not be allowed to run indefinitely due to:

- Network failure
- Software bug
- Stale command
- Sensor failure
- Backend failure

Possible local protections:

```text
Maximum runtime
Water-level interlock
Flow verification
Thermal protection
Emergency shutdown
```

---

# 58. Valve Control Safety

The valve subsystem should have:

```text
Maximum open duration
Safe default state
Command timeout
Local safety checks
```

The exact logic depends on whether the valve is:

```text
Normally closed
Normally open
Motorized
Solenoid
```

---

# 59. Water Isolation

Where practical:

```text
Electrical enclosure
```

should be physically separated from:

```text
Water reservoir
Pump
Tubing
Valves
Hydroponic channels
```

Use:

```text
Drip loops
Cable glands
Water-resistant connectors
Raised mounting
```

where appropriate.

---

# 60. Final Physical Architecture

The complete physical system should conceptually resemble:

```text
                         MAIN POWER
                             │
                    ┌────────┴────────┐
                    │                 │
                    ▼                 ▼
              LOGIC POWER       ACTUATOR POWER
                    │                 │
            ┌───────┴───────┐        │
            │               │        │
            ▼               ▼        ▼
       Raspberry Pi       ESP32    Driver
            │               │        │
          Camera       ┌────┼────┐    ├── Pump
            │          │    │    │    │
            │          ▼    ▼    ▼    └── Valve
            │        DHT11 TFT Sensors
            │
            │
            └──────── Wi-Fi ──────── ESP32
```

---

# 61. Complete Data + Wiring Boundary

The physical system connects to the software system as follows:

```text
                 PHYSICAL SYSTEM

Sensors ───────────────┐
                       │
Actuators ─────────────┤
                       ▼
                    ESP32
                       │
                    Wi-Fi
                       │
                       ▼
                 Raspberry Pi
                       │
                     MQTT
                       │
                       ▼

                  CLOUD SYSTEM

                    Backend
                       │
                 PostgreSQL
                       │
                  WebSocket
                       │
                       ▼
                   Dashboard
```

The cloud never has a direct physical electrical connection.

---

# 62. MVP Wiring

The initial project should use only:

```text
ESP32
DHT11
Breadboard
Jumper wires
USB power
```

The first objective is:

```text
DHT11
  ↓
ESP32
  ↓
Temperature / Humidity
```

Then integrate:

```text
ESP32
  ↓
Wi-Fi
  ↓
Raspberry Pi
```

Then:

```text
Raspberry Pi
  ↓
MQTT
  ↓
Backend
```

Then:

```text
Backend
  ↓
Frontend
```

---

# 63. Recommended Hardware Integration Order

Use the following order:

```text
1. ESP32
       ↓
2. DHT11
       ↓
3. Serial monitoring
       ↓
4. ESP32 Wi-Fi
       ↓
5. Raspberry Pi
       ↓
6. MQTT
       ↓
7. Backend
       ↓
8. PostgreSQL
       ↓
9. Frontend
       ↓
10. TFT
       ↓
11. Buzzer
       ↓
12. Flow sensor
       ↓
13. Water-level sensor
       ↓
14. pH
       ↓
15. TDS
       ↓
16. Relay/MOSFET
       ↓
17. Pump
       ↓
18. Valve
       ↓
19. Camera
       ↓
20. Computer Vision
```

This order prioritizes low-risk components before high-current
actuators.

---

# 64. Wiring Verification Checklist

Before powering any circuit:

```text
[ ] Component datasheet reviewed
[ ] Supply voltage verified
[ ] Current requirement verified
[ ] GPIO voltage verified
[ ] Pinout verified
[ ] Polarity verified
[ ] GND verified
[ ] Driver requirements verified
[ ] Protection components verified
[ ] Wiring visually inspected
[ ] No accidental shorts
[ ] Actuator disconnected during initial test
[ ] Safe actuator state confirmed
```

---

# 65. First-Power Checklist

For a new subsystem:

```text
[ ] Power OFF
[ ] Wiring complete
[ ] Continuity checked where appropriate
[ ] Voltage rail measured
[ ] Correct polarity confirmed
[ ] Load connected only after voltage validation
[ ] ESP32 powered
[ ] Serial logs checked
[ ] Sensor output verified
[ ] Temperature monitored
[ ] No unexpected reset
[ ] No abnormal heating
```

---

# 66. Troubleshooting Strategy

When something does not work, isolate the subsystem.

Use:

```text
Power
  ↓
ESP32
  ↓
Sensor
  ↓
Driver
  ↓
Actuator
  ↓
Network
```

Do not debug:

```text
hardware + MQTT + backend + frontend
```

simultaneously.

---

# 67. Common Failure Modes

## ESP32 resets

Check:

```text
Power supply
Voltage drop
Current capacity
USB cable
Brownout
Actuator noise
```

---

## Sensor reads invalid values

Check:

```text
Supply voltage
Ground
GPIO
Pull-up
Signal integrity
Library configuration
Sensor wiring
```

---

## Relay activates unexpectedly

Check:

```text
Active-high/active-low
GPIO boot state
Floating input
Relay driver
Firmware initialization
```

---

## Pump causes ESP32 reset

Check:

```text
Shared power rail
Ground path
Pump startup current
Converter capacity
Flyback/transient suppression
Relay/MOSFET wiring
```

---

## Analog sensor is noisy

Check:

```text
Grounding
Power noise
Pump switching
Cable routing
ADC configuration
Signal conditioning
Sensor placement
```

---

# 68. Final Wiring Invariants

The following rules must remain true unless explicitly changed by an
architecture decision.

### Invariant 1

The ESP32 does not directly power high-current actuators.

### Invariant 2

Every sensor's voltage requirements are verified before connection.

### Invariant 3

Every GPIO signal is verified against the ESP32's electrical limits.

### Invariant 4

Pumps and valves use appropriately rated switching hardware.

### Invariant 5

Inductive loads have appropriate transient protection.

### Invariant 6

High-current actuator wiring does not rely on breadboard traces.

### Invariant 7

The Raspberry Pi has its own appropriately rated power path.

### Invariant 8

The ESP32 has a stable regulated power source.

### Invariant 9

Sensitive analog wiring is kept away from noisy actuator wiring where
practical.

### Invariant 10

Actuators have defined safe states.

### Invariant 11

Water and electrical systems are physically separated and protected.

### Invariant 12

The authoritative GPIO assignments are maintained in:

```text
docs/hardware/PINOUT.md
```

### Invariant 13

Power architecture is maintained in:

```text
docs/hardware/POWER.md
```

### Invariant 14

The actual hardware datasheet overrides this document.

---

# 69. Final Wiring Architecture

The final physical architecture is:

```text
                       POWER SYSTEM
                            │
                 ┌──────────┼──────────┐
                 │          │          │
                 ▼          ▼          ▼
              Raspberry   ESP32     Actuator
               Pi 5                  Supply
                 │          │          │
              Camera    ┌────┼────┐    │
                        │    │    │    │
                        ▼    ▼    ▼    ▼
                      DHT11 TFT Sensors Driver
                                             │
                                      ┌──────┴──────┐
                                      │             │
                                      ▼             ▼
                                    Pump          Valve


                         NETWORK
                            │
                            ▼
                      Raspberry Pi
                            │
                          Wi-Fi
                            │
                            ▼
                          ESP32


                         CLOUD
                            │
                            ▼
                      MQTT / Backend
                            │
                            ▼
                       Dashboard
```

The physical wiring system must preserve three distinct concerns:

```text
1. POWER
2. SIGNAL
3. COMMUNICATION
```

The ESP32 owns physical I/O and immediate safety.

The Raspberry Pi owns edge connectivity and computation.

The cloud owns application-level monitoring, persistence, automation,
and remote control.

The wiring must never allow a software failure, network failure, or
cloud failure to bypass the physical safety characteristics of the
hardware.
```