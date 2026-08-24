import React from "react";
import { cn } from "../lib/utils";

interface StatusBadgeProps {
  status: "ONLINE" | "OFFLINE" | "OPTIMAL" | "WARNING" | "CRITICAL" | "ACTIVE" | "IDLE";
  label?: string;
  size?: "sm" | "md";
}

export function StatusBadge({ status, label, size = "md" }: StatusBadgeProps) {
  const displayLabel = label || status;

  const colorStyles = {
    ONLINE: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    OPTIMAL: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    ACTIVE: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    IDLE: "bg-slate-500/10 text-slate-400 border-slate-500/20",
    OFFLINE: "bg-rose-500/10 text-rose-400 border-rose-500/20",
    CRITICAL: "bg-rose-500/10 text-rose-400 border-rose-500/20",
    WARNING: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  }[status] || "bg-slate-500/10 text-slate-400 border-slate-500/20";

  const dotColor = {
    ONLINE: "bg-emerald-400",
    OPTIMAL: "bg-emerald-400",
    ACTIVE: "bg-emerald-400",
    IDLE: "bg-slate-400",
    OFFLINE: "bg-rose-400",
    CRITICAL: "bg-rose-400",
    WARNING: "bg-amber-400",
  }[status] || "bg-slate-400";

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 font-mono font-medium border rounded-md uppercase tracking-wider",
        size === "sm" ? "px-2 py-0.5 text-[10px]" : "px-2.5 py-1 text-xs",
        colorStyles
      )}
    >
      <span className={cn("w-1.5 h-1.5 rounded-full animate-pulse", dotColor)} />
      {displayLabel}
    </span>
  );
}
