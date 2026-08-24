"use client";

import React from "react";
import { AlertTriangle, Bell, Check, ShieldCheck } from "lucide-react";
import { AlertItem } from "../types/telemetry";
import { resolveAlert } from "../lib/api";
import { formatTimeAgo } from "../lib/utils";

interface AlertFeedProps {
  alerts: AlertItem[];
  onRefresh?: () => void;
}

export function AlertFeed({ alerts, onRefresh }: AlertFeedProps) {
  const activeAlerts = alerts.filter((a) => !a.resolved);

  const handleResolve = async (id: number | string) => {
    await resolveAlert(id);
    if (onRefresh) onRefresh();
  };

  return (
    <div className="rounded-xl border border-border bg-surface p-5 flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between pb-4 border-b border-border/60">
          <div className="flex items-center gap-2">
            <Bell className="w-5 h-5 text-amber-400" />
            <h2 className="text-sm font-semibold text-textPrimary uppercase tracking-wider">
              System Alerts & Events
            </h2>
          </div>
          <span className="text-xs font-mono text-textMuted">
            Active: <strong className={activeAlerts.length > 0 ? "text-rose-400" : "text-emerald-400"}>{activeAlerts.length}</strong>
          </span>
        </div>

        {/* Alert List */}
        <div className="mt-4 space-y-2.5 max-h-60 overflow-y-auto pr-1">
          {activeAlerts.length === 0 ? (
            <div className="py-8 flex flex-col items-center justify-center text-center text-textMuted">
              <ShieldCheck className="w-8 h-8 text-emerald-400/60 mb-2" />
              <p className="text-xs font-medium text-textPrimary">All Systems Nominal</p>
              <p className="text-[11px] font-mono mt-0.5">No active hardware faults or warnings.</p>
            </div>
          ) : (
            activeAlerts.map((alert) => (
              <div
                key={alert.id}
                className="p-3 rounded-lg border border-border bg-background/50 flex items-start justify-between gap-3"
              >
                <div className="flex items-start gap-2.5">
                  <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold text-textPrimary">{alert.type}</span>
                      <span className="text-[10px] font-mono text-textMuted">{formatTimeAgo(alert.createdAt)}</span>
                    </div>
                    <p className="text-xs text-textMuted mt-0.5">{alert.message}</p>
                  </div>
                </div>

                <button
                  onClick={() => handleResolve(alert.id)}
                  className="p-1.5 rounded bg-surfaceLight hover:bg-border border border-border text-textMuted hover:text-emerald-400 transition-colors"
                  title="Mark Resolved"
                >
                  <Check className="w-3.5 h-3.5" />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-border/60 text-[11px] font-mono text-textMuted flex items-center justify-between">
        <span>Log Retention: <strong className="text-textPrimary">Supabase Cloud</strong></span>
        <span>Auto-Sync: <strong className="text-emerald-400">ENABLED</strong></span>
      </div>
    </div>
  );
}
