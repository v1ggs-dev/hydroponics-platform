"use client";

import React from "react";
import { ArrowRight, ArrowLeft } from "lucide-react";

interface FloatingNavProps {
  activeView: "main" | "analytics";
  onSwitchView: (view: "main" | "analytics") => void;
}

export const FloatingNav: React.FC<FloatingNavProps> = ({
  activeView,
  onSwitchView,
}) => {
  return (
    <>
      {/* Floating Right Arrow Tab (Navigates to Analytics View) */}
      <button
        id="float-to-analytics-btn"
        className={`floating-nav-btn right-nav ${activeView === "analytics" ? "hidden" : ""}`}
        title="Open Analytics & IoT Controls"
        onClick={() => onSwitchView("analytics")}
      >
        <div className="nav-btn-content">
          <span className="nav-btn-text">Analytics</span>
          <ArrowRight size={14} className="nav-arrow-icon" />
        </div>
      </button>

      {/* Floating Left Arrow Tab (Navigates back to Main View) */}
      <button
        id="float-to-main-btn"
        className={`floating-nav-btn left-nav ${activeView === "main" ? "hidden" : ""}`}
        title="Back to Live Overview"
        onClick={() => onSwitchView("main")}
      >
        <div className="nav-btn-content">
          <ArrowLeft size={14} className="nav-arrow-icon" />
          <span className="nav-btn-text">Overview</span>
        </div>
      </button>
    </>
  );
};
