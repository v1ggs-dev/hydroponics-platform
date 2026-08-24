"use client";

import React, { useState } from "react";
import { Sliders, Power, Cpu, ShieldAlert, RotateCcw } from "lucide-react";

interface IoTControlSwitchboardProps {
  onSendCommand: (action: string, value?: string) => Promise<boolean>;
  isPumpRunning: boolean;
  isAutoEnabled: boolean;
  feedbackMessage: string;
}

export const IoTControlSwitchboard: React.FC<IoTControlSwitchboardProps> = ({
  onSendCommand,
  isPumpRunning,
  isAutoEnabled,
  feedbackMessage,
}) => {
  const [safetyCleared, setSafetyCleared] = useState(true);

  const handleTogglePump = () => {
    const nextState = isPumpRunning ? "OFF" : "ON";
    onSendCommand("SET_STATE", nextState);
  };

  const handleToggleAuto = () => {
    const nextAction = isAutoEnabled ? "AUTO_OFF" : "AUTO_ON";
    onSendCommand(nextAction);
  };

  const handleClearFaults = () => {
    onSendCommand("RESET_FAULT");
    setSafetyCleared(true);
  };

  return (
    <section className="glass-panel control-switchboard">
      <div className="panel-header-row">
        <h2 style={{ display: "flex", alignItems: "center", gap: "0.45rem" }}>
          <Sliders size={18} className="text-emerald-600" />
          IoT Remote Actuator Controls
        </h2>
        <span id="controller-mode-badge" className="badge low">
          EDGE CONNECTED
        </span>
      </div>

      <div className="controls-list">
        {/* Pump Switch */}
        <div className="control-tile">
          <div className="tile-info">
            <div className="tile-title" style={{ display: "flex", alignItems: "center", gap: "0.35rem" }}>
              <Power size={14} className={isPumpRunning ? "text-emerald-600" : "text-slate-400"} />
              Nutrient Pump Relay (GPIO 26)
            </div>
            <div
              className="tile-sub"
              id="pump-state-text"
              style={{ color: isPumpRunning ? "#059669" : "#64748b" }}
            >
              {isPumpRunning ? "State: Active (Dosing Reservoir)" : "State: Standby / Idle"}
            </div>
          </div>
          <button
            id="toggle-pump-btn"
            className={`switch-btn ${isPumpRunning ? "on" : "off"}`}
            onClick={handleTogglePump}
          >
            <span className="switch-knob"></span>
            <span className="switch-label">
              {isPumpRunning ? "PUMP RUNNING" : "START PUMP"}
            </span>
          </button>
        </div>

        {/* Auto Irrigation Toggle */}
        <div className="control-tile">
          <div className="tile-info">
            <div className="tile-title" style={{ display: "flex", alignItems: "center", gap: "0.35rem" }}>
              <Cpu size={14} className="text-sky-600" />
              Autonomous Smart Irrigation
            </div>
            <div className="tile-sub">Moisture-triggered automated dosing</div>
          </div>
          <button
            id="toggle-auto-btn"
            className={`switch-btn ${isAutoEnabled ? "on" : "off"}`}
            onClick={handleToggleAuto}
          >
            <span className="switch-knob"></span>
            <span className="switch-label">
              {isAutoEnabled ? "AUTO ACTIVE" : "MANUAL ONLY"}
            </span>
          </button>
        </div>

        {/* Safety Reset / Emergency Stop */}
        <div className="control-tile danger-tile">
          <div className="tile-info">
            <div className="tile-title" style={{ display: "flex", alignItems: "center", gap: "0.35rem" }}>
              <ShieldAlert size={14} className="text-red-500" />
              Safety Interlock &amp; Alarm
            </div>
            <div
              className="tile-sub"
              id="safety-status-text"
              style={{ color: safetyCleared ? "#059669" : "#ef4444" }}
            >
              {safetyCleared ? "Interlock: Normal (No Faults)" : "Interlock: Fault Tripped"}
            </div>
          </div>
          <button
            id="reset-safety-btn"
            className="action-mini-btn"
            onClick={handleClearFaults}
            style={{ display: "inline-flex", alignItems: "center", gap: "0.3rem" }}
          >
            <RotateCcw size={12} />
            Clear Faults
          </button>
        </div>
      </div>

      <div className="command-feedback" id="command-feedback-msg">
        {feedbackMessage || "Ready to dispatch MQTT commands to esp32-env"}
      </div>
    </section>
  );
};
