import { Router } from "express";
import path from "path";
import fs from "fs";
import { getDevices, getDeviceById } from "../controllers/device.controller";
import { getLatestTelemetry, getTelemetryHistory } from "../controllers/telemetry.controller";
import { sendActuatorCommand, getCommands } from "../controllers/command.controller";
import { getAlerts, resolveAlert } from "../controllers/alert.controller";
import { prisma } from "../db/prisma";

export const apiRouter = Router();

// 1. Healthcheck
apiRouter.get("/health", async (req, res) => {
  try {
    await prisma.$queryRaw`SELECT 1`;
    return res.json({
      status: "HEALTHY",
      service: "hydroponics-backend",
      database: "CONNECTED (Supabase PostgreSQL)",
      uptimeSeconds: process.uptime(),
      timestamp: new Date().toISOString(),
    });
  } catch (err: any) {
    return res.status(503).json({
      status: "DEGRADED",
      database: "DISCONNECTED",
      error: err.message,
    });
  }
});

// 2. Devices
apiRouter.get("/devices", getDevices);
apiRouter.get("/devices/:id", getDeviceById);

// 3. Telemetry
apiRouter.get("/telemetry/latest", getLatestTelemetry);
apiRouter.get("/telemetry/history", getTelemetryHistory);

// 4. Commands
apiRouter.post("/commands", sendActuatorCommand);
apiRouter.get("/commands", getCommands);

// 5. Alerts
apiRouter.get("/alerts", getAlerts);
apiRouter.patch("/alerts/:id/resolve", resolveAlert);

// 6. Camera & AI Vision Feed
const SNAPSHOT_PATH = path.resolve(__dirname, "../../../edge/camera/snapshots/latest.jpg");

apiRouter.get("/camera/latest", (req, res) => {
  if (fs.existsSync(SNAPSHOT_PATH)) {
    res.setHeader("Content-Type", "image/jpeg");
    res.setHeader("Cache-Control", "no-cache, no-store, must-revalidate");
    return res.sendFile(SNAPSHOT_PATH);
  }
  return res.status(404).json({ success: false, message: "No snapshot available yet" });
});

// Real-Time MJPEG Video Stream
apiRouter.get("/camera/stream", (req, res) => {
  res.writeHead(200, {
    "Content-Type": "multipart/x-mixed-replace; boundary=frame",
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Connection": "keep-alive",
    "Pragma": "no-cache",
  });

  const sendFrame = () => {
    if (fs.existsSync(SNAPSHOT_PATH)) {
      try {
        const frame = fs.readFileSync(SNAPSHOT_PATH);
        res.write(`--frame\r\n`);
        res.write(`Content-Type: image/jpeg\r\n`);
        res.write(`Content-Length: ${frame.length}\r\n\r\n`);
        res.write(frame);
        res.write(`\r\n`);
      } catch (e) {
        // File may be briefly locked during atomic write
      }
    }
  };

  sendFrame();
  const interval = setInterval(sendFrame, 150); // ~7 FPS stream rate

  req.on("close", () => {
    clearInterval(interval);
  });
});

apiRouter.get("/camera/status", (req, res) => {
  const exists = fs.existsSync(SNAPSHOT_PATH);
  const stats = exists ? fs.statSync(SNAPSHOT_PATH) : null;
  return res.json({
    success: true,
    available: exists,
    lastCaptureAt: stats ? stats.mtime.toISOString() : null,
    fileSizeBytes: stats ? stats.size : 0,
  });
});
