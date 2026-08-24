"use client";

import React from "react";
import { Layers, Cpu, Database, Radio, RefreshCw } from "lucide-react";
import { formatTimeAgo } from "../lib/utils";

interface NavbarProps {
  deviceStatus: "ONLINE" | "OFFLINE";
  wsConnected: boolean;
  lastUpdated: string;
  uptimeSeconds: number;
  onRefresh: () => void;
}

export function Navbar({
  deviceStatus,
  wsConnected,
  lastUpdated,
  uptimeSeconds,
  onRefresh,
}: NavbarProps) {
  const formatUptime = (seconds: number) => {
    if (!seconds) return "0s";
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    if (h > 0) return `${h}h ${m}m`;
    if (m > 0) return `${m}m ${s}s`;
    return `${s}s`;
  };

  return (
    <header className="border-b border-border bg-surface/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Left: Branding & Multi-Node Tag */}
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-semibold text-textPrimary tracking-tight">
                Hydroponics Control Platform
              </h1>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-border text-textMuted">
                v0.2.0-DUAL
              </span>
            </div>
            <p className="text-xs text-textMuted font-mono">
              Nodes: <span className="text-textPrimary">esp32-env &amp; esp32-chem</span> &bull; Displays: <span className="text-textPrimary">2x ST7735</span>
            </p>
          </div>
        </div>

        {/* Center: Live Architecture Connection Telemetry */}
        <div className="hidden md:flex items-center gap-4 text-xs font-mono text-textMuted bg-background/50 border border-border/80 px-3.5 py-1.5 rounded-lg">
          <div className="flex items-center gap-1.5">
            <Cpu className="w-3.5 h-3.5 text-textMuted" />
            <span>Dual ESP32:</span>
            <span className={deviceStatus === "ONLINE" ? "text-emerald-400" : "text-emerald-400"}>
              ACTIVE
            </span>
          </div>

          <div className="w-px h-3 bg-border" />

          <div className="flex items-center gap-1.5">
            <Database className="w-3.5 h-3.5 text-textMuted" />
            <span>Supabase:</span>
            <span className="text-emerald-400">SYNCED</span>
          </div>

          <div className="w-px h-3 bg-border" />

          <div className="flex items-center gap-1.5">
            <Radio className="w-3.5 h-3.5 text-textMuted" />
            <span>WebSocket:</span>
            <span className={wsConnected ? "text-sky-400" : "text-amber-400"}>
              {wsConnected ? "LIVE STREAM" : "POLLING"}
            </span>
          </div>
        </div>

        {/* Right: Last Synced & Actions */}
        <div className="flex items-center gap-3">
          <div className="text-right hidden sm:block">
            <div className="text-[11px] font-mono text-textMuted">
              Uptime: <span className="text-textPrimary tabular-nums">{formatUptime(uptimeSeconds)}</span>
            </div>
            <div className="text-[11px] font-mono text-textMuted">
              Synced: <span className="text-emerald-400">{formatTimeAgo(lastUpdated)}</span>
            </div>
          </div>

          <button
            onClick={onRefresh}
            className="p-2 rounded-lg border border-border bg-surfaceLight hover:bg-border/60 text-textMuted hover:text-textPrimary transition-colors"
            title="Refresh latest telemetry"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>

      </div>
    </header>
  );
}
