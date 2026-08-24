"use client";

import React from "react";
import { LatestTelemetryMap } from "../types/telemetry";

import { HeartPulse } from "lucide-react";

interface HealthAndVPDCardProps {
  telemetry: LatestTelemetryMap | null;
  isOnline: boolean;
}

export const HealthAndVPDCard: React.FC<HealthAndVPDCardProps> = ({
  telemetry,
  isOnline,
}) => {
  const temp = telemetry?.air_temperature?.value ?? 25.0;
  const hum = telemetry?.humidity?.value ?? 60.0;
  const ph = telemetry?.ph?.value ?? 6.0;
  const tds = telemetry?.tds?.value ?? 850;

  // 1. Calculate Vapor Pressure Deficit (VPD in kPa)
  const vpSat = 0.61078 * Math.exp((17.27 * temp) / (temp + 237.3));
  const vpActual = vpSat * (hum / 100.0);
  const vpd = isOnline ? Math.max(0, vpSat - vpActual) : 1.15;

  // 2. Compute Health Index (0-100%)
  let health = 100;
  if (ph < 5.5 || ph > 6.5) health -= Math.min(30, Math.abs(6.0 - ph) * 25);
  if (tds < 600) health -= Math.min(25, ((600 - tds) / 600) * 25);
  if (tds > 1400) health -= Math.min(25, ((tds - 1400) / 1000) * 25);
  if (temp < 18 || temp > 32) health -= Math.min(20, Math.abs(25 - temp) * 2);
  health = isOnline ? Math.max(20, Math.min(100, Math.round(health))) : 96;

  let healthStatusText = "EXCELLENT";
  let healthBadgeClass = "badge low";
  let healthStrokeColor = "#10b981";

  if (health < 60) {
    healthStatusText = "ACTION REQUIRED";
    healthBadgeClass = "badge high";
    healthStrokeColor = "#ef4444";
  } else if (health < 80) {
    healthStatusText = "MONITORING";
    healthBadgeClass = "badge medium";
    healthStrokeColor = "#f59e0b";
  }

  // Radial SVG stroke offset (circumference = 2 * PI * 40 = 251.2)
  const strokeOffset = 251.2 - (251.2 * health) / 100;

  // VPD Scale Position
  let markerPercent = 50;
  let vpdBadgeText = "IDEAL TRANSPIRATION";
  let vpdBadgeClass = "status-pill green";
  let vpdDesc = "Stomata are actively transpiring with optimal nutrient uptake. Low fungal pathogen pressure.";

  if (vpd < 0.4) {
    markerPercent = (vpd / 0.4) * 25;
    vpdBadgeText = "LOW TRANSPIRATION (HUMID)";
    vpdBadgeClass = "status-pill yellow";
    vpdDesc = "Air is saturated. Transpiration is stunted, increasing risks of mold and fungal pathogens.";
  } else if (vpd <= 1.2) {
    markerPercent = 25 + ((vpd - 0.4) / 0.8) * 45;
    vpdBadgeText = "OPTIMAL VEGETATIVE UPTAKE";
    vpdBadgeClass = "status-pill green";
    vpdDesc = "Stomata are breathing freely with balanced nutrient and water transport to foliage.";
  } else if (vpd <= 1.6) {
    markerPercent = 70 + ((vpd - 1.2) / 0.4) * 15;
    vpdBadgeText = "OPTIMAL FLOWERING / FRUITING";
    vpdBadgeClass = "status-pill green";
    vpdDesc = "Mild evaporative pull encouraging dense root feeding and robust flowering.";
  } else {
    markerPercent = Math.min(98, 85 + ((vpd - 1.6) / 1.0) * 15);
    vpdBadgeText = "WATER STRESS / DRY AIR";
    vpdBadgeClass = "status-pill red";
    vpdDesc = "High evaporative loss causes leaf tip curling and moisture stress. Increase humidity.";
  }

  return (
    <section className="glass-panel agronomic-card">
      <div className="panel-header-row">
        <h2 style={{ display: "flex", alignItems: "center", gap: "0.45rem" }}>
          <HeartPulse size={18} className="text-emerald-600" />
          Agronomic &amp; System Health
        </h2>
        <span id="health-badge" className={healthBadgeClass}>
          {healthStatusText}
        </span>
      </div>

      <div className="agronomic-grid">
        {/* Overall Health Score Gauge */}
        <div className="health-score-block">
          <div className="radial-gauge-container">
            <svg className="radial-svg" viewBox="0 0 100 100">
              <circle className="radial-bg" cx="50" cy="50" r="40" />
              <circle
                id="health-circle-bar"
                className="radial-bar"
                cx="50"
                cy="50"
                r="40"
                style={{
                  stroke: healthStrokeColor,
                  strokeDashoffset: strokeOffset,
                }}
              />
            </svg>
            <div className="radial-center-text">
              <span id="health-score-val">{health}</span>
              <span className="radial-pct">%</span>
            </div>
          </div>
          <div className="gauge-caption">System Health Index</div>
        </div>

        {/* VPD & Transpiration Rate */}
        <div className="vpd-block">
          <div className="vpd-header">
            <span className="vpd-title">Vapor Pressure Deficit (VPD)</span>
            <span id="vpd-status-badge" className={vpdBadgeClass}>
              {vpdBadgeText}
            </span>
          </div>
          <div className="vpd-value-row">
            <span id="vpd-val">{vpd.toFixed(2)}</span>{" "}
            <span className="vpd-unit">kPa</span>
          </div>
          <p className="vpd-desc" id="vpd-description">
            {vpdDesc}
          </p>
          <div className="vpd-scale-bar">
            <div
              id="vpd-indicator-marker"
              className="vpd-marker"
              style={{ left: `${markerPercent}%` }}
            ></div>
          </div>
          <div className="vpd-scale-labels">
            <span>0.4 (Under)</span>
            <span>1.0 (Optimal)</span>
            <span>1.6+ (Stress)</span>
          </div>
        </div>
      </div>
    </section>
  );
};
