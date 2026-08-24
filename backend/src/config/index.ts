import dotenv from "dotenv";
import path from "path";

dotenv.config({ path: path.resolve(__dirname, "../../.env") });

export const config = {
  port: parseInt(process.env.PORT || "4000", 10),
  nodeEnv: process.env.NODE_ENV || "development",
  databaseUrl: process.env.DATABASE_URL || "",
  directUrl: process.env.DIRECT_URL || "",
  supabase: {
    url: process.env.SUPABASE_URL || "",
    anonKey: process.env.SUPABASE_ANON_KEY || "",
    serviceRoleKey: process.env.SUPABASE_SERVICE_ROLE_KEY || "",
  },
  mqtt: {
    brokerUrl: process.env.MQTT_BROKER_URL || "mqtt://localhost:1883",
    clientId: process.env.MQTT_CLIENT_ID || "hydro-backend-service",
    topicTelemetry: "hydroponics/+/telemetry",
    topicStatus: "hydroponics/+/status",
    topicCommands: "hydroponics/{deviceId}/commands",
    topicEvents: "hydroponics/+/events",
  },
};
