"use client";

import React, { useState, useEffect } from "react";
import { Camera, RefreshCw, Sparkles, Video, Play, Pause, Maximize2 } from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:4000/api/v1";

export function CameraView() {
  const [streamUrl, setStreamUrl] = useState<string>(`${API_BASE}/camera/stream`);
  const [isPlaying, setIsPlaying] = useState<boolean>(true);
  const [status, setStatus] = useState<any>(null);
  const [key, setKey] = useState<number>(Date.now());

  const fetchStatus = async () => {
    try {
      const res = await fetch(`${API_BASE}/camera/status`);
      if (res.ok) {
        const data = await res.json();
        setStatus(data);
      }
    } catch (e) {
      console.error("Camera status error:", e);
    }
  };

  const handleTogglePlay = () => {
    if (isPlaying) {
      // Freeze on latest snapshot
      setStreamUrl(`${API_BASE}/camera/latest?t=${Date.now()}`);
      setIsPlaying(false);
    } else {
      // Resume live MJPEG stream
      setStreamUrl(`${API_BASE}/camera/stream?t=${Date.now()}`);
      setIsPlaying(true);
      setKey(Date.now());
    }
  };

  const handleRefresh = () => {
    setKey(Date.now());
    setStreamUrl(`${API_BASE}/camera/stream?t=${Date.now()}`);
    fetchStatus();
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  return (
    <div className="rounded-xl border border-border bg-surface p-5 flex flex-col justify-between">
      <div>
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-border/60">
          <div className="flex items-center gap-2">
            <Video className="w-5 h-5 text-sky-400" />
            <h2 className="text-sm font-semibold text-textPrimary uppercase tracking-wider">
              Live Plant Camera
            </h2>
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-border text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              LIVE STREAM
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleTogglePlay}
              className="p-1.5 rounded-lg border border-border bg-surfaceLight hover:bg-border text-textMuted hover:text-textPrimary transition-colors"
              title={isPlaying ? "Pause Stream" : "Resume Stream"}
            >
              {isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5 text-emerald-400" />}
            </button>
            <button
              onClick={handleRefresh}
              className="p-1.5 rounded-lg border border-border bg-surfaceLight hover:bg-border text-textMuted hover:text-textPrimary transition-colors"
              title="Reload Stream"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Live Video Feed Container */}
        <div className="mt-4 relative aspect-[4/3] rounded-lg overflow-hidden border border-border bg-background/90 flex items-center justify-center group">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            key={key}
            src={streamUrl}
            alt="Live Plant Canopy Video Stream"
            className="w-full h-full object-cover"
            onError={(e) => {
              // Retry on brief stream glitch
              setTimeout(() => setKey(Date.now()), 1500);
            }}
          />

          {/* Live Recording Badge */}
          <div className="absolute top-2.5 left-2.5 px-2 py-1 rounded bg-background/85 backdrop-blur-md border border-border/80 text-[10px] font-mono text-rose-400 flex items-center gap-1.5 shadow-sm">
            <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping" />
            REC &bull; 800x600 HD
          </div>

          {/* AI Interface Ready Pill */}
          <div className="absolute bottom-2.5 right-2.5 px-2 py-1 rounded bg-background/85 backdrop-blur-md border border-border/80 text-[10px] font-mono text-sky-400 flex items-center gap-1 shadow-sm">
            <Sparkles className="w-3 h-3 text-sky-400" />
            AI Hook: get_latest_frame()
          </div>
        </div>
      </div>

      {/* Bottom Metadata */}
      <div className="mt-4 pt-3 border-t border-border/60 text-[11px] font-mono text-textMuted flex items-center justify-between">
        <span>Source: <strong className="text-textPrimary">ESP32-CAM (COM9)</strong></span>
        <span>Mode: <strong className="text-emerald-400">{isPlaying ? "Continuous Stream" : "Paused"}</strong></span>
      </div>
    </div>
  );
}
