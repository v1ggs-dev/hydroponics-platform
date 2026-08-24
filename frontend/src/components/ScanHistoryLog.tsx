"use client";

import React from "react";
import { History, Trash2 } from "lucide-react";
import { ScanRecord } from "../types/telemetry";

interface ScanHistoryLogProps {
  history: ScanRecord[];
  onClearHistory: () => void;
}

export const ScanHistoryLog: React.FC<ScanHistoryLogProps> = ({
  history,
  onClearHistory,
}) => {
  const formatClassName = (name: string) => {
    return name
      .replace(/___/g, " — ")
      .replace(/_/g, " ")
      .replace(/Tomato/g, "Tomato");
  };

  const getBadgeClass = (className: string) => {
    return className.toLowerCase().includes("healthy") ? "badge low" : "badge high";
  };

  return (
    <section className="glass-panel history-panel">
      <div className="panel-header-row">
        <div>
          <h2 style={{ display: "flex", alignItems: "center", gap: "0.45rem" }}>
            <History size={18} className="text-emerald-600" />
            AI Vision Inspection Log &amp; Pathology Timeline
          </h2>
          <span className="analytics-sub">
            Saved diagnostic records and treatment verification timeline
          </span>
        </div>
        {history.length > 0 && (
          <button id="clear-history-btn" className="btn-ghost" onClick={onClearHistory} style={{ display: "inline-flex", alignItems: "center", gap: "0.3rem" }}>
            <Trash2 size={12} />
            Clear Log
          </button>
        )}
      </div>

      <div
        id="scan-history-container"
        className={`history-grid ${history.length === 0 ? "empty" : ""}`}
      >
        {history.length > 0 ? (
          history.map((record) => (
            <div className="history-card" key={record.id}>
              {record.thumbnail && (
                <img
                  src={record.thumbnail}
                  className="history-thumb"
                  alt="Snapshot"
                />
              )}
              <div className="history-details">
                <div className="history-title-row">
                  <span className="history-disease">
                    {formatClassName(record.predicted_class)}
                  </span>
                  <span className={getBadgeClass(record.predicted_class)}>
                    {(record.confidence * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="history-time">{record.dateStr}</div>
                <p className="history-summary">{record.summary}</p>
              </div>
            </div>
          ))
        ) : (
          <div className="history-empty-placeholder">
            No plant inspection snapshots saved yet. Capture and analyze leaves to build your crop health timeline.
          </div>
        )}
      </div>
    </section>
  );
};
