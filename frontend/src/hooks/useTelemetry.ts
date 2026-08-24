"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { LatestTelemetryMap, AlertItem, EdgeHealth } from "../types/telemetry";
import { fetchLatestTelemetry, fetchAlerts } from "../lib/api";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:4000/ws";

export function useTelemetry(deviceId: string = "esp32-01") {
  const [telemetry, setTelemetry] = useState<LatestTelemetryMap>({});
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [edgeHealth, setEdgeHealth] = useState<EdgeHealth | null>(null);
  const [deviceStatus, setDeviceStatus] = useState<"ONLINE" | "OFFLINE">("ONLINE");
  const [wsConnected, setWsConnected] = useState<boolean>(false);
  const [lastUpdated, setLastUpdated] = useState<string>("");
  const [uptimeSeconds, setUptimeSeconds] = useState<number>(0);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Initial Data Fetch
  const loadInitialData = useCallback(async () => {
    const latestRes = await fetchLatestTelemetry(deviceId);
    if (latestRes?.success && latestRes.data) {
      setTelemetry(latestRes.data);
      setLastUpdated(latestRes.timestamp || new Date().toISOString());
    }

    const alertsRes = await fetchAlerts();
    if (alertsRes?.success && alertsRes.data) {
      setAlerts(alertsRes.data);
    }
  }, [deviceId]);

  useEffect(() => {
    loadInitialData();

    function connectWebSocket() {
      if (wsRef.current?.readyState === WebSocket.OPEN) return;

      try {
        const ws = new WebSocket(WS_URL);
        wsRef.current = ws;

        ws.onopen = () => {
          console.log("🟢 [Frontend WS] Connected to backend real-time stream.");
          setWsConnected(true);
        };

        ws.onmessage = (event) => {
          try {
            const msg = JSON.parse(event.data);

            if (msg.event === "telemetry" && msg.data) {
              const measurements = msg.data.measurements || [];
              const newMap: LatestTelemetryMap = {};

              measurements.forEach((m: any) => {
                newMap[m.metric] = {
                  value: m.value,
                  unit: m.unit,
                  quality: m.quality,
                  sensorId: m.sensorId,
                  timestamp: msg.data.timestamp,
                };
              });

              setTelemetry((prev) => ({ ...prev, ...newMap }));
              setLastUpdated(msg.data.timestamp || new Date().toISOString());
              if (msg.data.uptimeSeconds) setUptimeSeconds(msg.data.uptimeSeconds);
              setDeviceStatus("ONLINE");
            } else if (msg.event === "device_status" && msg.data) {
              setDeviceStatus(msg.data.status || "ONLINE");
            } else if (msg.event === "alert" && msg.data) {
              setAlerts((prev) => [msg.data, ...prev]);
            } else if (msg.event === "edge_health" && msg.data) {
              setEdgeHealth(msg.data);
            }
          } catch (err) {
            console.error("WS Parse error:", err);
          }
        };

        ws.onclose = () => {
          console.log("🔴 [Frontend WS] Disconnected. Reconnecting in 3s...");
          setWsConnected(false);
          reconnectTimeoutRef.current = setTimeout(connectWebSocket, 3000);
        };

        ws.onerror = () => {
          ws.close();
        };
      } catch (e) {
        reconnectTimeoutRef.current = setTimeout(connectWebSocket, 3000);
      }
    }

    connectWebSocket();

    // Fallback polling every 5s if WS is offline
    const pollInterval = setInterval(() => {
      if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
        loadInitialData();
      }
    }, 5000);

    return () => {
      clearInterval(pollInterval);
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [loadInitialData]);

  return {
    telemetry,
    alerts,
    edgeHealth,
    deviceStatus,
    wsConnected,
    lastUpdated,
    uptimeSeconds,
    refreshData: loadInitialData,
  };
}
