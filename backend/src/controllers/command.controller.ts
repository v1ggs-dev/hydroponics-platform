import { Request, Response } from "express";
import { prisma } from "../db/prisma";
import { mqttService } from "../services/mqtt.service";
import { z } from "zod";

const CommandSchema = z.object({
  deviceId: z.string().default("esp32-01"),
  actuatorId: z.string().default("pump-01"),
  action: z.enum(["SET_STATE", "TOGGLE", "RESET_FAULT", "AUTO_ON", "AUTO_OFF"]),
  value: z.string().optional(),
});

export async function sendActuatorCommand(req: Request, res: Response) {
  try {
    const parseResult = CommandSchema.safeParse(req.body);
    if (!parseResult.success) {
      return res.status(400).json({ success: false, errors: parseResult.error.errors });
    }

    const { deviceId, actuatorId, action, value } = parseResult.data;
    const commandId = `cmd-${Date.now()}`;

    // 1. Log in Database
    const commandRecord = await prisma.command.create({
      data: {
        id: commandId,
        deviceId,
        actuatorId,
        action,
        value: value || null,
        status: "PENDING",
      },
    });

    // 2. Publish to MQTT for Edge Gateway
    const mqttPayload = {
      commandId,
      deviceId,
      actuatorId,
      action,
      value,
      timestamp: new Date().toISOString(),
    };

    const published = await mqttService.publishCommand(deviceId, mqttPayload);

    if (published) {
      await prisma.command.update({
        where: { id: commandId },
        data: { status: "EXECUTED", executedAt: new Date() },
      });
    }

    return res.json({
      success: true,
      message: `Command '${action}' dispatched successfully to device '${deviceId}'.`,
      command: commandRecord,
    });
  } catch (error: any) {
    return res.status(500).json({ success: false, error: error.message });
  }
}

export async function getCommands(req: Request, res: Response) {
  try {
    const deviceId = (req.query.deviceId as string) || "esp32-01";
    const commands = await prisma.command.findMany({
      where: { deviceId },
      orderBy: { createdAt: "desc" },
      take: 50,
    });
    return res.json({ success: true, count: commands.length, data: commands });
  } catch (error: any) {
    return res.status(500).json({ success: false, error: error.message });
  }
}
