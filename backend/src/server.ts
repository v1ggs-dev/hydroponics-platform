import express from "express";
import http from "http";
import cors from "cors";
import { config } from "./config";
import { connectDatabase } from "./db/prisma";
import { wsService } from "./services/websocket.service";
import { mqttService } from "./services/mqtt.service";
import { apiRouter } from "./routes/api";

async function bootstrap() {
  const app = express();

  // Middleware
  app.use(cors({ origin: "*" }));
  app.use(express.json());

  // Mount API Router under /api/v1 and /api
  app.use("/api/v1", apiRouter);
  app.use("/api", apiRouter);

  // Root welcome
  app.get("/", (req, res) => {
    res.json({
      service: "Hydroponics Platform Cloud API",
      version: "v1",
      docs: "/api/v1/health",
      websocket: `ws://${req.headers.host}/ws`,
    });
  });

  const server = http.createServer(app);

  // 1. Initialize Realtime WebSocket Service
  wsService.init(server);

  // 2. Connect to Supabase PostgreSQL Database (Non-blocking if not configured yet)
  try {
    if (config.databaseUrl) {
      await connectDatabase();
    } else {
      console.warn("⚠️ [Database] DATABASE_URL not set yet in backend/.env. Waiting for Supabase credentials...");
    }
  } catch (err: any) {
    console.warn("⚠️ [Database] Could not connect to Supabase yet. Configure .env to establish link.");
  }

  // 3. Initialize MQTT Ingestion Service
  mqttService.init();

  // 4. Start HTTP Server
  server.listen(config.port, () => {
    console.log("\n" + "=".repeat(65));
    console.log(`  🚀 HYDROPONICS BACKEND RUNNING ON http://localhost:${config.port}`);
    console.log("=".repeat(65));
    console.log(`  REST API Base:    http://localhost:${config.port}/api/v1`);
    console.log(`  WebSocket Stream: ws://localhost:${config.port}/ws`);
    console.log(`  MQTT Broker:      ${config.mqtt.brokerUrl}`);
    console.log("=".repeat(65) + "\n");
  });
}

bootstrap().catch((err) => {
  console.error("Fatal Error during bootstrap:", err);
  process.exit(1);
});
