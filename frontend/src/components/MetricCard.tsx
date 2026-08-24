import React from "react";
import { LucideIcon } from "lucide-react";
import { formatMetricValue } from "../lib/utils";

interface MetricCardProps {
  label: string;
  metric: string;
  value: number | undefined | null;
  unit: string;
  icon: LucideIcon;
  accentColor: string; // e.g. "text-coral", "text-sky-400"
  badgeBg: string;
  sensorId: string;
  quality?: string;
  optimalRange: string;
  statusText?: string;
  statusType?: "OPTIMAL" | "WARNING" | "CRITICAL";
}

export function MetricCard({
  label,
  metric,
  value,
  unit,
  icon: Icon,
  accentColor,
  badgeBg,
  sensorId,
  quality = "GOOD",
  optimalRange,
  statusText,
  statusType = "OPTIMAL",
}: MetricCardProps) {
  const formatted = formatMetricValue(value, metric);

  const statusColor = {
    OPTIMAL: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
    WARNING: "text-amber-400 bg-amber-500/10 border-amber-500/20",
    CRITICAL: "text-rose-400 bg-rose-500/10 border-rose-500/20",
  }[statusType];

  return (
    <div className="rounded-xl border border-border bg-surface p-5 hover:border-borderLight transition-all flex flex-col justify-between">
      {/* Top row: Label & Icon */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className={`p-2 rounded-lg ${badgeBg}`}>
            <Icon className={`w-4 h-4 ${accentColor}`} />
          </div>
          <div>
            <h3 className="text-xs font-semibold text-textMuted uppercase tracking-wider">
              {label}
            </h3>
            <span className="text-[10px] font-mono text-textMuted/70">
              {sensorId}
            </span>
          </div>
        </div>

        {statusText && (
          <span className={`text-[10px] font-mono font-medium px-2 py-0.5 rounded border uppercase ${statusColor}`}>
            {statusText}
          </span>
        )}
      </div>

      {/* Main Value & Unit */}
      <div className="my-4 flex items-baseline gap-1.5">
        <span className={`text-3xl sm:text-4xl font-bold font-mono tracking-tight tabular-nums ${accentColor}`}>
          {formatted}
        </span>
        <span className="text-sm font-mono text-textMuted font-medium">
          {unit}
        </span>
      </div>

      {/* Bottom Range & Data Quality */}
      <div className="pt-3 border-t border-border/60 flex items-center justify-between text-[11px] font-mono text-textMuted">
        <span>Target: <strong className="text-textPrimary">{optimalRange}</strong></span>
        <span className="flex items-center gap-1">
          <span className={`w-1.5 h-1.5 rounded-full ${quality === "GOOD" ? "bg-emerald-400" : "bg-rose-400"}`} />
          {quality}
        </span>
      </div>
    </div>
  );
}
