"use client";

import React, { useRef, useState, useEffect } from "react";
import { 
  Globe, 
  Camera, 
  UploadCloud, 
  FolderOpen, 
  Smartphone, 
  Cpu, 
  Video, 
  CheckCircle2, 
  AlertCircle, 
  AlertTriangle, 
  Bug, 
  CircleDot, 
  Target, 
  RotateCcw,
  Sparkles,
  Eye
} from "lucide-react";
import { VisionClassificationResult } from "../types/telemetry";

interface OpticalFeedScannerProps {
  onAnalyze: (imageBlob: Blob, dataUrl: string, filename?: string) => Promise<void>;
  isAnalyzing: boolean;
  classificationResult: VisionClassificationResult | null;
}

type CameraSourceMode = "upload" | "ip" | "webcam";

export const OpticalFeedScanner: React.FC<OpticalFeedScannerProps> = ({
  onAnalyze,
  isAnalyzing,
  classificationResult,
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [mode, setMode] = useState<CameraSourceMode>("upload");
  const [ipUrl, setIpUrl] = useState<string>("http://10.13.14.68:8080/video");
  const [streamSrc, setStreamSrc] = useState<string>("http://10.13.14.68:8080/video");
  const [hasSnapshot, setHasSnapshot] = useState(false);
  const [previewSrc, setPreviewSrc] = useState<string | null>(null);
  const [currentFilename, setCurrentFilename] = useState<string>("leaf_snapshot.jpg");
  const [streamActive, setStreamActive] = useState(false);
  const [ipLoading, setIpLoading] = useState(false);
  const [useProxy, setUseProxy] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);

  // Load saved IP Camera URL from localStorage
  useEffect(() => {
    try {
      const savedIp = localStorage.getItem("agroeye_ip_cam_url");
      if (savedIp) {
        setIpUrl(savedIp);
        setStreamSrc(savedIp);
      }
    } catch {
      // Ignored
    }
  }, []);

  useEffect(() => {
    if (mode === "webcam") {
      startWebcam();
    } else {
      stopWebcam();
    }
    return () => {
      stopWebcam();
    };
  }, [mode]);

  const handleApplyIp = (newUrl: string) => {
    setIpUrl(newUrl);
    setStreamSrc(newUrl);
    setUseProxy(false);
    try {
      localStorage.setItem("agroeye_ip_cam_url", newUrl);
    } catch {
      // Ignored
    }
  };

  const startWebcam = async () => {
    try {
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "environment", width: { ideal: 1280 }, height: { ideal: 720 } },
          audio: false,
        });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.muted = true;
          videoRef.current.setAttribute("playsinline", "true");
          videoRef.current.onloadedmetadata = () => {
            videoRef.current?.play().catch((err) => console.warn("Autoplay notice:", err));
          };
          try {
            await videoRef.current.play();
          } catch {
            // Ignored
          }
          setStreamActive(true);
        }
      }
    } catch (err) {
      console.warn("Webcam access error or denied:", err);
      setMode("upload");
    }
  };

  const stopWebcam = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach((t) => t.stop());
      videoRef.current.srcObject = null;
      setStreamActive(false);
    }
  };

  const captureFrame = async () => {
    if (mode === "webcam") {
      if (!videoRef.current || !canvasRef.current) return;
      const video = videoRef.current;
      const canvas = canvasRef.current;
      canvas.width = video.videoWidth || 640;
      canvas.height = video.videoHeight || 480;

      const ctx = canvas.getContext("2d");
      if (ctx) {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const dataUrl = canvas.toDataURL("image/jpeg", 0.9);
        setPreviewSrc(dataUrl);
        setHasSnapshot(true);

        canvas.toBlob((blob) => {
          if (blob) {
            onAnalyze(blob, dataUrl, "camera_capture.jpg");
          }
        }, "image/jpeg", 0.9);
      }
    } else if (mode === "ip") {
      setIpLoading(true);
      try {
        const proxyUrl = `http://localhost:8000/api/v1/recommendation/proxy-frame?url=${encodeURIComponent(ipUrl)}`;
        const res = await fetch(proxyUrl);
        if (!res.ok) throw new Error("Could not fetch frame from IP camera");
        
        const blob = await res.blob();
        const reader = new FileReader();
        reader.onloadend = () => {
          const dataUrl = reader.result as string;
          setPreviewSrc(dataUrl);
          setHasSnapshot(true);
          setIpLoading(false);
          onAnalyze(blob, dataUrl, "ip_camera_scan.jpg");
        };
        reader.readAsDataURL(blob);
      } catch (err) {
        setIpLoading(false);
        alert(`Could not grab snapshot from ${ipUrl}. Ensure phone/camera is on the same Wi-Fi.`);
      }
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    processFile(file);
  };

  const processFile = (file: File) => {
    setCurrentFilename(file.name);
    const reader = new FileReader();
    reader.onload = (event) => {
      const dataUrl = event.target?.result as string;
      setPreviewSrc(dataUrl);
      setHasSnapshot(true);
      onAnalyze(file, dataUrl, file.name);
    };
    reader.readAsDataURL(file);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) {
      processFile(file);
    }
  };

  const resetCamera = () => {
    setHasSnapshot(false);
    setPreviewSrc(null);
  };

  const formatClassName = (name: string) => {
    return name
      .replace(/___/g, " — ")
      .replace(/_/g, " ")
      .replace(/Tomato/g, "Tomato");
  };

  const isHealthy = classificationResult?.predicted_class.toLowerCase().includes("healthy");
  const confidencePct = classificationResult ? (classificationResult.confidence * 100).toFixed(1) : "0";

  const currentStreamUrl = useProxy
    ? `http://localhost:8000/api/v1/recommendation/stream-proxy?url=${encodeURIComponent(ipUrl)}`
    : streamSrc;

  return (
    <div className="main-content">
      {/* Left: Camera Feed & Image Uploader */}
      <section className="upload-section glass-panel">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.85rem", flexWrap: "wrap", gap: "0.5rem" }}>
          <h2 style={{ display: "flex", alignItems: "center", gap: "0.45rem" }}>
            <Eye size={18} className="text-emerald-600" />
            Plant Pathology Optical Feed
          </h2>
          
          {/* Camera Source Selector */}
          <div style={{ display: "flex", gap: "0.25rem", background: "#f1f5f9", padding: "0.2rem", borderRadius: "999px", border: "1px solid #e2e8f0" }}>
            <button
              onClick={() => setMode("upload")}
              style={{
                background: mode === "upload" ? "#ffffff" : "transparent",
                color: mode === "upload" ? "#0f172a" : "#64748b",
                border: "none",
                borderRadius: "999px",
                padding: "0.35rem 0.75rem",
                fontSize: "0.75rem",
                fontWeight: 600,
                cursor: "pointer",
                boxShadow: mode === "upload" ? "0 1px 2px rgba(0,0,0,0.05)" : "none",
                display: "inline-flex",
                alignItems: "center",
                gap: "0.3rem",
                transition: "all 0.15s ease"
              }}
            >
              <UploadCloud size={13} />
              Upload Photo
            </button>
            <button
              onClick={() => setMode("ip")}
              style={{
                background: mode === "ip" ? "#ffffff" : "transparent",
                color: mode === "ip" ? "#0f172a" : "#64748b",
                border: "none",
                borderRadius: "999px",
                padding: "0.35rem 0.75rem",
                fontSize: "0.75rem",
                fontWeight: 600,
                cursor: "pointer",
                boxShadow: mode === "ip" ? "0 1px 2px rgba(0,0,0,0.05)" : "none",
                display: "inline-flex",
                alignItems: "center",
                gap: "0.3rem",
                transition: "all 0.15s ease"
              }}
            >
              <Globe size={13} />
              IP Camera
            </button>
            <button
              onClick={() => setMode("webcam")}
              style={{
                background: mode === "webcam" ? "#ffffff" : "transparent",
                color: mode === "webcam" ? "#0f172a" : "#64748b",
                border: "none",
                borderRadius: "999px",
                padding: "0.35rem 0.75rem",
                fontSize: "0.75rem",
                fontWeight: 600,
                cursor: "pointer",
                boxShadow: mode === "webcam" ? "0 1px 2px rgba(0,0,0,0.05)" : "none",
                display: "inline-flex",
                alignItems: "center",
                gap: "0.3rem",
                transition: "all 0.15s ease"
              }}
            >
              <Camera size={13} />
              USB / Webcam
            </button>
          </div>
        </div>

        {/* IP Camera URL Input Bar */}
        {mode === "ip" && (
          <div style={{ marginBottom: "0.85rem", padding: "0.65rem 0.75rem", background: "#f8fafc", borderRadius: "8px", border: "1px solid #e2e8f0" }}>
            <div style={{ display: "flex", gap: "0.4rem", marginBottom: "0.45rem" }}>
              <input
                type="text"
                value={ipUrl}
                onChange={(e) => setIpUrl(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleApplyIp(ipUrl)}
                placeholder="e.g. http://10.13.14.68:8080/video"
                style={{
                  flex: 1,
                  background: "#ffffff",
                  border: "1px solid #cbd5e1",
                  borderRadius: "6px",
                  padding: "0.4rem 0.65rem",
                  color: "#0f172a",
                  fontSize: "0.82rem",
                  outline: "none"
                }}
              />
              <button
                type="button"
                onClick={() => handleApplyIp(ipUrl)}
                style={{
                  background: "#059669",
                  color: "#ffffff",
                  border: "none",
                  borderRadius: "6px",
                  padding: "0.4rem 0.85rem",
                  fontWeight: 600,
                  fontSize: "0.78rem",
                  cursor: "pointer"
                }}
              >
                Connect Stream
              </button>
            </div>
            <div style={{ display: "flex", gap: "0.35rem", flexWrap: "wrap", alignItems: "center" }}>
              <span style={{ fontSize: "0.68rem", color: "#64748b", fontWeight: 500, marginRight: "0.15rem" }}>Presets:</span>
              <button
                type="button"
                onClick={() => handleApplyIp("http://10.13.14.68:8080/video")}
                style={{ background: "#ffffff", border: "1px solid #e2e8f0", borderRadius: "4px", color: "#0284c7", padding: "0.15rem 0.45rem", fontSize: "0.68rem", fontWeight: 500, cursor: "pointer", display: "inline-flex", alignItems: "center", gap: "0.2rem" }}
              >
                <Smartphone size={11} /> Phone (:8080/video)
              </button>
              <button
                type="button"
                onClick={() => handleApplyIp("http://192.168.1.50/stream")}
                style={{ background: "#ffffff", border: "1px solid #e2e8f0", borderRadius: "4px", color: "#475569", padding: "0.15rem 0.45rem", fontSize: "0.68rem", fontWeight: 500, cursor: "pointer", display: "inline-flex", alignItems: "center", gap: "0.2rem" }}
              >
                <Cpu size={11} /> ESP32-CAM (:80/stream)
              </button>
              <button
                type="button"
                onClick={() => handleApplyIp("http://192.168.1.50:4747/video")}
                style={{ background: "#ffffff", border: "1px solid #e2e8f0", borderRadius: "4px", color: "#475569", padding: "0.15rem 0.45rem", fontSize: "0.68rem", fontWeight: 500, cursor: "pointer", display: "inline-flex", alignItems: "center", gap: "0.2rem" }}
              >
                <Video size={11} /> DroidCam (:4747/video)
              </button>
            </div>
          </div>
        )}

        {/* Dropzone & Live Display */}
        <div
          id="camera-container"
          className="drop-zone"
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => mode === "upload" && fileInputRef.current?.click()}
          style={{
            borderColor: isDragOver ? "#059669" : "#cbd5e1",
            background: mode === "upload" && !hasSnapshot ? "#f8fafc" : "#0f172a",
            cursor: mode === "upload" ? "pointer" : "default"
          }}
        >
          {mode === "upload" && !hasSnapshot && (
            <div style={{ textAlign: "center", padding: "2rem", color: "#64748b", display: "flex", flexDirection: "column", alignItems: "center" }}>
              <UploadCloud size={38} className="text-slate-400 mb-2" />
              <div style={{ fontWeight: 600, color: "#0f172a", fontSize: "0.92rem", marginBottom: "0.25rem" }}>
                Click to browse or Drag & Drop tomato leaf image
              </div>
              <div style={{ fontSize: "0.78rem", color: "#94a3b8" }}>
                Supports JPG, JPEG, PNG, WEBP from your folder
              </div>
            </div>
          )}

          {mode === "webcam" && (
            <video
              ref={videoRef}
              id="webcam-video"
              autoPlay
              playsInline
              muted
              className={hasSnapshot ? "hidden" : ""}
            />
          )}

          {mode === "ip" && !hasSnapshot && (
            <img
              key={currentStreamUrl}
              src={currentStreamUrl}
              alt="IP Camera Live Stream"
              onError={() => {
                if (!useProxy) {
                  setUseProxy(true);
                }
              }}
              style={{
                width: "100%",
                height: "100%",
                objectFit: "contain",
                borderRadius: "0.5rem",
                background: "#000"
              }}
            />
          )}

          <canvas ref={canvasRef} id="snapshot-canvas" hidden />
          
          {hasSnapshot && previewSrc && (
            <img id="image-preview" src={previewSrc} alt="Snapshot" />
          )}

          <input
            type="file"
            ref={fileInputRef}
            style={{ display: "none" }}
            accept="image/*"
            onChange={handleFileUpload}
          />
        </div>

        <div className="camera-controls">
          {mode === "upload" ? (
            <div style={{ display: "flex", gap: "0.75rem", width: "100%" }}>
              <button
                type="button"
                className="btn primary-btn"
                onClick={() => fileInputRef.current?.click()}
                disabled={isAnalyzing}
              >
                <FolderOpen size={16} />
                <span className="btn-text">
                  {isAnalyzing ? "Analyzing Plant Pathology..." : "Choose Image from Folder"}
                </span>
                {isAnalyzing && <span className="btn-spinner"></span>}
              </button>
              {hasSnapshot && (
                <button type="button" className="btn secondary-btn" onClick={resetCamera}>
                  <RotateCcw size={14} className="inline mr-1" />
                  Clear
                </button>
              )}
            </div>
          ) : (
            !hasSnapshot ? (
              <button
                id="analyze-btn"
                className="btn primary-btn"
                onClick={captureFrame}
                disabled={isAnalyzing || ipLoading}
              >
                <Sparkles size={16} />
                <span className="btn-text">
                  {isAnalyzing || ipLoading ? "Analyzing Plant Pathology..." : "Capture & Analyze Plant"}
                </span>
                {(isAnalyzing || ipLoading) && <span className="btn-spinner"></span>}
              </button>
            ) : (
              <button id="reset-cam-btn" className="btn secondary-btn" onClick={resetCamera}>
                <RotateCcw size={14} className="inline mr-1" />
                Reset Camera
              </button>
            )
          )}
        </div>
      </section>

      {/* Right: AI Classification Results */}
      <section className="results-section glass-panel">
        <h2 style={{ display: "flex", alignItems: "center", gap: "0.45rem" }}>
          <Sparkles size={18} className="text-emerald-600" />
          AI Classification Results
        </h2>
        <div
          id="classification-results"
          className={`results-content ${classificationResult ? "" : "empty"}`}
        >
          {classificationResult ? (
            <div className="primary-result">
              <div className="result-header">
                <h3>Primary Diagnosis</h3>
                <span className={isHealthy ? "badge low" : "badge high"}>
                  {isHealthy ? "HEALTHY" : "PATHOLOGY DETECTED"}
                </span>
              </div>
              <div className="diagnosis-name">
                {formatClassName(classificationResult.predicted_class)}
              </div>
              <div className="confidence-bar-container">
                <div
                  className="confidence-bar"
                  style={{ width: `${confidencePct}%` }}
                ></div>
              </div>
              <div className="confidence-label">
                Confidence: <strong>{confidencePct}%</strong>
              </div>

              {classificationResult.top_k && classificationResult.top_k.length > 1 && (
                <div className="top-k-results">
                  <h4>Alternative Candidates:</h4>
                  {classificationResult.top_k.slice(1).map((item, idx) => (
                    <div className="candidate-row" key={idx}>
                      <span>{formatClassName(item.class)}</span>
                      <span className="candidate-pct">
                        {(item.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <p className="placeholder-text">
              Select or upload a tomato leaf image to trigger Deep Learning pathology classification.
            </p>
          )}
        </div>
      </section>
    </div>
  );
};
