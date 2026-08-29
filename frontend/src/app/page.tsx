"use client";

import React, { useState, useEffect } from "react";
import { Header } from "../components/Header";
import { FloatingNav } from "../components/FloatingNav";
import { TelemetryPanel } from "../components/TelemetryPanel";
import { OpticalFeedScanner } from "../components/OpticalFeedScanner";
import { AgronomicRecommendations } from "../components/AgronomicRecommendations";
import { HealthAndVPDCard } from "../components/HealthAndVPDCard";
import { IoTControlSwitchboard } from "../components/IoTControlSwitchboard";
import { AnalyticsCharts } from "../components/AnalyticsCharts";
import { ScanHistoryLog } from "../components/ScanHistoryLog";
import {
  LatestTelemetryMap,
  VisionClassificationResult,
  AgronomicRecommendation,
  ScanRecord,
} from "../types/telemetry";
import { getApiBaseUrl, getAiBaseUrl } from "../lib/api";

export default function AgroEyeDashboard() {
  const API_IOT = getApiBaseUrl();
  const API_AI = getAiBaseUrl();
  const [activeView, setActiveView] = useState<"main" | "analytics">("main");
  const [aiStatus, setAiStatus] = useState<"online" | "offline" | "loading">("loading");
  const [iotStatus, setIotStatus] = useState<"online" | "offline" | "loading">("loading");

  const [telemetry, setTelemetry] = useState<LatestTelemetryMap | null>(null);
  const [isOnline, setIsOnline] = useState(false);
  const [lastSyncedAt, setLastSyncedAt] = useState<string>("Syncing...");

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [classificationResult, setClassificationResult] = useState<VisionClassificationResult | null>(null);
  const [recommendation, setRecommendation] = useState<AgronomicRecommendation | null>(null);

  const [isPumpRunning, setIsPumpRunning] = useState(false);
  const [isAutoEnabled, setIsAutoEnabled] = useState(true);
  const [feedbackMessage, setFeedbackMessage] = useState("Ready to dispatch MQTT commands to esp32-env");

  const [currentRange, setCurrentRange] = useState("1h");
  const [historicalData, setHistoricalData] = useState<any[] | null>(null);
  const [scanHistory, setScanHistory] = useState<ScanRecord[]>([]);

  // 1. Initial Load & Intervals
  useEffect(() => {
    checkHealth();
    fetchSensors();
    fetchChartHistory(currentRange);
    loadScanHistory();

    const sensorInterval = setInterval(fetchSensors, 4000);
    const healthInterval = setInterval(checkHealth, 15000);
    const historyInterval = setInterval(() => fetchChartHistory(currentRange), 30000);

    return () => {
      clearInterval(sensorInterval);
      clearInterval(healthInterval);
      clearInterval(historyInterval);
    };
  }, []);

  // 2. Health check
  const checkHealth = async () => {
    try {
      const res = await fetch(`${API_AI}/health`);
      setAiStatus(res.ok ? "online" : "offline");
    } catch {
      setAiStatus("offline");
    }

    try {
      const res = await fetch(`${API_IOT}/health`);
      setIotStatus(res.ok ? "online" : "offline");
    } catch {
      setIotStatus("offline");
    }
  };

  // 3. Fetch Sensors
  const fetchSensors = async () => {
    try {
      const res = await fetch(`${API_IOT}/telemetry/latest?deviceId=all`);
      if (!res.ok) throw new Error("API Error");
      const json = await res.json();

      if (json.success && json.data && Object.keys(json.data).length > 0) {
        const now = new Date().getTime();
        let fresh = false;

        for (const key in json.data) {
          if (json.data[key]?.timestamp) {
            const readingTime = new Date(json.data[key].timestamp).getTime();
            if ((now - readingTime) / 1000 < 60) {
              fresh = true;
              break;
            }
          }
        }

        setTelemetry(json.data);
        setIsOnline(fresh);
        setLastSyncedAt(new Date().toLocaleTimeString());
      } else {
        setIsOnline(false);
      }
    } catch {
      setIsOnline(false);
    }
  };

  // 4. Fetch History
  const fetchChartHistory = async (range: string) => {
    try {
      const res = await fetch(`${API_IOT}/telemetry/history?range=${range}&deviceId=all&limit=200`);
      if (res.ok) {
        const json = await res.json();
        if (json.success && Array.isArray(json.data)) {
          setHistoricalData(json.data);
        }
      }
    } catch (err) {
      console.warn("Could not fetch historical data:", err);
    }
  };

  // 5. Scan History Storage
  const loadScanHistory = () => {
    try {
      const saved = localStorage.getItem("agroeye_scan_history");
      if (saved) {
        setScanHistory(JSON.parse(saved));
      }
    } catch (e) {
      console.warn("Error reading localStorage scan history:", e);
    }
  };

  const handleClearHistory = () => {
    if (confirm("Clear all saved plant inspection scans?")) {
      localStorage.removeItem("agroeye_scan_history");
      setScanHistory([]);
    }
  };

  // 6. 1-Click AI Analysis
  const handleAnalyze = async (blob: Blob, dataUrl: string, filename?: string) => {
    setIsAnalyzing(true);
    try {
      const formData = new FormData();
      formData.append("file", blob, filename || "leaf_snapshot.jpg");

      const res = await fetch(`${API_AI}/api/v1/recommendation/generate`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("AI Service inference failed");
      const json = await res.json();

      if (json.vision) {
        setClassificationResult(json.vision);
      }
      if (json.recommendation) {
        setRecommendation(json.recommendation);
      }

      // Save to history log
      const newRecord: ScanRecord = {
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        dateStr: new Date().toLocaleString(),
        thumbnail: dataUrl,
        predicted_class: json.vision?.predicted_class || "Unknown",
        confidence: json.vision?.confidence || 0,
        priority: json.recommendation?.priority || "Normal",
        summary: json.recommendation?.summary || "Completed pathology analysis.",
      };

      const updatedHistory = [newRecord, ...scanHistory].slice(0, 15);
      setScanHistory(updatedHistory);
      localStorage.setItem("agroeye_scan_history", JSON.stringify(updatedHistory));
    } catch (err: any) {
      alert(`AI Analysis Error: ${err.message || "Could not reach AgroEye AI server"}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // 7. Actuator Commands
  const handleSendCommand = async (action: string, value?: string): Promise<boolean> => {
    setFeedbackMessage(`Dispatching command: ${action} ${value || ""}...`);
    try {
      const payload = {
        deviceId: "esp32-env",
        actuatorId: "pump-01",
        action,
        value: value || undefined,
      };

      const res = await fetch(`${API_IOT}/commands`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (res.ok && data.success) {
        setFeedbackMessage(`✅ Successfully sent ${action} to esp32-env`);
        if (action === "SET_STATE") {
          setIsPumpRunning(value === "ON");
        } else if (action === "AUTO_ON") {
          setIsAutoEnabled(true);
        } else if (action === "AUTO_OFF") {
          setIsAutoEnabled(false);
        }
        return true;
      } else {
        setFeedbackMessage(`⚠️ Command rejected: ${data.message || "Error"}`);
        return false;
      }
    } catch {
      setFeedbackMessage(`❌ Network Error: Could not reach backend`);
      return false;
    }
  };

  const handleSwitchView = (view: "main" | "analytics") => {
    setActiveView(view);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div className="flex flex-col min-h-screen">
      {/* Header */}
      <Header
        activeView={activeView}
        onSwitchView={handleSwitchView}
        aiStatus={aiStatus}
        iotStatus={iotStatus}
      />

      {/* Floating Navigation Pill */}
      <FloatingNav activeView={activeView} onSwitchView={handleSwitchView} />

      {/* Sliding Viewport */}
      <div className="slider-viewport">
        <div
          id="slider-track"
          className={`slider-track ${
            activeView === "analytics" ? "view-analytics-active" : "view-main-active"
          }`}
        >
          {/* VIEW 1: LIVE OVERVIEW */}
          <div className="slider-page" id="page-main">
            <div className="page-content">
              {/* 1. Telemetry Cards */}
              <TelemetryPanel
                telemetry={telemetry}
                isOnline={isOnline}
                lastSyncedAt={lastSyncedAt}
              />

              {/* 2. Optical Feed & AI Classifier */}
              <OpticalFeedScanner
                onAnalyze={handleAnalyze}
                isAnalyzing={isAnalyzing}
                classificationResult={classificationResult}
              />

              {/* 3. Agronomic Recommendations */}
              <AgronomicRecommendations recommendation={recommendation} />
            </div>
          </div>

          {/* VIEW 2: ANALYTICS & IOT CONTROL HUB */}
          <div className="slider-page" id="page-analytics">
            <div className="page-content">
              {/* Dual Row: Health & VPD + IoT Control Switchboard */}
              <div className="dashboard-dual-row">
                <HealthAndVPDCard telemetry={telemetry} isOnline={isOnline} />
                <IoTControlSwitchboard
                  onSendCommand={handleSendCommand}
                  isPumpRunning={isPumpRunning}
                  isAutoEnabled={isAutoEnabled}
                  feedbackMessage={feedbackMessage}
                />
              </div>

              {/* Interactive Analytics Charts */}
              <AnalyticsCharts
                currentRange={currentRange}
                onRangeChange={(range) => {
                  setCurrentRange(range);
                  fetchChartHistory(range);
                }}
                historicalData={historicalData}
              />

              {/* AI Vision Inspection History Log */}
              <ScanHistoryLog
                history={scanHistory}
                onClearHistory={handleClearHistory}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="footer">
        <p>
          AgroEye AI Ecosystem &copy; 2026 — Distributed Hydroponics IoT Controller & Neural Pathology Engine
        </p>
      </footer>
    </div>
  );
}
