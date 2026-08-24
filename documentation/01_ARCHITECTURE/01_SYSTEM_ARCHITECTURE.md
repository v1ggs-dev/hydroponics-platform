# Hydroponics Platform — System Architecture

## 1. Overview

The Hydroponics Platform is a modular IoT-based monitoring, control,
automation, and computer-vision system.

The system is designed around four primary layers:

1. Hardware Controller — ESP32
2. Edge Gateway — Raspberry Pi 5
3. Cloud Platform — Backend + Database + Messaging
4. User Interface — Web Dashboard

The architecture is intentionally modular so that sensors, actuators,
communication methods, AI/CV components, and cloud infrastructure can
be replaced or extended without requiring a complete system redesign.

---

# 2. High-Level Architecture

The conceptual system is:

                    ┌─────────────────────────────┐
                    │       USER BROWSER          │
                    │                             │
                    │       Web Dashboard         │
                    └─────────────┬───────────────┘
                                  │
                           HTTPS / WebSocket
                                  │
                                  ▼
                    ┌─────────────────────────────┐
                    │        CLOUD SERVER         │
                    │                             │
                    │  Frontend                   │
                    │  Backend API                │
                    │  MQTT / Messaging           │
                    │  PostgreSQL                 │
                    │  Authentication             │
                    └─────────────┬───────────────┘
                                  │
                              Internet
                                  │
                                  ▼
                    ┌─────────────────────────────┐
                    │       RASPBERRY PI 5        │
                    │                             │
                    │  Edge Gateway               │
                    │  Local Network              │
                    │  MQTT Client/Broker         │
                    │  Camera                     │
                    │  Computer Vision             │
                    │  Local Automation            │
                    │  Local Buffer                │
                    └─────────────┬───────────────┘
                                  │
                             Private Wi-Fi
                                  │
                                  ▼
                    ┌─────────────────────────────┐
                    │           ESP32             │
                    │                             │
                    │  Sensor Acquisition         │
                    │  Actuator Control           │
                    │  Hardware Safety            │
                    │  TFT Display                │
                    │  Buzzer                     │
                    └─────────────┬───────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
                SENSORS                     ACTUATORS
                    │                           │
              ┌─────┼─────┐              ┌──────┼──────┐
              │     │     │              │      │      │
             pH    EC    DHT11          Pump   Valve  Relay