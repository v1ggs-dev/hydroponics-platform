import { Request, Response } from "express";
import { prisma, isDatabaseConnected } from "../db/prisma";

const fallbackDevices = [
  {
    id: "esp32-env",
    name: "Hydroponics Node 1 (Environment & Actuation)",
    type: "controller",
    status: "ONLINE",
    lastSeenAt: new Date().toISOString(),
  },
  {
    id: "esp32-chem",
    name: "Hydroponics Node 2 (Water Chemistry & Root Zone)",
    type: "controller",
    status: "ONLINE",
    lastSeenAt: new Date().toISOString(),
  },
];

export async function getDevices(req: Request, res: Response) {
  if (isDatabaseConnected) {
    try {
      const devices = await prisma.device.findMany({
        orderBy: { lastSeenAt: "desc" },
      });
      if (devices.length > 0) {
        return res.json({ success: true, data: devices });
      }
    } catch {
      // Fallback
    }
  }
  return res.json({ success: true, data: fallbackDevices });
}

export async function getDeviceById(req: Request, res: Response) {
  const { id } = req.params;
  if (isDatabaseConnected) {
    try {
      const device = await prisma.device.findUnique({
        where: { id },
        include: {
          alerts: { where: { resolved: false }, take: 5 },
        },
      });

      if (device) {
        return res.json({ success: true, data: device });
      }
    } catch {
      // Fallback
    }
  }

  const found = fallbackDevices.find((d) => d.id === id);
  if (found) {
    return res.json({ success: true, data: { ...found, alerts: [] } });
  }
  return res.status(404).json({ success: false, error: "Device not found" });
}
