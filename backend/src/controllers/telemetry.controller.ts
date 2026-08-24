import { Request, Response } from "express";
import { prisma, isDatabaseConnected } from "../db/prisma";
import { inMemoryLatestTelemetry, inMemoryHistoryBuffer } from "../services/mqtt.service";

export async function getLatestTelemetry(req: Request, res: Response) {
  try {
    const deviceId = req.query.deviceId as string | undefined;

    const metrics = [
      "air_temperature",
      "humidity",
      "tds",
      "ph",
      "substrate_moisture",
      "flow_rate",
      "water_volume",
    ];

    const latestReadings: Record<string, any> = { ...inMemoryLatestTelemetry };

    if (isDatabaseConnected) {
      try {
        await Promise.all(
          metrics.map(async (metric) => {
            const whereClause: any = { metric };
            if (deviceId && deviceId !== "all") {
              whereClause.deviceId = deviceId;
            }

            const reading = await prisma.measurement.findFirst({
              where: whereClause,
              orderBy: { timestamp: "desc" },
            });

            if (reading) {
              latestReadings[metric] = {
                value: reading.value,
                unit: reading.unit,
                quality: reading.quality,
                sensorId: reading.sensorId,
                deviceId: reading.deviceId,
                timestamp: reading.timestamp,
              };
            }
          })
        );
      } catch {
        // Fallback gracefully to in-memory readings
      }
    }

    return res.json({
      success: true,
      deviceId: deviceId || "all",
      data: latestReadings,
      timestamp: new Date().toISOString(),
    });
  } catch (error: any) {
    return res.json({
      success: true,
      deviceId: "all",
      data: inMemoryLatestTelemetry,
      timestamp: new Date().toISOString(),
    });
  }
}

export async function getTelemetryHistory(req: Request, res: Response) {
  try {
    const deviceId = req.query.deviceId as string | undefined;
    const metric = req.query.metric as string | undefined;
    const range = (req.query.range as string) || "24h";
    const limit = parseInt((req.query.limit as string) || "500", 10);

    // If connected to Supabase, query PostgreSQL
    if (isDatabaseConnected) {
      try {
        const now = new Date();
        let startTime = new Date(now.getTime() - 24 * 60 * 60 * 1000); // default 24h

        if (range === "1h") startTime = new Date(now.getTime() - 1 * 60 * 60 * 1000);
        else if (range === "6h") startTime = new Date(now.getTime() - 6 * 60 * 60 * 1000);
        else if (range === "24h") startTime = new Date(now.getTime() - 24 * 60 * 60 * 1000);
        else if (range === "7d") startTime = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        else if (range === "30d") startTime = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);

        const whereClause: any = { timestamp: { gte: startTime } };
        if (deviceId && deviceId !== "all") whereClause.deviceId = deviceId;
        if (metric) whereClause.metric = metric;

        const measurements = await prisma.measurement.findMany({
          where: whereClause,
          orderBy: { timestamp: "asc" },
          take: limit,
          select: {
            id: true,
            deviceId: true,
            sensorId: true,
            metric: true,
            value: true,
            unit: true,
            quality: true,
            timestamp: true,
          },
        });

        if (measurements.length > 0) {
          return res.json({
            success: true,
            deviceId: deviceId || "all",
            range,
            count: measurements.length,
            data: measurements,
          });
        }
      } catch {
        // Fallback to in-memory buffer
      }
    }

    // Serve from In-Memory Buffer
    let filtered = [...inMemoryHistoryBuffer];
    if (deviceId && deviceId !== "all") {
      filtered = filtered.filter((r) => r.deviceId === deviceId);
    }
    if (metric) {
      filtered = filtered.filter((r) => r.metric === metric);
    }

    return res.json({
      success: true,
      deviceId: deviceId || "all",
      range,
      count: filtered.length,
      data: filtered.slice(-limit),
    });
  } catch (error: any) {
    return res.json({
      success: true,
      deviceId: "all",
      range: "24h",
      count: inMemoryHistoryBuffer.length,
      data: inMemoryHistoryBuffer,
    });
  }
}
