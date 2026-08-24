"use client";

import React from "react";
import { 
  Thermometer, 
  Activity, 
  Droplets, 
  Sprout, 
  Wind, 
  Gauge, 
  Database, 
  AlertCircle 
} from "lucide-react";
import { LatestTelemetryMap } from "../types/telemetry";

interface TelemetryPanelProps {
  telemetry: LatestTelemetryMap | null;
  isOnline: boolean;
  lastSyncedAt: string;
}

export const TelemetryPanel: React.FC<TelemetryPanelProps> = ({
  telemetry,
  isOnline,
  lastSyncedAt,
}) => {
  const getCardClass = (id: string, val: number | undefined, minOk: number, maxOk: number) => {
    if (val === undefined || val === null || !isOnline) return "val-gray";
    if (val >= minOk && val <= maxOk) return "val-green";
    if (id === "ph" && (val < 4.0 || val > 8.5)) return "val-red";
    return "val-yellow";
  };

  const formatValue = (val: number | undefined) => {
    if (val === undefined || val === null || !isOnline) return "--";
    return Number.isInteger(val) ? val.toString() : val.toFixed(1);
  };

  const temp = telemetry?.air_temperature?.value;
  const tds = telemetry?.tds?.value;
  const ph = telemetry?.ph?.value;
  const moist = telemetry?.substrate_moisture?.value;
  const hum = telemetry?.humidity?.value;
  const flow = telemetry?.flow_rate?.value;
  const vol = telemetry?.water_volume?.value;

  return (
    <section className="sensor-panel">
      <div className="section-title-row">
        <div className="sensor-header">
          <h2>Live Hydroponic Telemetry</h2>
          {!isOnline && (
            <span id="sensor-offline-badge" className="badge offline" style={{ display: "inline-flex", alignItems: "center", gap: "0.3rem" }}>
              <AlertCircle size={12} className="shrink-0" />
              Sensors Offline
            </span>
          )}
        </div>
        <div className="last-sync-text" id="last-sync-time">
          {isOnline ? `Last synced: ${lastSyncedAt}` : "Awaiting ESP32 connection..."}
        </div>
      </div>

      <div className="sensor-grid">
        {/* Temperature */}
        <div className="sensor-card" id="card-temp">
          <div className="sensor-info">
            <div className="sensor-label" style={{ display: "inline-flex", alignItems: "center", gap: "0.3rem" }}>
              <Thermometer size={13} className="text-rose-500" />
              Temperature
            </div>
            <div className="sensor-value">
              <span id="val-temp" className={getCardClass("temp", temp, 20, 30)}>
                {formatValue(temp)}
              </span>{" "}
              <span className="sensor-unit">°C</span>
            </div>
          </div>
        </div>

        {/* TDS */}
        <div className="sensor-card" id="card-tds">
          <div className="sensor-info">
            <div className="sensor-label" style={{ display: "inline-flex", alignItems: "center", gap: "0.3rem" }}>
              <Activity size={13} className="text-sky-500" />
              TDS (Nutrients)
            </div>
            <div className="sensor-value">
              <span id="val-tds" className={getCardClass("tds", tds, 500, 1400)}>
                {formatValue(tds)}
              </span>{" "}
              <span className="sensor-unit">ppm</span>
            </div>
          </div>
        </div>

        {/* pH */}
        <div className="sensor-card" id="card-ph">
          <div className="sensor-info">
            <div className="sensor-label" style={{ display: "inline-flex", alignItems: "center", gap: "0.3rem" }}>
              <Droplets size={13} className="text-purple-500" />
              pH Level
            </div>
            <div className="sensor-value">
              <span id="val-ph" className={getCardClass("ph", ph, 5.5, 6.5)}>
                {formatValue(ph)}
              </span>{" "}
              <span className="sensor-unit">pH</span>
            </div>
          </div>
        </div>

        {/* Moisture */}
        <div className="sensor-card" id="card-moist">
          <div className="sensor-info">
            <div className="sensor-label" style={{ display: "inline-flex", alignItems: "center", gap: "0.3rem" }}>
              <Sprout size={13} className="text-emerald-500" />
              Substrate Moisture
            </div>
            <div className="sensor-value">
              <span id="val-moist" className={getCardClass("moist", moist, 40, 80)}>
                {formatValue(moist)}
              </span>{" "}
              <span className="sensor-unit">%</span>
            </div>
          </div>
        </div>

        {/* Humidity */}
        <div className="sensor-card" id="card-hum">
          <div className="sensor-info">
            <div className="sensor-label" style={{ display: "inline-flex", alignItems: "center", gap: "0.3rem" }}>
              <Wind size={13} className="text-cyan-500" />
              Air Humidity
            </div>
            <div className="sensor-value">
              <span id="val-hum" className={getCardClass("hum", hum, 45, 75)}>
                {formatValue(hum)}
              </span>{" "}
              <span className="sensor-unit">%</span>
            </div>
          </div>
        </div>

        {/* Water Flow */}
        <div className="sensor-card" id="card-flow">
          <div className="sensor-info">
            <div className="sensor-label" style={{ display: "inline-flex", alignItems: "center", gap: "0.3rem" }}>
              <Gauge size={13} className="text-blue-500" />
              Water Flow
            </div>
            <div className="sensor-value">
              <span id="val-flow" className={getCardClass("flow", flow, 0.2, 3.0)}>
                {formatValue(flow)}
              </span>{" "}
              <span className="sensor-unit">L/min</span>
            </div>
          </div>
        </div>

        {/* Volume */}
        <div className="sensor-card" id="card-vol">
          <div className="sensor-info">
            <div className="sensor-label" style={{ display: "inline-flex", alignItems: "center", gap: "0.3rem" }}>
              <Database size={13} className="text-amber-500" />
              Total Volume
            </div>
            <div className="sensor-value">
              <span id="val-vol" className={getCardClass("vol", vol, 2, 50)}>
                {formatValue(vol)}
              </span>{" "}
              <span className="sensor-unit">L</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
