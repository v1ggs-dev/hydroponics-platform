"use client";

import React, { useEffect, useRef, useState } from "react";
import {
  Chart,
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";

import { TrendingUp } from "lucide-react";

// Register Chart.js components
Chart.register(
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface AnalyticsChartsProps {
  currentRange: string;
  onRangeChange: (range: string) => void;
  historicalData: any[] | null;
}

export const AnalyticsCharts: React.FC<AnalyticsChartsProps> = ({
  currentRange,
  onRangeChange,
  historicalData,
}) => {
  const waterCanvasRef = useRef<HTMLCanvasElement>(null);
  const climateCanvasRef = useRef<HTMLCanvasElement>(null);

  const waterChartRef = useRef<Chart | null>(null);
  const climateChartRef = useRef<Chart | null>(null);

  useEffect(() => {
    // Initialize Water Chart
    if (waterCanvasRef.current) {
      if (waterChartRef.current) waterChartRef.current.destroy();
      const ctx = waterCanvasRef.current.getContext("2d");
      if (ctx) {
        waterChartRef.current = new Chart(ctx, {
          type: "line",
          data: {
            labels: [],
            datasets: [
              {
                label: "TDS (ppm)",
                data: [],
                borderColor: "#0284c7",
                backgroundColor: "rgba(2, 132, 199, 0.08)",
                fill: true,
                tension: 0.35,
                borderWidth: 2.5,
                yAxisID: "yTds",
                pointRadius: 2,
                pointHoverRadius: 5,
              },
              {
                label: "pH Level",
                data: [],
                borderColor: "#8b5cf6",
                backgroundColor: "transparent",
                borderDash: [4, 4],
                tension: 0.35,
                borderWidth: 2.5,
                yAxisID: "yPh",
                pointRadius: 2,
                pointHoverRadius: 5,
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: "index", intersect: false },
            plugins: {
              legend: {
                position: "top",
                align: "end",
                labels: { boxWidth: 12, usePointStyle: true },
              },
            },
            scales: {
              x: { grid: { display: false } },
              yTds: {
                type: "linear",
                position: "left",
                min: 0,
                max: 1800,
                grid: { color: "rgba(226, 232, 240, 0.6)" },
                title: { display: true, text: "TDS (ppm)", font: { weight: "bold" } },
              },
              yPh: {
                type: "linear",
                position: "right",
                min: 4.0,
                max: 8.5,
                grid: { display: false },
                title: { display: true, text: "pH", font: { weight: "bold" } },
              },
            },
          },
        });
      }
    }

    // Initialize Climate Chart
    if (climateCanvasRef.current) {
      if (climateChartRef.current) climateChartRef.current.destroy();
      const ctx = climateCanvasRef.current.getContext("2d");
      if (ctx) {
        climateChartRef.current = new Chart(ctx, {
          type: "line",
          data: {
            labels: [],
            datasets: [
              {
                label: "Air Temp (°C)",
                data: [],
                borderColor: "#10b981",
                backgroundColor: "rgba(16, 185, 129, 0.08)",
                fill: true,
                tension: 0.35,
                borderWidth: 2.5,
                yAxisID: "yTemp",
                pointRadius: 2,
                pointHoverRadius: 5,
              },
              {
                label: "Humidity (%)",
                data: [],
                borderColor: "#06b6d4",
                backgroundColor: "transparent",
                borderDash: [4, 4],
                tension: 0.35,
                borderWidth: 2.5,
                yAxisID: "yHum",
                pointRadius: 2,
                pointHoverRadius: 5,
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: "index", intersect: false },
            plugins: {
              legend: {
                position: "top",
                align: "end",
                labels: { boxWidth: 12, usePointStyle: true },
              },
            },
            scales: {
              x: { grid: { display: false } },
              yTemp: {
                type: "linear",
                position: "left",
                min: 10,
                max: 40,
                grid: { color: "rgba(226, 232, 240, 0.6)" },
                title: { display: true, text: "Temp (°C)", font: { weight: "bold" } },
              },
              yHum: {
                type: "linear",
                position: "right",
                min: 20,
                max: 100,
                grid: { display: false },
                title: { display: true, text: "Humidity (%)", font: { weight: "bold" } },
              },
            },
          },
        });
      }
    }

    return () => {
      if (waterChartRef.current) waterChartRef.current.destroy();
      if (climateChartRef.current) climateChartRef.current.destroy();
    };
  }, []);

  // Update chart data whenever historicalData changes
  useEffect(() => {
    let labels: string[] = [];
    let tdsData: number[] = [];
    let phData: number[] = [];
    let tempData: number[] = [];
    let humData: number[] = [];

    if (historicalData && historicalData.length > 0) {
      // Group by timestamp or step
      historicalData.forEach((rec) => {
        const timeLabel = new Date(rec.timestamp).toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        });
        if (!labels.includes(timeLabel)) labels.push(timeLabel);

        if (rec.metric === "tds") tdsData.push(rec.value);
        if (rec.metric === "ph") phData.push(rec.value);
        if (rec.metric === "air_temperature") tempData.push(rec.value);
        if (rec.metric === "humidity") humData.push(rec.value);
      });
    } else {
      // Generate standard baseline curves
      const now = Date.now();
      const points = 12;
      for (let i = points; i >= 0; i--) {
        const t = new Date(now - i * 5 * 60 * 1000);
        labels.push(t.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }));
        tdsData.push(850 + Math.sin(i * 0.5) * 40);
        phData.push(6.0 + Math.cos(i * 0.5) * 0.2);
        tempData.push(24.5 + Math.sin(i * 0.4) * 1.5);
        humData.push(62.0 + Math.cos(i * 0.4) * 4.0);
      }
    }

    if (waterChartRef.current) {
      waterChartRef.current.data.labels = labels;
      waterChartRef.current.data.datasets[0].data = tdsData;
      waterChartRef.current.data.datasets[1].data = phData;
      waterChartRef.current.update();
    }

    if (climateChartRef.current) {
      climateChartRef.current.data.labels = labels;
      climateChartRef.current.data.datasets[0].data = tempData;
      climateChartRef.current.data.datasets[1].data = humData;
      climateChartRef.current.update();
    }
  }, [historicalData]);

  const ranges = ["1h", "6h", "24h", "7d"];

  return (
    <section className="glass-panel analytics-panel">
      <div className="analytics-header">
        <div>
          <h2 style={{ display: "flex", alignItems: "center", gap: "0.45rem" }}>
            <TrendingUp size={18} className="text-emerald-600" />
            Telemetry Analytics &amp; Trend History
          </h2>
          <span className="analytics-sub">
            Correlated real-time data curves &amp; optimal growth zones
          </span>
        </div>
        <div className="time-filter-buttons">
          {ranges.map((r) => (
            <button
              key={r}
              className={`time-btn ${currentRange === r ? "active" : ""}`}
              onClick={() => onRangeChange(r)}
            >
              {r === "1h" ? "1 Hour" : r === "6h" ? "6 Hours" : r === "24h" ? "24 Hours" : "7 Days"}
            </button>
          ))}
        </div>
      </div>

      <div className="charts-grid">
        {/* Water Chemistry Chart */}
        <div className="chart-container-card">
          <div className="chart-card-title">
            <span>Water Chemistry: TDS (ppm) vs pH Balance</span>
            <span className="chart-legend-badge">Dual-Axis</span>
          </div>
          <div className="canvas-wrapper">
            <canvas ref={waterCanvasRef} id="waterChemistryChart"></canvas>
          </div>
        </div>

        {/* Climate Environment Chart */}
        <div className="chart-container-card">
          <div className="chart-card-title">
            <span>Climate Environment: Temperature vs Humidity</span>
            <span className="chart-legend-badge">Dynamic Curve</span>
          </div>
          <div className="canvas-wrapper">
            <canvas ref={climateCanvasRef} id="climateChart"></canvas>
          </div>
        </div>
      </div>
    </section>
  );
};
