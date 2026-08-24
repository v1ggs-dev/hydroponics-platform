import React from "react";
import { Thermometer, Droplets, Zap, Gauge, Waves, Container, FlaskConical } from "lucide-react";
import { MetricCard } from "./MetricCard";
import { LatestTelemetryMap } from "../types/telemetry";

interface TelemetryGridProps {
  telemetry: LatestTelemetryMap;
}

export function TelemetryGrid({ telemetry }: TelemetryGridProps) {
  const temp = telemetry["air_temperature"];
  const hum = telemetry["humidity"];
  const ph = telemetry["ph"];
  const tds = telemetry["tds"];
  const moist = telemetry["substrate_moisture"];
  const flow = telemetry["flow_rate"];
  const vol = telemetry["water_volume"];

  // Evaluate temperature status
  const tempVal = temp?.value;
  const tempStatus = tempVal !== undefined && !isNaN(tempVal)
    ? tempVal < 18 ? "COLD" : tempVal > 30 ? "WARM" : "OPTIMAL"
    : "PENDING";

  // Evaluate pH status
  const phVal = ph?.value;
  const phStatus = phVal !== undefined && !isNaN(phVal)
    ? phVal < 5.5 ? "ACIDIC" : phVal > 6.8 ? "ALKALINE" : "OPTIMAL"
    : "PENDING";

  // Evaluate moisture status
  const moistVal = moist?.value;
  const moistStatus = moistVal !== undefined && !isNaN(moistVal)
    ? moistVal < 25 ? "LOW / DRY" : moistVal > 80 ? "SATURATED" : "OPTIMAL"
    : "PENDING";

  // Evaluate TDS status
  const tdsVal = tds?.value;
  const tdsStatus = tdsVal !== undefined && !isNaN(tdsVal)
    ? tdsVal < 200 ? "LOW EC" : tdsVal > 900 ? "HIGH EC" : "OPTIMAL"
    : "PENDING";

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {/* Card 1: Air Temp */}
      <MetricCard
        label="Air Temperature"
        metric="air_temperature"
        value={temp?.value}
        unit="°C"
        icon={Thermometer}
        accentColor="text-rose-400"
        badgeBg="bg-rose-500/10"
        sensorId="dht11-01"
        quality={temp?.quality}
        optimalRange="20–26°C"
        statusText={tempStatus}
        statusType={tempStatus === "OPTIMAL" ? "OPTIMAL" : "WARNING"}
      />

      {/* Card 2: Relative Humidity */}
      <MetricCard
        label="Relative Humidity"
        metric="humidity"
        value={hum?.value}
        unit="%"
        icon={Droplets}
        accentColor="text-sky-400"
        badgeBg="bg-sky-500/10"
        sensorId="dht11-01"
        quality={hum?.quality}
        optimalRange="60–85%"
        statusText={hum?.value ? "OPTIMAL" : "PENDING"}
        statusType="OPTIMAL"
      />

      {/* Card 3: Solution pH */}
      <MetricCard
        label="Solution Acidity / pH"
        metric="ph"
        value={ph?.value}
        unit="pH"
        icon={FlaskConical}
        accentColor="text-fuchsia-400"
        badgeBg="bg-fuchsia-500/10"
        sensorId="ph-01"
        quality={ph?.quality}
        optimalRange="5.5–6.5 pH"
        statusText={phStatus}
        statusType={phStatus === "OPTIMAL" ? "OPTIMAL" : "WARNING"}
      />

      {/* Card 4: Water Nutrient TDS */}
      <MetricCard
        label="Nutrient Concentration"
        metric="tds"
        value={tds?.value}
        unit="ppm"
        icon={Zap}
        accentColor="text-emerald-400"
        badgeBg="bg-emerald-500/10"
        sensorId="tds-01"
        quality={tds?.quality}
        optimalRange="300–800 ppm"
        statusText={tdsStatus}
        statusType={tdsStatus === "OPTIMAL" ? "OPTIMAL" : "WARNING"}
      />

      {/* Card 5: Substrate Moisture */}
      <MetricCard
        label="Substrate Moisture"
        metric="substrate_moisture"
        value={moist?.value}
        unit="%"
        icon={Gauge}
        accentColor="text-amber-400"
        badgeBg="bg-amber-500/10"
        sensorId="moisture-01"
        quality={moist?.quality}
        optimalRange="40–75%"
        statusText={moistStatus}
        statusType={moistStatus === "OPTIMAL" ? "OPTIMAL" : moistStatus.includes("LOW") ? "CRITICAL" : "WARNING"}
      />

      {/* Card 6: Flow Rate */}
      <MetricCard
        label="Water Flow Rate"
        metric="flow_rate"
        value={flow?.value}
        unit="L/min"
        icon={Waves}
        accentColor="text-cyan-400"
        badgeBg="bg-cyan-500/10"
        sensorId="flow-01"
        quality={flow?.quality}
        optimalRange="0.5–8.0 L/min"
        statusText={flow?.value && flow.value > 0.1 ? "ACTIVE FLOW" : "IDLE"}
        statusType={flow?.value && flow.value > 0.1 ? "OPTIMAL" : "OPTIMAL"}
      />

      {/* Card 7: Accumulated Water Volume */}
      <MetricCard
        label="Total Dispensed Volume"
        metric="water_volume"
        value={vol?.value}
        unit="Liters"
        icon={Container}
        accentColor="text-indigo-400"
        badgeBg="bg-indigo-500/10"
        sensorId="flow-01"
        quality={vol?.quality}
        optimalRange="Cumulative"
        statusText="TRACKING"
        statusType="OPTIMAL"
      />
    </div>
  );
}
