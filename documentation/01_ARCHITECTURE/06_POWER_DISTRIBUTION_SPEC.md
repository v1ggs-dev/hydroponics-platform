```markdown
# Hydroponics Platform — Power Architecture

## 1. Purpose

This document defines the electrical power architecture for the
Hydroponics Platform.

The system contains both low-voltage electronics and potentially
higher-current inductive loads such as:

- Raspberry Pi 5
- ESP32
- Sensors
- TFT display
- Buzzer
- Relay modules
- Pumps
- Solenoid/electrical valves
- Cameras
- DC/DC converters
- Future lighting or dosing equipment

The power architecture must provide:

- Stable power
- Correct voltage levels
- Adequate current capacity
- Electrical isolation where appropriate
- Protection against short circuits
- Protection against inductive loads
- Clean power for sensitive electronics
- Safe actuator switching
- A clear separation between logic power and actuator power

---

# 2. Critical Safety Notice

This document defines the software/hardware architecture, not a
substitute for electrical engineering or manufacturer specifications.

The exact power supply voltage, current rating, wiring, fuse ratings,
wire gauge, connector ratings, grounding, and protection devices must
be determined from the actual hardware datasheets.

Do not connect an unknown pump, valve, relay, converter, or power supply
based only on nominal voltage.

Never connect mains AC directly to the ESP32, Raspberry Pi, sensor
circuit, or breadboard.

For mains-powered equipment, use an appropriately rated enclosed
power supply, switching device, protection, and qualified electrical
installation.

---

# 3. Power Architecture Principles

The platform should follow these principles:

1. Logic electronics use regulated low-voltage power.
2. Actuators should have a dedicated power path where practical.
3. High-current loads should not be powered through the ESP32.
4. Raspberry Pi power should not be taken from an inadequate ESP32 or
   sensor supply.
5. Pumps and valves should not draw their operating current through
   breadboard traces.
6. Inductive loads require appropriate flyback/transient protection.
7. Grounds must be designed deliberately.
8. DC/DC converters must be sized for continuous and transient loads.
9. Each power rail must have an appropriate protection strategy.
10. The system must fail into a safe actuator state.

---

# 4. High-Level Power Architecture

The conceptual architecture is:

```text
                    MAIN DC POWER INPUT
                            │
                ┌───────────┼────────────┐
                │           │            │
                ▼           ▼            ▼
          Logic Converter  Logic       Actuator
                │          Converter      Supply
                │           │             │
                ▼           ▼             ▼
          Raspberry Pi     ESP32       Pump / Valve
                │           │             │
                │           │          Relay / MOSFET
                │           │             │
                │           ├── Sensors  │
                │           ├── TFT      │
                │           └── Buzzer   │
                │
                └── Camera / USB Devices
```

The exact voltage rails depend on the selected hardware.

---

# 5. Recommended Power Domains

The system should conceptually separate power into:

```text
DOMAIN A — Raspberry Pi

DOMAIN B — ESP32 + Low-Power Sensors

DOMAIN C — Actuators

DOMAIN D — Cameras / High-Power Peripherals
```

These domains may share a common primary DC source if appropriate, but
their regulation and protection should be designed separately.

---

# 6. Raspberry Pi 5 Power Domain

The Raspberry Pi 5 requires a stable regulated supply appropriate to the
specific board and connected peripherals.

The Raspberry Pi should receive power from:

```text
Main DC Supply
      ↓
Appropriate DC/DC Converter
      ↓
Raspberry Pi 5
```

The converter must be sized for:

- Raspberry Pi 5 baseline consumption
- USB peripherals
- Camera devices
- Storage
- Networking
- Future edge compute
- Startup/transient requirements

Do not assume that a converter rated only for the Raspberry Pi board
will also support all connected USB devices.

---

# 7. Raspberry Pi Power Rule

The Raspberry Pi should have a dedicated regulated power path.

Do not power the Raspberry Pi through:

```text
ESP32
```

or:

```text
Breadboard 5V rail
```

unless the complete power architecture has been explicitly designed
and electrically validated for the required current.

---

# 8. ESP32 Power Domain

The ESP32 should receive a stable regulated supply appropriate to the
specific development board being used.

Typical architecture:

```text
Main DC Supply
      ↓
DC/DC Converter
      ↓
ESP32 Power Input
```

The exact input voltage must follow the ESP32 board manufacturer's
specification.

Do not assume that every ESP32 board accepts the same voltage on every
pin.

---

# 9. ESP32 Current Requirements

ESP32 current consumption is not constant.

Wireless transmission can create current peaks.

Therefore, the power supply must account for:

```text
Average consumption
+
Wi-Fi/Bluetooth peaks
+
Peripheral consumption
+
Startup/transient behavior
```

An inadequate power supply can produce:

```text
Brownouts
Random resets
Wi-Fi instability
Sensor failures
Unexpected actuator behavior
```

---

# 10. Sensor Power Domain

Low-power sensors should normally be powered from an appropriate
regulated logic rail.

Example:

```text
ESP32 Logic Supply
       │
       ├── DHT11
       ├── pH Interface
       ├── TDS Interface
       ├── Flow Sensor
       └── Other Low-Power Sensors
```

The actual sensor voltage must always be verified against the
manufacturer's datasheet.

Do not assume that a sensor module marked with a particular voltage is
safe to connect directly to an ESP32 GPIO.

---

# 11. Sensor Voltage Compatibility

The ESP32 uses 3.3V logic.

Every sensor interface must be checked for:

```text
Supply voltage
Logic voltage
Output voltage
Maximum GPIO voltage
Current requirements
Analog output range
```

If a sensor outputs a voltage above the ESP32 ADC/GPIO safe range,
appropriate conditioning or level shifting is required.

---

# 12. DHT11 Power

The DHT11 is a low-power sensor and is suitable for the initial MVP.

Conceptually:

```text
ESP32
 │
 ├── Sensor Power
 ├── Data GPIO
 └── GND
       │
       ▼
     DHT11
```

The exact wiring must follow the specific DHT11 module/sensor
configuration being used.

Some DHT11 breakout modules already include supporting components.

---

# 13. TFT Display Power

The TFT display must be treated according to its specific controller
and breakout-board specifications.

Conceptually:

```text
ESP32
 │
 ├── SPI
 ├── Control GPIO
 └── Display Power
          │
          ▼
        TFT
```

Verify:

- Logic voltage
- Backlight voltage
- Display current
- SPI logic compatibility

The TFT backlight can consume substantially more current than the
display logic.

---

# 14. Buzzer Power

The buzzer should not be driven directly from an ESP32 GPIO if its
current requirement exceeds the GPIO capability.

Preferred architecture:

```text
ESP32 GPIO
     ↓
Transistor / MOSFET Driver
     ↓
Buzzer Power
     ↓
Buzzer
```

If the buzzer is inductive or otherwise requires transient protection,
provide the appropriate protection circuit.

---

# 15. Actuator Power Domain

Pumps and valves should generally have a separate actuator power path.

Conceptually:

```text
Main Power
    │
    ▼
Actuator Supply
    │
    ├── Pump
    │
    └── Valve
```

The ESP32 controls the actuator through a suitable switching device.

Example:

```text
ESP32
  │
  ▼
Relay / MOSFET Driver
  │
  ▼
Pump / Valve
```

The ESP32 does not provide the actuator's operating power.

---

# 16. Pump Power

A pump may require substantially more current than the ESP32 or
Raspberry Pi.

The pump should therefore use an appropriately rated dedicated supply.

Conceptually:

```text
Actuator Power Supply
        │
        ▼
   Protection
        │
        ▼
 Relay / MOSFET
        │
        ▼
       Pump
```

The pump's startup current must be considered when sizing the power
supply and switching device.

---

# 17. Pump Startup Current

Pump motors can draw substantially more current during startup than
during steady-state operation.

Power calculations must therefore consider:

```text
Startup current
+
Continuous current
+
Other actuator loads
```

Do not size the supply based only on the pump's nominal running current.

---

# 18. Solenoid Valve Power

Solenoid valves are also inductive loads.

Architecture:

```text
Actuator Supply
      │
      ▼
 Switching Device
      │
      ▼
 Solenoid Valve
```

The valve's:

- Voltage
- Current
- Coil resistance
- Duty cycle
- Startup behavior

must be verified from the manufacturer's specification.

---

# 19. Inductive Load Protection

Pumps, solenoids, relays, and other inductive loads can generate
voltage transients when switched off.

Appropriate protection may include:

```text
Flyback diode
TVS diode
RC snubber
Other manufacturer-recommended suppression
```

The correct protection depends on:

- DC vs AC load
- Switching device
- Load voltage
- Load current
- Switching frequency

Do not blindly place a flyback diode across an AC load.

---

# 20. Relay Architecture

A relay module should be treated as a switching interface, not as a
power supply.

Conceptually:

```text
ESP32
  │
  ▼
Relay Driver
  │
  ▼
Relay Contacts
  │
  ▼
Actuator Supply
  │
  ▼
Pump / Valve
```

The relay contact rating must exceed the actual load requirements,
including startup conditions where applicable.

---

# 21. MOSFET Architecture

For suitable DC loads, a MOSFET-based switching stage may be preferable
to a mechanical relay.

Conceptually:

```text
ESP32 GPIO
    │
    ▼
Gate Driver / MOSFET
    │
    ▼
DC Load
```

Benefits may include:

- Fast switching
- No mechanical wear
- Lower switching noise
- PWM capability where appropriate

The MOSFET must be selected for the actual voltage, current, gate
drive, thermal conditions, and load type.

---

# 22. Logic Ground

Logic components generally require a common reference where their
signals are electrically connected.

Example:

```text
ESP32 GND
   │
   ├── Sensor GND
   ├── Display GND
   └── Driver signal reference
```

The exact grounding architecture must account for actuator noise and
current paths.

---

# 23. Grounding Strategy

High-current actuator return currents should not be routed through
sensitive sensor wiring.

Avoid architectures where:

```text
Pump current
     ↓
shared thin logic ground path
     ↓
ESP32
```

Instead, design the power distribution so high-current returns and
sensitive logic references are appropriately routed.

A star/structured grounding approach may be appropriate depending on
the physical implementation.

---

# 24. Common Ground vs Isolation

Not every subsystem should automatically share ground.

Whether grounds should be common depends on the interface:

```text
Direct GPIO
UART
I2C
SPI
Analog signal
Relay module
Optocoupler
Isolated converter
```

If galvanic isolation is used, do not accidentally defeat it by
connecting isolated grounds elsewhere.

---

# 25. Analog Sensor Noise

pH and TDS/EC measurements can be sensitive to electrical noise.

The following can introduce measurement errors:

- Pump motors
- Switching converters
- PWM
- Relay switching
- Long wires
- Poor grounding
- Shared noisy power rails

Therefore, analog sensor interfaces should be physically and
electrically separated from noisy actuator paths where practical.

---

# 26. pH Sensor Power Considerations

pH interfaces can be sensitive analog circuits.

The design should consider:

```text
Stable supply
Low electrical noise
Proper grounding
Analog signal conditioning
Cable shielding where appropriate
Physical separation from motors
```

The exact pH interface board determines the required electrical
architecture.

Do not connect a raw pH probe directly to an ESP32 GPIO.

Use an appropriate pH interface circuit.

---

# 27. TDS / EC Sensor Power Considerations

TDS/EC measurements can also be affected by:

- Electrical noise
- Ground loops
- Pump switching
- Poor power regulation
- Incorrect excitation circuitry

The specific sensor interface should determine the correct power and
signal-conditioning architecture.

---

# 28. Flow Sensor Power

Flow sensors often contain a Hall-effect sensor and may have their own
supply requirements.

Conceptually:

```text
Sensor Supply
      │
      ▼
Flow Sensor
      │
      ▼
Pulse Output
      │
      ▼
ESP32 GPIO
```

Verify that the output signal is safe for the ESP32 GPIO.

If the sensor output voltage is higher than the ESP32's allowed input
voltage, use appropriate level shifting.

---

# 29. Water-Level Sensor Power

Water-level sensors should be selected based on the required sensing
method.

Possible technologies include:

- Float switch
- Capacitive sensor
- Optical sensor
- Conductive sensor
- Ultrasonic sensor

The power architecture depends on the selected device.

Safety-critical water-level detection should be designed so that a
sensor failure results in a safe actuator state.

---

# 30. Camera Power

Cameras can create significant transient and continuous power demand.

Possible architecture:

```text
Raspberry Pi
     │
     └── Camera
```

or:

```text
Dedicated Camera Supply
     │
     └── Camera
```

The exact approach depends on the camera interface.

USB cameras can also contribute to Raspberry Pi USB power demand.

---

# 31. ESP32-CAM Power

If an ESP32-CAM is used as a separate device:

```text
ESP32-CAM
     │
     ├── Camera
     └── Wi-Fi
```

Its power requirements should be considered independently from the
primary ESP32 controller.

Do not assume that the primary ESP32's regulator can power an ESP32-CAM
plus its camera reliably.

---

# 32. Raspberry Pi + USB Power Budget

If the Raspberry Pi has:

```text
USB Camera
USB Storage
Wi-Fi peripherals
Other USB devices
```

the power budget must include all connected peripherals.

A Raspberry Pi that is stable without peripherals may become unstable
when additional USB loads are connected.

---

# 33. DC/DC Converter Selection

Every DC/DC converter should be selected based on:

```text
Input voltage range
Output voltage
Continuous current
Peak current
Efficiency
Thermal performance
Protection features
```

Protection features may include:

```text
Over-current protection
Over-voltage protection
Short-circuit protection
Thermal shutdown
Under-voltage protection
```

The converter's maximum current rating should not be treated as the
normal operating target.

---

# 34. Converter Headroom

Power supplies and converters should have reasonable design headroom.

Avoid:

```text
Load ≈ Converter maximum rating
```

Prefer a design where expected continuous and transient loads remain
comfortably within the converter's specified operating range.

The exact engineering margin should be determined from the actual
loads and environmental conditions.

---

# 35. Power Distribution

A structured power distribution system is preferred.

Conceptually:

```text
                    MAIN DC INPUT
                          │
                    Protection
                          │
                          ▼
                 POWER DISTRIBUTION
                    ┌─────┼─────┐
                    │     │     │
                    ▼     ▼     ▼
                  5V    Logic  Actuator
                   │     Rail    Rail
                   │       │       │
                   ▼       ▼       ▼
                  Pi     ESP32   Pump
                           │     Valve
                           │
                        Sensors
                        Display
                        Buzzer
```

The actual rail voltages must be determined by the selected hardware.

---

# 36. Fusing and Protection

Power domains should be appropriately protected.

Potential protection includes:

```text
Fuse
Resettable fuse
Circuit breaker
Reverse-polarity protection
TVS protection
Over-current protection
```

The exact protection devices and ratings must be selected from the
actual electrical design.

Never substitute a fuse with an arbitrarily higher-rated device.

---

# 37. Reverse Polarity Protection

Where the power input can potentially be connected incorrectly,
consider reverse-polarity protection.

Possible implementations include:

```text
Diode
P-channel MOSFET
Ideal-diode controller
```

The appropriate method depends on the power level and efficiency
requirements.

---

# 38. Power-On Sequence

The desired system boot sequence is:

```text
Main Power
    ↓
Power Rails Stable
    ↓
Raspberry Pi Boot
    ↓
ESP32 Boot
    ↓
ESP32 Safe Hardware State
    ↓
Sensor Initialization
    ↓
Local Wi-Fi
    ↓
MQTT
    ↓
Cloud Connectivity
    ↓
Normal Operation
```

The ESP32 must enter a safe actuator state before attempting network
connections.

---

# 39. ESP32 Boot State

At startup, the ESP32 should establish known safe outputs.

Example:

```text
Pump:
    OFF

Valve:
    SAFE/CLOSED

Buzzer:
    OFF

Relay:
    SAFE STATE
```

The exact state depends on the electrical switching design.

The firmware must account for active-low and active-high relay modules.

---

# 40. Power-Loss Behavior

When power is lost:

```text
Power Loss
    ↓
ESP32 shuts down
    ↓
Actuator control lost
    ↓
Hardware should default to safe state
```

The hardware switching design should avoid requiring software to remain
running in order to maintain a safe state.

For example, if a pump must normally be OFF, the switching circuit
should naturally default to OFF when the controller loses power.

---

# 41. Brownout Behavior

Brownouts can be dangerous because the MCU may behave unpredictably
during unstable supply conditions.

The ESP32 should use its brownout protection where appropriate.

The power architecture should minimize:

```text
Voltage sag
Current starvation
Noisy rails
Converter instability
```

If brownouts occur, investigate the power system before modifying
software to hide the symptom.

---

# 42. Motor Noise

Pumps and motors can introduce:

```text
Voltage transients
EMI
Ground noise
Current spikes
```

Mitigation may include:

```text
Separate actuator supply
Flyback/transient suppression
Physical separation
Appropriate wiring
Filtering
Proper grounding
```

Do not assume that software debouncing or sensor averaging alone will
solve electrical noise.

---

# 43. Relay Noise

Mechanical relay switching can introduce electrical noise.

Potential mitigation:

```text
Appropriate driver circuitry
Suppression components
Physical separation
Proper grounding
Power rail filtering
```

The relay module's own input requirements must be verified.

---

# 44. Breadboard Usage

Breadboards are appropriate for:

```text
MVP
Low-current sensor testing
ESP32 development
Prototype logic
```

They should generally not be used as the final power distribution
system for:

```text
High-current pumps
High-current valves
Large motors
High-current power rails
```

Actuator power wiring should use appropriately rated wiring,
connectors, terminals, and distribution hardware.

---

# 45. Wire Sizing

Wire gauge must be selected based on:

```text
Current
Wire length
Voltage
Allowed voltage drop
Temperature
Installation method
```

Do not choose wire size solely by physical convenience.

Long actuator runs can create significant voltage drop.

---

# 46. Connector Selection

Connectors must be rated for:

```text
Voltage
Current
Environment
Temperature
Mechanical stress
```

Hydroponics systems involve water and humidity, so connectors should be
selected and protected accordingly.

---

# 47. Water and Electrical Separation

Electrical equipment must be physically separated from water wherever
possible.

Important measures include:

```text
Enclosures
Cable management
Drip loops
Water-resistant connectors
Appropriate mounting
Physical separation
```

Do not place exposed electrical connections where water can easily reach
them.

---

# 48. Enclosures

The production system should use suitable enclosures for:

- Raspberry Pi
- Power converters
- Relay/driver circuits
- Terminal blocks
- Power distribution
- High-voltage equipment where applicable

The enclosure must provide appropriate ventilation and environmental
protection.

---

# 49. Thermal Management

Power converters, Raspberry Pi, MOSFETs, and other components generate
heat.

Thermal design should consider:

```text
Ambient temperature
Continuous load
Converter efficiency
Enclosure airflow
Heat dissipation
```

Do not place a high-power converter in a sealed enclosure without
considering its thermal characteristics.

---

# 50. Power Monitoring

Future versions may include electrical monitoring.

Possible sensors:

```text
Current sensor
Voltage sensor
Power monitor
Energy meter
```

Potential architecture:

```text
Power Monitor
      ↓
ESP32
      ↓
Telemetry
      ↓
Backend
      ↓
Dashboard
```

This could allow the platform to detect:

- Pump current anomalies
- Unexpected load
- Power consumption
- Actuator faults

---

# 51. Pump Fault Detection

A future closed-loop architecture may be:

```text
Pump Command
     ↓
ESP32
     ↓
Pump
     ↓
Flow Sensor
     ↓
ESP32
     ↓
Expected Flow?
     │
   ┌─┴─┐
  YES  NO
   │    │
   │    ▼
   │  Fault
   │    ↓
   │  Pump OFF
   │    ↓
   │  Alert
   │
   ▼
Normal Operation
```

This is more reliable than assuming that:

```text
Relay ON = Pump ON
```

---

# 52. Power Domain Summary

The intended conceptual domains are:

```text
┌──────────────────────────────┐
│ LOGIC DOMAIN                 │
│                              │
│ ESP32                        │
│ DHT11                        │
│ pH interface                │
│ TDS interface               │
│ Flow sensor                 │
│ TFT                          │
│ Buzzer driver               │
└──────────────────────────────┘


┌──────────────────────────────┐
│ EDGE DOMAIN                  │
│                              │
│ Raspberry Pi 5               │
│ Camera                       │
│ USB devices                  │
│ Edge compute                 │
└──────────────────────────────┘


┌──────────────────────────────┐
│ ACTUATOR DOMAIN              │
│                              │
│ Pump                         │
│ Solenoid valve               │
│ Relay / MOSFET               │
│ Future actuators             │
└──────────────────────────────┘
```

The domains may originate from the same main power source, but they
should not be treated as one undifferentiated electrical circuit.

---

# 53. Power Failure Isolation

A failure in one power domain should have minimal impact on unrelated
domains.

Example:

```text
Pump failure
    ↓
Should not destroy
    ↓
ESP32
```

Similarly:

```text
Camera power problem
    ↓
Should not disable
    ↓
DHT11 telemetry
```

Proper protection and power distribution are therefore architectural
requirements.

---

# 54. MVP Power Architecture

For the initial DHT11 MVP:

```text
                 MAIN DC SUPPLY
                        │
              ┌─────────┴─────────┐
              │                   │
              ▼                   ▼
       Raspberry Pi Supply    ESP32 Supply
              │                   │
              ▼                   ▼
        Raspberry Pi 5          ESP32
                                  │
                           ┌──────┼──────┐
                           │      │      │
                           ▼      ▼      ▼
                         DHT11   TFT   Buzzer
```

The exact voltage and current ratings must be based on the actual
boards/modules being used.

At this stage, avoid introducing pumps and valves until the low-voltage
logic system is stable.

---

# 55. MVP Expansion

After the telemetry pipeline works:

```text
ESP32
  │
  ├── DHT11
  ├── pH
  ├── TDS
  ├── Flow
  └── Water Level
```

Then introduce:

```text
ESP32
  │
  ├── Relay / MOSFET
  │      │
  │      ├── Pump
  │      └── Valve
```

The actuator supply should be designed separately from the sensor
prototype.

---

# 56. Recommended Development Sequence

## Phase 1 — Logic Only

Build:

```text
ESP32
DHT11
Breadboard
USB power
```

Verify:

```text
Temperature
Humidity
Stable ESP32 operation
```

---

## Phase 2 — Network

Add:

```text
Wi-Fi
Raspberry Pi
MQTT
```

Verify:

```text
ESP32
    ↓
Raspberry Pi
    ↓
MQTT
```

---

## Phase 3 — Cloud

Add:

```text
Backend
PostgreSQL
Frontend
```

Verify:

```text
Sensor
    ↓
Dashboard
```

---

## Phase 4 — Actuator

Add:

```text
Relay/MOSFET
Pump
```

only after the logic and power architecture have been validated.

---

## Phase 5 — Additional Sensors

Add:

```text
pH
TDS
Flow
Water Level
```

one subsystem at a time.

---

## Phase 6 — Camera

Add:

```text
Camera
    ↓
Raspberry Pi
```

---

## Phase 7 — Computer Vision

Add:

```text
Camera
    ↓
CV
    ↓
AI
```

---

# 57. Power Validation Checklist

Before connecting a component, verify:

```text
[ ] Required supply voltage known
[ ] Maximum current known
[ ] Startup current known
[ ] Logic voltage known
[ ] GPIO voltage compatibility checked
[ ] Connector rating checked
[ ] Wire rating checked
[ ] Converter rating checked
[ ] Protection requirements checked
[ ] Grounding requirements checked
[ ] Inductive-load protection checked
[ ] Safe failure state defined
```

---

# 58. Pre-Power Checklist

Before applying power:

```text
[ ] Correct polarity
[ ] No short circuits
[ ] Correct voltage selected
[ ] Power supply current rating adequate
[ ] Converter configured correctly
[ ] ESP32 GPIOs not exposed to excessive voltage
[ ] Sensor wiring verified
[ ] Actuator supply isolated from logic during initial testing
[ ] Pump/valve disconnected during firmware bring-up
[ ] Relay/MOSFET wiring verified
[ ] Emergency shutdown method available
```

---

# 59. Testing Checklist

Test power architecture in stages.

## Test 1

```text
ESP32 only
```

Verify:

```text
Stable boot
No brownouts
```

## Test 2

```text
ESP32 + DHT11
```

Verify:

```text
Stable readings
```

## Test 3

```text
ESP32 + sensors + TFT
```

Verify:

```text
Stable operation
```

## Test 4

```text
ESP32 + Raspberry Pi
```

Verify:

```text
No unexpected resets
```

## Test 5

```text
Actuator driver without load
```

Verify:

```text
Correct switching
Safe default state
```

## Test 6

```text
Actuator with actual supply/load
```

Verify:

```text
No ESP32 reset
No excessive voltage drop
No abnormal heating
```

---

# 60. Fault Scenarios

The system should be evaluated against:

```text
Power supply failure
DC/DC converter failure
Short circuit
Over-current
Brownout
Pump startup surge
Valve switching
Relay switching
Sensor noise
Ground noise
Cable disconnect
Water exposure
Overheating
```

---

# 61. Documentation Requirements

Any new hardware component added to the system must update the relevant
documentation.

At minimum:

```text
docs/hardware/HARDWARE.md
docs/hardware/PINOUT.md
docs/hardware/WIRING.md
docs/hardware/POWER.md
```

If the component changes telemetry:

```text
docs/protocols/TELEMETRY.md
```

If the component introduces a controllable actuator:

```text
docs/protocols/COMMANDS.md
```

---

# 62. Power Architecture Invariants

The following rules must remain true unless explicitly changed by an
architecture decision.

### Invariant 1

The ESP32 does not directly power high-current actuators.

### Invariant 2

The Raspberry Pi has an appropriately rated regulated power source.

### Invariant 3

Actuators have an appropriately rated power path.

### Invariant 4

High-current actuator wiring does not rely on breadboard traces.

### Invariant 5

Inductive loads have appropriate transient protection.

### Invariant 6

ESP32 GPIO voltage limits are respected.

### Invariant 7

Sensor power requirements are verified individually.

### Invariant 8

The system has defined safe actuator states.

### Invariant 9

Power failures must not intentionally create unsafe actuator states.

### Invariant 10

Water and electrical systems are physically separated and protected.

### Invariant 11

Power converters are sized for both continuous and transient loads.

### Invariant 12

The actual hardware datasheet is authoritative over this document.

---

# 63. Final Power Architecture

The intended system-level power structure is:

```text
                         MAIN POWER
                             │
                     INPUT PROTECTION
                             │
                             ▼
                    POWER DISTRIBUTION
                             │
             ┌───────────────┼────────────────┐
             │               │                │
             ▼               ▼                ▼
       LOGIC POWER       EDGE POWER      ACTUATOR POWER
             │               │                │
             ▼               ▼                ▼
          ESP32        Raspberry Pi 5      Pump / Valve
             │               │                │
       ┌─────┼─────┐         │             Driver
       │     │     │         │                │
       ▼     ▼     ▼         ▼                ▼
    Sensors  TFT  Buzzer   Camera          Actuators
```

The electrical architecture should preserve a clear distinction
between:

```text
LOW-POWER LOGIC

EDGE COMPUTE

HIGH-CURRENT ACTUATORS
```

The ESP32 controls physical loads through properly rated switching
hardware.

The Raspberry Pi and ESP32 receive stable regulated supplies.

Sensitive sensors should be protected from actuator-generated
electrical noise.

All power, grounding, protection, and wiring decisions must ultimately
be validated against the exact hardware components selected for the
final system.
```