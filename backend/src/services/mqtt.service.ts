import mqtt, { MqttClient } from "mqtt";
import { config } from "../config";
import { prisma, isDatabaseConnected } from "../db/prisma";
import { wsService } from "./websocket.service";

// In-Memory Real-Time Cache & Ring Buffer for offline/disconnected resilience
export const inMemoryLatestTelemetry: Record<string, any> = {
  air_temperature: { value: 24.5, unit: "°C", quality: "GOOD", timestamp: new Date().toISOString() },
  humidity: { value: 62.0, unit: "%", quality: "GOOD", timestamp: new Date().toISOString() },
  tds: { value: 850.0, unit: "ppm", quality: "GOOD", timestamp: new Date().toISOString() },
  ph: { value: 6.20, unit: "pH", quality: "GOOD", timestamp: new Date().toISOString() },
  substrate_moisture: { value: 65.0, unit: "%", quality: "GOOD", timestamp: new Date().toISOString() },
  flow_rate: { value: 0.0, unit: "L/min", quality: "GOOD", timestamp: new Date().toISOString() },
  water_volume: { value: 12.5, unit: "L", quality: "GOOD", timestamp: new Date().toISOString() },
};

export const inMemoryHistoryBuffer: Array<{
  id: string | number;
  deviceId: string;
  sensorId: string;
  metric: string;
  value: number;
  unit: string;
  quality: string;
  timestamp: string;
}> = [];

export class MQTTService {
  private static instance: MQTTService;
  private client: MqttClient | null = null;

  private constructor() {}

  public static getInstance(): MQTTService {
    if (!MQTTService.instance) {
      MQTTService.instance = new MQTTService();
    }
    return MQTTService.instance;
  }

  public init() {
    console.log(`📡 [MQTT Service] Connecting to broker at ${config.mqtt.brokerUrl}...`);
    this.client = mqtt.connect(config.mqtt.brokerUrl, {
      clientId: config.mqtt.clientId,
      clean: true,
      reconnectPeriod: 5000,
    });

    this.client.on("connect", () => {
      console.log("✅ [MQTT Service] Connected to MQTT broker!");
      this.client?.subscribe([
        "hydroponics/+/telemetry",
        "hydroponics/+/status",
        "hydroponics/+/events",
        "hydroponics/edge/health"
      ], (err) => {
        if (err) {
          console.error("❌ [MQTT Service] Subscription error:", err);
        } else {
          console.log("📥 [MQTT Service] Subscribed to telemetry, status & events topics.");
        }
      });
    });

    this.client.on("message", async (topic: string, payload: Buffer) => {
      try {
        const rawStr = payload.toString();
        const data = JSON.parse(rawStr);
        await this.handleMessage(topic, data);
      } catch (err) {
        console.error(`❌ [MQTT Service] Error processing message on topic ${topic}:`, err);
      }
    });

    this.client.on("error", (err) => {
      console.error("❌ [MQTT Service] Connection error:", err.message);
    });

    this.client.on("offline", () => {
      console.warn("⚠️ [MQTT Service] Disconnected from broker. Retrying...");
    });
  }

  public publishCommand(deviceId: string, command: any): Promise<boolean> {
    return new Promise((resolve) => {
      if (!this.client || !this.client.connected) {
        console.error("❌ [MQTT Service] Cannot publish command: Broker not connected.");
        return resolve(false);
      }

      const topic = `hydroponics/${deviceId}/commands`;
      const payload = JSON.stringify(command);

      this.client.publish(topic, payload, { qos: 1 }, (err) => {
        if (err) {
          console.error(`❌ [MQTT Service] Failed to publish command to ${topic}:`, err);
          resolve(false);
        } else {
          console.log(`📤 [MQTT Service] Published command to ${topic}: ${payload}`);
          resolve(true);
        }
      });
    });
  }

  private async handleMessage(topic: string, data: any) {
    const parts = topic.split("/");
    const deviceId = data.deviceId || parts[1] || "esp32-01";

    // 1. Ingest Telemetry
    if (topic.endsWith("/telemetry")) {
      await this.ingestTelemetry(deviceId, data);
    }
    // 2. Device Status (LWT / Online Heartbeats)
    else if (topic.endsWith("/status")) {
      await this.handleStatusUpdate(deviceId, data);
    }
    // 3. Urgent Events & Alarms
    else if (topic.endsWith("/events")) {
      await this.handleEvent(deviceId, data);
    }
    // 4. Edge Gateway Health
    else if (topic === "hydroponics/edge/health") {
      wsService.broadcast("edge_health", data);
    }
  }

  private async ingestTelemetry(deviceId: string, data: any) {
    const measurements = data.measurements || [];
    if (!measurements.length) return;

    const timestamp = data.receivedAt ? new Date(data.receivedAt) : new Date();

    // 1. Update In-Memory Real-Time Cache
    measurements.forEach((m: any) => {
      if (m.metric) {
        inMemoryLatestTelemetry[m.metric] = {
          value: typeof m.value === "number" ? m.value : 0.0,
          unit: m.unit || "",
          quality: m.quality || "GOOD",
          sensorId: m.sensorId || "unknown",
          deviceId,
          timestamp: timestamp.toISOString(),
        };

        // Add to historical ring buffer (keep max 1000 items)
        inMemoryHistoryBuffer.push({
          id: `${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
          deviceId,
          sensorId: m.sensorId || "unknown",
          metric: m.metric,
          value: typeof m.value === "number" ? m.value : 0.0,
          unit: m.unit || "",
          quality: m.quality || "GOOD",
          timestamp: timestamp.toISOString(),
        });
      }
    });

    if (inMemoryHistoryBuffer.length > 1000) {
      inMemoryHistoryBuffer.splice(0, inMemoryHistoryBuffer.length - 1000);
    }

    // 2. Broadcast live update to all connected WebSockets immediately
    wsService.broadcast("telemetry", {
      deviceId,
      uptimeSeconds: data.uptimeSeconds,
      timestamp: timestamp.toISOString(),
      measurements,
    });

    // 3. Optional DB Persistence (only if Supabase is connected)
    if (isDatabaseConnected) {
      try {
        await prisma.device.upsert({
          where: { id: deviceId },
          update: {
            status: "ONLINE",
            lastSeenAt: new Date(),
          },
          create: {
            id: deviceId,
            name: `Hydroponics Unit (${deviceId})`,
            type: "controller",
            status: "ONLINE",
            lastSeenAt: new Date(),
          },
        });

        const records = measurements.map((m: any) => ({
          deviceId,
          sensorId: m.sensorId || "unknown",
          metric: m.metric,
          value: typeof m.value === "number" ? m.value : 0.0,
          unit: m.unit || "",
          quality: m.quality || "GOOD",
          timestamp,
        }));

        await prisma.measurement.createMany({
          data: records,
        });
      } catch (error) {
        // Silently handled in memory
      }
    }
  }

  private async handleStatusUpdate(deviceId: string, data: any) {
    const status = data.status || "ONLINE";
    wsService.broadcast("device_status", { deviceId, status, timestamp: new Date().toISOString() });

    if (isDatabaseConnected) {
      try {
        await prisma.device.upsert({
          where: { id: deviceId },
          update: {
            status,
            lastSeenAt: new Date(),
          },
          create: {
            id: deviceId,
            name: `Hydroponics Unit (${deviceId})`,
            status,
            lastSeenAt: new Date(),
          },
        });
      } catch (err) {
        // Silently handled
      }
    }
  }

  private async handleEvent(deviceId: string, data: any) {
    wsService.broadcast("alert", {
      deviceId,
      type: data.type || "EVENT",
      severity: data.severity || "INFO",
      message: data.message || "Hardware event received",
      timestamp: new Date().toISOString(),
    });

    if (isDatabaseConnected) {
      try {
        await prisma.alert.create({
          data: {
            deviceId,
            type: data.type || "HARDWARE_EVENT",
            severity: data.severity || "INFO",
            message: data.message || "Device event triggered",
          },
        });
      } catch (err) {
        // Silently handled
      }
    }
  }
}

export const mqttService = MQTTService.getInstance();
