"use client";

import React from "react";
import { LayoutDashboard, Sliders, BrainCircuit, Cpu, Sprout } from "lucide-react";

interface HeaderProps {
  activeView: "main" | "analytics";
  onSwitchView: (view: "main" | "analytics") => void;
  aiStatus: "online" | "offline" | "loading";
  iotStatus: "online" | "offline" | "loading";
}

export const Header: React.FC<HeaderProps> = ({
  activeView,
  onSwitchView,
  aiStatus,
  iotStatus,
}) => {
  return (
    <header className="header">
      <div className="logo-container">
        <div className="logo">
          <Sprout size={20} className="text-emerald-600 inline" />
          AgroEye AI
        </div>
        <span className="sub-brand">Hydroponic Ecosystem Intelligence</span>
      </div>

      {/* View Switcher Pills */}
      <div className="view-switcher-container">
        <button
          id="header-btn-main"
          className={`view-pill ${activeView === "main" ? "active" : ""}`}
          onClick={() => onSwitchView("main")}
          style={{ display: "inline-flex", alignItems: "center", gap: "0.4rem" }}
        >
          <LayoutDashboard size={14} />
          <span>Live Overview</span>
        </button>
        <button
          id="header-btn-analytics"
          className={`view-pill ${activeView === "analytics" ? "active" : ""}`}
          onClick={() => onSwitchView("analytics")}
          style={{ display: "inline-flex", alignItems: "center", gap: "0.4rem" }}
        >
          <Sliders size={14} />
          <span>Analytics &amp; Controls</span>
        </button>
      </div>

      <div className="header-right">
        <div className="status-container">
          <div className="status-indicator">
            <span
              id="ai-status-dot"
              className={`dot ${aiStatus}`}
            ></span>
            <BrainCircuit size={13} className="text-slate-600" />
            <span className="status-label">AI Pathology</span>
          </div>
          <div className="status-indicator">
            <span
              id="iot-status-dot"
              className={`dot ${iotStatus}`}
            ></span>
            <Cpu size={13} className="text-slate-600" />
            <span className="status-label">IoT Controller</span>
          </div>
        </div>
      </div>
    </header>
  );
};
