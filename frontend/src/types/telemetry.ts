export interface Measurement {
  sensorId: string;
  metric: string;
  value: number;
  unit: string;
  quality: "GOOD" | "BAD" | "SUSPECT";
  timestamp?: string;
}

export interface LatestTelemetryMap {
  [metric: string]: {
    value: number;
    unit: string;
    quality?: string;
    sensorId?: string;
    deviceId?: string;
    timestamp?: string;
  };
}

export interface PredictionClass {
  class: string;
  confidence: number;
}

export interface VisionClassificationResult {
  model_version?: string;
  crop?: string;
  predicted_class: string;
  confidence: number;
  top_k: PredictionClass[];
}

export interface RecommendationAction {
  action: string;
  reason: string;
  source_ids?: string[];
}

export interface AgronomicRecommendation {
  priority: "high" | "medium" | "low" | string;
  summary: string;
  actions: RecommendationAction[];
  warnings?: string[];
}

export interface ScanRecord {
  id: string;
  timestamp: string;
  dateStr: string;
  thumbnail: string;
  predicted_class: string;
  confidence: number;
  priority: string;
  summary: string;
}

export interface DeviceInfo {
  id: string;
  name: string;
  status: "ONLINE" | "OFFLINE";
  lastSeenAt: string;
}

export interface HistoricalRecord {
  id: number | string;
  sensorId: string;
  metric: string;
  value: number;
  unit: string;
  timestamp: string;
}

export interface AlertItem {
  id: number | string;
  deviceId: string;
  type: string;
  severity: "INFO" | "WARNING" | "CRITICAL";
  message: string;
  resolved: boolean;
  createdAt: string;
  resolvedAt?: string;
}

export interface EdgeHealth {
  gatewayId: string;
  serialPort: string;
  serialConnected: boolean;
  cpuPercent: number;
  ramPercent: number;
  pendingBufferedRecords: number;
  timestamp: string;
}
