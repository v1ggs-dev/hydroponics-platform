"use client";

import React from "react";
import { BookOpen, AlertTriangle, ClipboardList } from "lucide-react";
import { AgronomicRecommendation } from "../types/telemetry";

interface AgronomicRecommendationsProps {
  recommendation: AgronomicRecommendation | null;
}

export const AgronomicRecommendations: React.FC<AgronomicRecommendationsProps> = ({
  recommendation,
}) => {
  const getPriorityClass = (priority: string | undefined) => {
    if (priority === "high") return "badge high";
    if (priority === "medium") return "badge medium";
    return "badge low";
  };

  return (
    <section className="recommendation-section glass-panel">
      <h2 style={{ display: "flex", alignItems: "center", gap: "0.45rem" }}>
        <ClipboardList size={18} className="text-emerald-600" />
        Agronomic Pathology Recommendations
      </h2>
      <div
        id="recommendation-content"
        className={`recommendation-content ${recommendation ? "" : "empty"}`}
      >
        {recommendation ? (
          <div>
            <div className="recommendation-header">
              <h3>Diagnostic Evaluation & Treatment Protocol</h3>
              <span className={getPriorityClass(recommendation.priority)}>
                {(recommendation.priority || "NORMAL").toUpperCase()} PRIORITY
              </span>
            </div>
            <p className="summary-text">{recommendation.summary}</p>

            {recommendation.actions && recommendation.actions.length > 0 && (
              <div className="actions-list">
                <h4>Prescribed Agronomic Actions:</h4>
                {recommendation.actions.map((act, idx) => (
                  <div className="action-item" key={idx}>
                    <div className="action-num">{idx + 1}</div>
                    <div className="action-details">
                      <div className="action-title">{act.action}</div>
                      <div className="action-reason">
                        <strong>Why:</strong> {act.reason}
                      </div>
                      {act.source_ids && act.source_ids.length > 0 && (
                        <div className="source-tags">
                          {act.source_ids.map((s, sIdx) => (
                            <span className="source-tag" key={sIdx} style={{ display: "inline-flex", alignItems: "center", gap: "0.25rem" }}>
                              <BookOpen size={11} className="text-sky-600" />
                              {s}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {recommendation.warnings && recommendation.warnings.length > 0 && (
              <div className="warnings-box">
                <h4 style={{ display: "flex", alignItems: "center", gap: "0.35rem" }}>
                  <AlertTriangle size={15} className="text-amber-600" />
                  Warnings & Environmental Safeguards:
                </h4>
                <ul>
                  {recommendation.warnings.map((w, wIdx) => (
                    <li key={wIdx}>{w}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ) : (
          <p className="placeholder-text">
            Expert treatment protocols and bio-nutrient recommendations will appear here after analysis.
          </p>
        )}
      </div>
    </section>
  );
};
