"use client";

import React, { useState } from "react";
import { Power, ShieldAlert, Cpu, CheckCircle2, RotateCcw, AlertTriangle } from "lucide-react";
import { sendActuatorCommand } from "../lib/api";

export function ControlPanel() {
  const [pumpState, setPumpState] = useState<boolean>(false);
  const [autoWater, setAutoWater] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [lastFeedback, setLastFeedback] = useState<string | null>(null);

  const handleTogglePump = async () => {
    setLoading(true);
    const nextState = !pumpState;
    const res = await sendActuatorCommand(nextState ? "SET_STATE" : "SET_STATE", nextState ? "ON" : "OFF");
    if (res.success) {
      setPumpState(nextState);
      setLastFeedback(`Pump set to ${nextState ? "ON" : "OFF"}`);
    } else {
      setLastFeedback(`Error: ${res.error || "Failed to dispatch command"}`);
    }
    setLoading(false);
  };

  const handleToggleAutoWater = async () => {
    setLoading(true);
    const nextState = !autoWater;
    const res = await sendActuatorCommand(nextState ? "AUTO_ON" : "AUTO_OFF");
    if (res.success) {
      setAutoWater(nextState);
      setLastFeedback(`Auto-irrigation ${nextState ? "ENABLED" : "DISABLED"}`);
    }
    setLoading(false);
  };

  const handleResetFaults = async () => {
    setLoading(true);
    const res = await sendActuatorCommand("RESET_FAULT");
    if (res.success) {
      setLastFeedback("Safety lockout cleared. Ready.");
    }
    setLoading(false);
  };

  return (
    <div className="rounded-xl border border-border bg-surface p-5 flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between pb-4 border-b border-border/60">
          <div className="flex items-center gap-2">
            <Cpu className="w-5 h-5 text-emerald-400" />
            <h2 className="text-sm font-semibold text-textPrimary uppercase tracking-wider">
              Actuator & Safety Controls
            </h2>
          </div>
          {lastFeedback && (
            <span className="text-[11px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
              {lastFeedback}
            </span>
          )}
        </div>

        {/* Control Switches */}
        <div className="mt-5 space-y-4">
          {/* Pump Control Card */}
          <div className="flex items-center justify-between p-3.5 rounded-lg bg-background/50 border border-border">
            <div className="flex items-center gap-3">
              <div className={`p-2.5 rounded-lg ${pumpState ? "bg-emerald-500/20 text-emerald-400" : "bg-border text-textMuted"}`}>
                <Power className="w-4 h-4" />
              </div>
              <div>
                <h4 className="text-xs font-semibold text-textPrimary">Main Water Pump</h4>
                <p className="text-[11px] font-mono text-textMuted">Relay: pump-01 (GPIO 26)</p>
              </div>
            </div>

            <button
              onClick={handleTogglePump}
              disabled={loading}
              className={`px-4 py-1.5 rounded-lg text-xs font-mono font-bold transition-all ${
                pumpState
                  ? "bg-rose-500 hover:bg-rose-600 text-white shadow-lg shadow-rose-500/20"
                  : "bg-emerald-500 hover:bg-emerald-600 text-white shadow-lg shadow-emerald-500/20"
              }`}
            >
              {pumpState ? "TURN OFF" : "TURN ON"}
            </button>
          </div>

          {/* Auto Irrigation */}
          <div className="flex items-center justify-between p-3.5 rounded-lg bg-background/50 border border-border">
            <div className="flex items-center gap-3">
              <div className={`p-2.5 rounded-lg ${autoWater ? "bg-sky-500/20 text-sky-400" : "bg-border text-textMuted"}`}>
                <CheckCircle2 className="w-4 h-4" />
              </div>
              <div>
                <h4 className="text-xs font-semibold text-textPrimary">Auto-Irrigation Engine</h4>
                <p className="text-[11px] font-mono text-textMuted">Triggers when substrate &lt; 25%</p>
              </div>
            </div>

            <button
              onClick={handleToggleAutoWater}
              disabled={loading}
              className={`px-4 py-1.5 rounded-lg text-xs font-mono font-medium border transition-colors ${
                autoWater
                  ? "bg-sky-500/10 text-sky-400 border-sky-500/30"
                  : "bg-surfaceLight text-textMuted border-border hover:text-textPrimary"
              }`}
            >
              {autoWater ? "ENABLED" : "DISABLED"}
            </button>
          </div>

          {/* Safety Interlock Reset */}
          <div className="flex items-center justify-between p-3.5 rounded-lg bg-background/50 border border-border">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-lg bg-amber-500/10 text-amber-400">
                <ShieldAlert className="w-4 h-4" />
              </div>
              <div>
                <h4 className="text-xs font-semibold text-textPrimary">Hardware Safety Interlocks</h4>
                <p className="text-[11px] font-mono text-textMuted">8s Dry-run & 5m Max runtime</p>
              </div>
            </div>

            <button
              onClick={handleResetFaults}
              disabled={loading}
              className="px-3 py-1.5 rounded-lg text-xs font-mono font-medium border border-border bg-surfaceLight hover:bg-border text-textPrimary flex items-center gap-1.5 transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              CLEAR FAULTS
            </button>
          </div>
        </div>
      </div>

      <div className="mt-5 pt-3 border-t border-border/60 text-[11px] font-mono text-textMuted flex items-center justify-between">
        <span>Interlock Status: <strong className="text-emerald-400">ARMED</strong></span>
        <span>Target: <strong className="text-textPrimary">esp32-01</strong></span>
      </div>
    </div>
  );
}
