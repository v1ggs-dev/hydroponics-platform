import { Request, Response } from "express";
import { prisma } from "../db/prisma";

export async function getAlerts(req: Request, res: Response) {
  try {
    const deviceId = req.query.deviceId as string | undefined;
    const resolved = req.query.resolved !== undefined ? req.query.resolved === "true" : undefined;

    const whereClause: any = {};
    if (deviceId) whereClause.deviceId = deviceId;
    if (resolved !== undefined) whereClause.resolved = resolved;

    const alerts = await prisma.alert.findMany({
      where: whereClause,
      orderBy: { createdAt: "desc" },
      take: 100,
    });

    return res.json({ success: true, count: alerts.length, data: alerts });
  } catch (error: any) {
    return res.status(500).json({ success: false, error: error.message });
  }
}

export async function resolveAlert(req: Request, res: Response) {
  try {
    const id = parseInt(req.params.id, 10);
    const alert = await prisma.alert.update({
      where: { id },
      data: {
        resolved: true,
        resolvedAt: new Date(),
      },
    });

    return res.json({ success: true, message: "Alert resolved", data: alert });
  } catch (error: any) {
    return res.status(500).json({ success: false, error: error.message });
  }
}
