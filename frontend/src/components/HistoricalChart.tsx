"use client";

import React, { useEffect, useState } from "react";
import ReactECharts from "echarts-for-react";
import { fetchTelemetryHistory } from "../lib/api";
import { LineChart, Clock } from "lucide-react";

type TimeRange = "1h" | "6h" | "24h" | "7d";
type MetricTab = "all" | "environment" | "nutrients" | "flow";

export function HistoricalChart() {
  const [range, setRange] = useState<TimeRange>("24h");
  const [activeTab, setActiveTab] = useState<MetricTab>("all");
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function loadHistory() {
      setLoading(true);
      const res = await fetchTelemetryHistory("all", undefined, range);
      if (res?.success && res.data) {
        setData(res.data);
      }
      setLoading(false);
    }
    loadHistory();
  }, [range]);

  // Group measurements by timestamp
  const timeMap = new Map<string, Record<string, number>>();
  data.forEach((item) => {
    const timeStr = new Date(item.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    if (!timeMap.has(timeStr)) {
      timeMap.set(timeStr, {});
    }
    timeMap.get(timeStr)![item.metric] = item.value;
  });

  const timestamps = Array.from(timeMap.keys());
  const tempData = timestamps.map((t) => timeMap.get(t)?.["air_temperature"] ?? null);
  const humData = timestamps.map((t) => timeMap.get(t)?.["humidity"] ?? null);
  const phData = timestamps.map((t) => timeMap.get(t)?.["ph"] ?? null);
  const tdsData = timestamps.map((t) => timeMap.get(t)?.["tds"] ?? null);
  const moistData = timestamps.map((t) => timeMap.get(t)?.["substrate_moisture"] ?? null);
  const flowData = timestamps.map((t) => timeMap.get(t)?.["flow_rate"] ?? null);

  // Configure series based on active tab
  const series: any[] = [];

  if (activeTab === "all" || activeTab === "environment") {
    series.push({
      name: "Air Temp (°C)",
      type: "line",
      smooth: true,
      showSymbol: false,
      data: tempData,
      itemStyle: { color: "#F87171" },
      areaStyle: {
        color: {
          type: "linear",
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [{ offset: 0, color: "rgba(248, 113, 113, 0.25)" }, { offset: 1, color: "rgba(248, 113, 113, 0.0)" }],
        },
      },
    });
    series.push({
      name: "Humidity (%)",
      type: "line",
      smooth: true,
      showSymbol: false,
      data: humData,
      itemStyle: { color: "#38BDF8" },
      areaStyle: {
        color: {
          type: "linear",
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [{ offset: 0, color: "rgba(56, 189, 248, 0.25)" }, { offset: 1, color: "rgba(56, 189, 248, 0.0)" }],
        },
      },
    });
  }

  if (activeTab === "all" || activeTab === "nutrients") {
    series.push({
      name: "Solution pH",
      type: "line",
      smooth: true,
      showSymbol: false,
      data: phData,
      itemStyle: { color: "#E879F9" },
    });
    series.push({
      name: "TDS (ppm)",
      type: "line",
      smooth: true,
      showSymbol: false,
      yAxisIndex: activeTab === "all" ? 1 : 0,
      data: tdsData,
      itemStyle: { color: "#34D399" },
    });
    series.push({
      name: "Moisture (%)",
      type: "line",
      smooth: true,
      showSymbol: false,
      data: moistData,
      itemStyle: { color: "#FBBF24" },
    });
  }

  if (activeTab === "all" || activeTab === "flow") {
    series.push({
      name: "Flow (L/min)",
      type: "line",
      smooth: true,
      showSymbol: false,
      data: flowData,
      itemStyle: { color: "#60A5FA" },
    });
  }

  const option = {
    backgroundColor: "transparent",
    tooltip: {
      trigger: "axis",
      backgroundColor: "#181B26",
      borderColor: "#232838",
      textStyle: { color: "#F1F5F9", fontFamily: "Inter, sans-serif", fontSize: 12 },
    },
    legend: {
      textStyle: { color: "#8E99B0", fontFamily: "Inter, sans-serif" },
      bottom: 0,
    },
    grid: {
      left: "3%",
      right: "4%",
      bottom: "12%",
      top: "8%",
      containLabel: true,
    },
    xAxis: {
      type: "category",
      boundaryGap: false,
      data: timestamps.length > 0 ? timestamps : ["No Data"],
      axisLine: { lineStyle: { color: "#232838" } },
      axisLabel: { color: "#8E99B0", fontFamily: "JetBrains Mono" },
    },
    yAxis: [
      {
        type: "value",
        splitLine: { lineStyle: { color: "#181B26" } },
        axisLabel: { color: "#8E99B0", fontFamily: "JetBrains Mono" },
      },
      activeTab === "all"
        ? {
            type: "value",
            splitLine: { show: false },
            axisLabel: { color: "#34D399", fontFamily: "JetBrains Mono" },
          }
        : null,
    ].filter(Boolean),
    series: series.length > 0 ? series : [{ type: "line", data: [] }],
  };

  return (
    <div className="rounded-xl border border-border bg-surface p-5">
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-border/60">
        <div className="flex items-center gap-2">
          <LineChart className="w-5 h-5 text-emerald-400" />
          <h2 className="text-sm font-semibold text-textPrimary uppercase tracking-wider">
            Historical Sensor Telemetry
          </h2>
          <span className="text-xs font-mono text-textMuted">({data.length} datapoints)</span>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-2">
          {/* Tab selector */}
          <div className="flex items-center bg-background/60 p-1 rounded-lg border border-border">
            {(["all", "environment", "nutrients", "flow"] as MetricTab[]).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-2.5 py-1 text-xs font-medium rounded-md capitalize transition-colors ${
                  activeTab === tab
                    ? "bg-surfaceLight text-textPrimary border border-border"
                    : "text-textMuted hover:text-textPrimary"
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          {/* Time range selector */}
          <div className="flex items-center bg-background/60 p-1 rounded-lg border border-border">
            {(["1h", "6h", "24h", "7d"] as TimeRange[]).map((r) => (
              <button
                key={r}
                onClick={() => setRange(r)}
                className={`px-2.5 py-1 text-xs font-mono font-medium rounded-md uppercase transition-colors ${
                  range === r
                    ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                    : "text-textMuted hover:text-textPrimary"
                }`}
              >
                {r}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Chart Canvas */}
      <div className="mt-4 h-72 sm:h-80 w-full">
        {loading ? (
          <div className="h-full flex items-center justify-center text-textMuted font-mono text-xs">
            Loading time-series records from Supabase...
          </div>
        ) : (
          <ReactECharts option={option} style={{ height: "100%", width: "100%" }} notMerge={true} />
        )}
      </div>
    </div>
  );
}
