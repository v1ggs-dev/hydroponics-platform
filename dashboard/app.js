// =============================================================================
// AgroEye AI — Advanced Dashboard Logic (IoT + Telemetry Analytics + Pathology)
// =============================================================================

const API_IOT = 'http://localhost:4000/api/v1';
const API_AI = 'http://localhost:8000';
const DEVICE_ID = 'esp32-env';

// DOM Elements
const aiStatusDot = document.getElementById('ai-status-dot');
const iotStatusDot = document.getElementById('iot-status-dot');
const sensorOfflineBadge = document.getElementById('sensor-offline-badge');
const lastSyncTime = document.getElementById('last-sync-time');

// View Transition Elements
const sliderTrack = document.getElementById('slider-track');
const floatToAnalyticsBtn = document.getElementById('float-to-analytics-btn');
const floatToMainBtn = document.getElementById('float-to-main-btn');
const headerBtnMain = document.getElementById('header-btn-main');
const headerBtnAnalytics = document.getElementById('header-btn-analytics');

// Health & VPD Elements
const healthScoreVal = document.getElementById('health-score-val');
const healthCircleBar = document.getElementById('health-circle-bar');
const healthBadge = document.getElementById('health-badge');
const vpdVal = document.getElementById('vpd-val');
const vpdStatusBadge = document.getElementById('vpd-status-badge');
const vpdDescription = document.getElementById('vpd-description');
const vpdIndicatorMarker = document.getElementById('vpd-indicator-marker');

// IoT Controls Elements
const togglePumpBtn = document.getElementById('toggle-pump-btn');
const pumpStateText = document.getElementById('pump-state-text');
const toggleAutoBtn = document.getElementById('toggle-auto-btn');
const resetSafetyBtn = document.getElementById('reset-safety-btn');
const safetyStatusText = document.getElementById('safety-status-text');
const commandFeedbackMsg = document.getElementById('command-feedback-msg');

// Camera & AI Elements
const video = document.getElementById('webcam-video');
const canvas = document.getElementById('snapshot-canvas');
const imagePreview = document.getElementById('image-preview');
const analyzeBtn = document.getElementById('analyze-btn');
const resetBtn = document.getElementById('reset-cam-btn');
const btnText = analyzeBtn.querySelector('.btn-text');
const btnSpinner = analyzeBtn.querySelector('.btn-spinner');
const classificationResults = document.getElementById('classification-results');
const recommendationContent = document.getElementById('recommendation-content');

// History Elements
const scanHistoryContainer = document.getElementById('scan-history-container');
const clearHistoryBtn = document.getElementById('clear-history-btn');

// State Variables
let isPumpRunning = false;
let isAutoIrrigationEnabled = true;
let currentRange = '1h';
let waterChartInstance = null;
let climateChartInstance = null;
let currentTelemetryData = null;
let currentActiveView = 'main';

// =============================================================================
// Initialization
// =============================================================================
document.addEventListener('DOMContentLoaded', () => {
    initCharts();
    checkHealth();
    fetchSensors();
    fetchChartHistory(currentRange);
    startWebcam();
    loadScanHistory();

    // Auto-refresh loops
    setInterval(fetchSensors, 5000);
    setInterval(checkHealth, 15000);
    setInterval(() => fetchChartHistory(currentRange), 30000);

    // Event Listeners
    setupEventListeners();
    setupNavigation();
});

// =============================================================================
// Sliding Viewport Navigation (Main Overview <-> Analytics & IoT Hub)
// =============================================================================
function setupNavigation() {
    // Navigate to Analytics
    floatToAnalyticsBtn.addEventListener('click', () => switchView('analytics'));
    headerBtnAnalytics.addEventListener('click', () => switchView('analytics'));

    // Navigate to Main Overview
    floatToMainBtn.addEventListener('click', () => switchView('main'));
    headerBtnMain.addEventListener('click', () => switchView('main'));
}

function switchView(viewName) {
    if (viewName === 'analytics') {
        currentActiveView = 'analytics';
        sliderTrack.className = 'slider-track view-analytics-active';
        
        // Update floating buttons
        floatToAnalyticsBtn.classList.add('hidden');
        floatToMainBtn.classList.remove('hidden');

        // Update header pills
        headerBtnMain.classList.remove('active');
        headerBtnAnalytics.classList.add('active');

        // Smooth scroll to top of view
        window.scrollTo({ top: 0, behavior: 'smooth' });

        // Trigger Chart resize after slide animation completes
        setTimeout(() => {
            if (waterChartInstance) waterChartInstance.resize();
            if (climateChartInstance) climateChartInstance.resize();
        }, 300);

    } else {
        currentActiveView = 'main';
        sliderTrack.className = 'slider-track view-main-active';
        
        // Update floating buttons
        floatToMainBtn.classList.add('hidden');
        floatToAnalyticsBtn.classList.remove('hidden');

        // Update header pills
        headerBtnAnalytics.classList.remove('active');
        headerBtnMain.classList.add('active');

        // Smooth scroll to top of view
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

function setupEventListeners() {
    // Range selector buttons
    document.querySelectorAll('.time-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.time-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            currentRange = e.target.getAttribute('data-range');
            fetchChartHistory(currentRange);
        });
    });

    // Pump Toggle
    togglePumpBtn.addEventListener('click', () => {
        const nextState = isPumpRunning ? 'OFF' : 'ON';
        sendActuatorCommand('SET_STATE', nextState);
    });

    // Auto Mode Toggle
    toggleAutoBtn.addEventListener('click', () => {
        const nextAction = isAutoIrrigationEnabled ? 'AUTO_OFF' : 'AUTO_ON';
        sendActuatorCommand(nextAction);
    });

    // Safety Fault Reset
    resetSafetyBtn.addEventListener('click', () => {
        sendActuatorCommand('RESET_FAULT');
    });

    // Clear History
    clearHistoryBtn.addEventListener('click', () => {
        if (confirm('Clear all saved plant inspection scans?')) {
            localStorage.removeItem('agroeye_scan_history');
            loadScanHistory();
        }
    });
}

// =============================================================================
// Health Checks & Server Connectivity
// =============================================================================
async function checkHealth() {
    // AI Service
    try {
        const res = await fetch(`${API_AI}/health`);
        if (res.ok) setOnline(aiStatusDot);
        else setOffline(aiStatusDot);
    } catch {
        setOffline(aiStatusDot);
    }

    // IoT Backend
    try {
        const res = await fetch(`${API_IOT}/health`);
        if (res.ok) setOnline(iotStatusDot);
        else setOffline(iotStatusDot);
    } catch {
        setOffline(iotStatusDot);
    }
}

function setOnline(el) { el.className = 'dot online'; }
function setOffline(el) { el.className = 'dot offline'; }

// =============================================================================
// Live Telemetry Ingestion
// =============================================================================
const SENSOR_STALE_THRESHOLD = 60; // seconds

async function fetchSensors() {
    try {
        const res = await fetch(`${API_IOT}/telemetry/latest?deviceId=all`);
        if (!res.ok) throw new Error('API Error');
        const json = await res.json();

        if (json.success && json.data && Object.keys(json.data).length > 0) {
            const now = new Date();
            let isFresh = false;

            for (const key in json.data) {
                if (json.data[key]?.timestamp) {
                    const readingTime = new Date(json.data[key].timestamp);
                    const ageSeconds = (now - readingTime) / 1000;
                    if (ageSeconds < SENSOR_STALE_THRESHOLD) {
                        isFresh = true;
                        break;
                    }
                }
            }

            currentTelemetryData = json.data;

            if (isFresh) {
                updateSensors(json.data);
                computeAgronomicIndices(json.data);
                sensorOfflineBadge.classList.add('hidden');
                lastSyncTime.textContent = `Last synced: ${new Date().toLocaleTimeString()}`;
            } else {
                showOfflineState();
            }
        } else {
            showOfflineState();
        }
    } catch (err) {
        showOfflineState();
    }
}

function showOfflineState() {
    sensorOfflineBadge.textContent = '🔴 Sensors Not Connected';
    sensorOfflineBadge.classList.remove('hidden');
    lastSyncTime.textContent = 'Awaiting ESP32 connection...';
    resetSensors();
    computeAgronomicIndices(null);
}

function updateSensors(data) {
    updateSensorCard('temp', data.air_temperature?.value, 20, 30);
    updateSensorCard('tds', data.tds?.value, 500, 1400);
    updateSensorCard('ph', data.ph?.value, 5.5, 6.5);
    updateSensorCard('moist', data.substrate_moisture?.value, 40, 80);
    updateSensorCard('hum', data.humidity?.value, 45, 75);
    updateSensorCard('flow', data.flow_rate?.value, 0.2, 3.0);
    updateSensorCard('vol', data.water_volume?.value, 2, 50);
}

function updateSensorCard(id, value, minOk, maxOk) {
    const el = document.getElementById(`val-${id}`);
    if (!el) return;
    if (value === undefined || value === null) {
        el.textContent = '--';
        el.className = 'val-gray';
        return;
    }

    let displayVal = value;
    if (typeof value === 'number') {
        displayVal = Number.isInteger(value) ? value : value.toFixed(1);
    }
    el.textContent = displayVal;

    if (value >= minOk && value <= maxOk) {
        el.className = 'val-green';
    } else {
        if (id === 'ph' && (value < 4.0 || value > 8.5)) {
            el.className = 'val-red';
        } else {
            el.className = 'val-yellow';
        }
    }
}

function resetSensors() {
    ['temp', 'tds', 'ph', 'moist', 'hum', 'flow', 'vol'].forEach(id => {
        const el = document.getElementById(`val-${id}`);
        if (el) {
            el.textContent = '--';
            el.className = 'val-gray';
        }
    });
}

// =============================================================================
// Feature 2: Agronomic Health & VPD Calculation
// =============================================================================
function computeAgronomicIndices(data) {
    if (!data) {
        updateHealthGauge(92, 'STANDBY');
        updateVpdDisplay(1.10, 'OPTIMAL');
        return;
    }

    const temp = data.air_temperature?.value ?? 25.0;
    const hum = data.humidity?.value ?? 60.0;
    const ph = data.ph?.value ?? 6.0;
    const tds = data.tds?.value ?? 850;

    // 1. Calculate Vapor Pressure Deficit (VPD in kPa)
    const vpSat = 0.61078 * Math.exp((17.27 * temp) / (temp + 237.3));
    const vpActual = vpSat * (hum / 100.0);
    const vpd = Math.max(0, vpSat - vpActual);

    updateVpdDisplay(vpd);

    // 2. Compute Health Index (0-100%)
    let health = 100;
    if (ph < 5.5 || ph > 6.5) health -= Math.min(30, Math.abs(6.0 - ph) * 25);
    if (tds < 600) health -= Math.min(25, ((600 - tds) / 600) * 25);
    if (tds > 1400) health -= Math.min(25, ((tds - 1400) / 1000) * 25);
    if (temp < 18 || temp > 32) health -= Math.min(20, Math.abs(25 - temp) * 2);

    health = Math.max(20, Math.min(100, Math.round(health)));

    let statusText = 'EXCELLENT';
    if (health < 60) statusText = 'ACTION REQUIRED';
    else if (health < 80) statusText = 'MONITORING';

    updateHealthGauge(health, statusText);
}

function updateHealthGauge(score, status) {
    healthScoreVal.textContent = score;
    healthBadge.textContent = status;

    if (score >= 85) {
        healthBadge.className = 'badge low';
        healthCircleBar.style.stroke = '#10b981';
    } else if (score >= 70) {
        healthBadge.className = 'badge medium';
        healthCircleBar.style.stroke = '#f59e0b';
    } else {
        healthBadge.className = 'badge high';
        healthCircleBar.style.stroke = '#ef4444';
    }

    const offset = 251.2 - (251.2 * score) / 100;
    healthCircleBar.style.strokeDashoffset = offset;
}

function updateVpdDisplay(vpd) {
    vpdVal.textContent = vpd.toFixed(2);

    const markerPos = Math.max(0, Math.min(100, (vpd / 2.0) * 100));
    vpdIndicatorMarker.style.left = `${markerPos}%`;

    if (vpd < 0.4) {
        vpdStatusBadge.textContent = 'LOW TRANSPIRATION (HUMID)';
        vpdStatusBadge.className = 'status-pill yellow';
        vpdDescription.textContent = 'Air is saturated. Transpiration is stunted, increasing risks of mold and fungal pathogens.';
    } else if (vpd <= 1.2) {
        vpdStatusBadge.textContent = 'OPTIMAL VEGETATIVE UPTAKE';
        vpdStatusBadge.className = 'status-pill green';
        vpdDescription.textContent = 'Stomata are breathing freely with balanced nutrient and water transport to foliage.';
    } else if (vpd <= 1.6) {
        vpdStatusBadge.textContent = 'OPTIMAL FLOWERING / FRUITING';
        vpdStatusBadge.className = 'status-pill green';
        vpdDescription.textContent = 'Mild evaporative pull encouraging dense root feeding and robust flowering.';
    } else {
        vpdStatusBadge.textContent = 'WATER STRESS / DRY AIR';
        vpdStatusBadge.className = 'status-pill red';
        vpdDescription.textContent = 'High evaporative loss causes leaf tip curling and moisture stress. Increase humidity.';
    }
}

// =============================================================================
// Feature 3: IoT Remote Control Center Commands
// =============================================================================
async function sendActuatorCommand(action, value) {
    commandFeedbackMsg.textContent = `Dispatching command: ${action} ${value || ''}...`;

    try {
        const payload = {
            deviceId: DEVICE_ID,
            actuatorId: 'pump-01',
            action,
            value: value || undefined
        };

        const res = await fetch(`${API_IOT}/commands`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await res.json();

        if (res.ok && data.success) {
            commandFeedbackMsg.textContent = `✅ Successfully sent ${action} to ${DEVICE_ID}`;
            
            if (action === 'SET_STATE') {
                isPumpRunning = (value === 'ON');
                updatePumpButtonUI();
            } else if (action === 'AUTO_ON') {
                isAutoIrrigationEnabled = true;
                updateAutoButtonUI();
            } else if (action === 'AUTO_OFF') {
                isAutoIrrigationEnabled = false;
                updateAutoButtonUI();
            } else if (action === 'RESET_FAULT') {
                safetyStatusText.textContent = 'Interlock: Cleared (Normal)';
                safetyStatusText.style.color = '#10b981';
            }
        } else {
            commandFeedbackMsg.textContent = `⚠️ Command rejected: ${data.message || 'Error'}`;
        }
    } catch (err) {
        commandFeedbackMsg.textContent = `❌ Network Error: Could not reach backend`;
    }
}

function updatePumpButtonUI() {
    if (isPumpRunning) {
        togglePumpBtn.className = 'switch-btn on';
        togglePumpBtn.querySelector('.switch-label').textContent = 'PUMP RUNNING';
        pumpStateText.textContent = 'State: Active (Dosing Reservoir)';
        pumpStateText.style.color = '#059669';
    } else {
        togglePumpBtn.className = 'switch-btn off';
        togglePumpBtn.querySelector('.switch-label').textContent = 'START PUMP';
        pumpStateText.textContent = 'State: Standby / Idle';
        pumpStateText.style.color = '#64748b';
    }
}

function updateAutoButtonUI() {
    if (isAutoIrrigationEnabled) {
        toggleAutoBtn.className = 'switch-btn on';
        toggleAutoBtn.querySelector('.switch-label').textContent = 'AUTO ACTIVE';
    } else {
        toggleAutoBtn.className = 'switch-btn off';
        toggleAutoBtn.querySelector('.switch-label').textContent = 'MANUAL ONLY';
    }
}

// =============================================================================
// Feature 1: Interactive Analytics & Trend Charts (Chart.js)
// =============================================================================
function initCharts() {
    const ctxWater = document.getElementById('waterChemistryChart')?.getContext('2d');
    const ctxClimate = document.getElementById('climateChart')?.getContext('2d');

    if (!ctxWater || !ctxClimate) return;

    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.font.size = 11;
    Chart.defaults.color = '#64748b';

    // 1. Water Chemistry Chart (TDS & pH)
    waterChartInstance = new Chart(ctxWater, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'TDS (ppm)',
                    data: [],
                    borderColor: '#0284c7',
                    backgroundColor: 'rgba(2, 132, 199, 0.08)',
                    fill: true,
                    tension: 0.35,
                    borderWidth: 2.5,
                    yAxisID: 'yTds',
                    pointRadius: 2,
                    pointHoverRadius: 5
                },
                {
                    label: 'pH Level',
                    data: [],
                    borderColor: '#8b5cf6',
                    backgroundColor: 'transparent',
                    borderDash: [4, 4],
                    tension: 0.35,
                    borderWidth: 2.5,
                    yAxisID: 'yPh',
                    pointRadius: 2,
                    pointHoverRadius: 5
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: { position: 'top', align: 'end', labels: { boxWidth: 12, usePointStyle: true } }
            },
            scales: {
                x: { grid: { display: false } },
                yTds: {
                    type: 'linear',
                    position: 'left',
                    min: 0,
                    max: 1800,
                    grid: { color: 'rgba(226, 232, 240, 0.6)' },
                    title: { display: true, text: 'TDS (ppm)', font: { weight: 'bold' } }
                },
                yPh: {
                    type: 'linear',
                    position: 'right',
                    min: 4.0,
                    max: 8.5,
                    grid: { display: false },
                    title: { display: true, text: 'pH', font: { weight: 'bold' } }
                }
            }
        }
    });

    // 2. Climate Environment Chart (Temp & Humidity)
    climateChartInstance = new Chart(ctxClimate, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Temperature (°C)',
                    data: [],
                    borderColor: '#f43f5e',
                    backgroundColor: 'transparent',
                    tension: 0.35,
                    borderWidth: 2.5,
                    yAxisID: 'yTemp',
                    pointRadius: 2,
                    pointHoverRadius: 5
                },
                {
                    label: 'Humidity (%)',
                    data: [],
                    borderColor: '#06b6d4',
                    backgroundColor: 'rgba(6, 182, 212, 0.08)',
                    fill: true,
                    tension: 0.35,
                    borderWidth: 2.5,
                    yAxisID: 'yHum',
                    pointRadius: 2,
                    pointHoverRadius: 5
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: { position: 'top', align: 'end', labels: { boxWidth: 12, usePointStyle: true } }
            },
            scales: {
                x: { grid: { display: false } },
                yTemp: {
                    type: 'linear',
                    position: 'left',
                    min: 10,
                    max: 40,
                    grid: { color: 'rgba(226, 232, 240, 0.6)' },
                    title: { display: true, text: 'Temp (°C)', font: { weight: 'bold' } }
                },
                yHum: {
                    type: 'linear',
                    position: 'right',
                    min: 20,
                    max: 100,
                    grid: { display: false },
                    title: { display: true, text: 'Humidity (%)', font: { weight: 'bold' } }
                }
            }
        }
    });
}

async function fetchChartHistory(range) {
    try {
        const res = await fetch(`${API_IOT}/telemetry/history?deviceId=${DEVICE_ID}&range=${range}&limit=40`);
        if (res.ok) {
            const json = await res.json();
            if (json.success && json.data && json.data.length > 0) {
                renderHistoricalData(json.data);
                return;
            }
        }
    } catch {
        // Fallback
    }

    generateSyntheticTrendData(range);
}

function renderHistoricalData(records) {
    const timeLabels = [];
    const tdsPoints = [];
    const phPoints = [];
    const tempPoints = [];
    const humPoints = [];

    records.forEach(r => {
        const timeStr = new Date(r.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        if (!timeLabels.includes(timeStr)) timeLabels.push(timeStr);

        if (r.metric === 'tds') tdsPoints.push(r.value);
        else if (r.metric === 'ph') phPoints.push(r.value);
        else if (r.metric === 'air_temperature') tempPoints.push(r.value);
        else if (r.metric === 'humidity') humPoints.push(r.value);
    });

    if (waterChartInstance) {
        waterChartInstance.data.labels = timeLabels;
        waterChartInstance.data.datasets[0].data = tdsPoints;
        waterChartInstance.data.datasets[1].data = phPoints;
        waterChartInstance.update();
    }

    if (climateChartInstance) {
        climateChartInstance.data.labels = timeLabels;
        climateChartInstance.data.datasets[0].data = tempPoints;
        climateChartInstance.data.datasets[1].data = humPoints;
        climateChartInstance.update();
    }
}

function generateSyntheticTrendData(range) {
    const pointsCount = 12;
    const labels = [];
    const tdsData = [];
    const phData = [];
    const tempData = [];
    const humData = [];

    const now = new Date();
    const intervalMinutes = range === '1h' ? 5 : range === '6h' ? 30 : range === '24h' ? 120 : 720;

    for (let i = pointsCount - 1; i >= 0; i--) {
        const t = new Date(now.getTime() - i * intervalMinutes * 60 * 1000);
        labels.push(t.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));

        tdsData.push(Math.round(820 + Math.sin(i * 0.8) * 60 + (Math.random() * 15)));
        phData.push(Number((6.1 + Math.cos(i * 0.6) * 0.25 + (Math.random() * 0.05)).toFixed(2)));
        tempData.push(Number((24.5 + Math.sin(i * 0.5) * 2.2 + (Math.random() * 0.4)).toFixed(1)));
        humData.push(Math.round(62 + Math.cos(i * 0.5) * 6 + (Math.random() * 2)));
    }

    if (waterChartInstance) {
        waterChartInstance.data.labels = labels;
        waterChartInstance.data.datasets[0].data = tdsData;
        waterChartInstance.data.datasets[1].data = phData;
        waterChartInstance.update();
    }

    if (climateChartInstance) {
        climateChartInstance.data.labels = labels;
        climateChartInstance.data.datasets[0].data = tempData;
        climateChartInstance.data.datasets[1].data = humData;
        climateChartInstance.update();
    }
}

// =============================================================================
// Camera & Vision AI Diagnostics
// =============================================================================
async function startWebcam() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { width: { ideal: 1280 }, height: { ideal: 720 }, facingMode: "environment" },
            audio: false
        });
        video.srcObject = stream;
        video.muted = true;
        video.setAttribute('playsinline', 'true');
        video.onloadedmetadata = () => {
            video.play().catch(err => console.warn("Autoplay notice:", err));
        };
        // Explicitly trigger play immediately
        video.play().catch(() => {});
    } catch (err) {
        console.warn("Webcam access note:", err);
    }
}

resetBtn.addEventListener('click', () => {
    imagePreview.classList.add('hidden');
    video.play();
    resetBtn.classList.add('hidden');

    classificationResults.innerHTML = '<p class="placeholder-text">Capture a leaf snapshot to trigger Deep Learning pathology classification.</p>';
    classificationResults.classList.add('empty');

    recommendationContent.innerHTML = '<p class="placeholder-text">Expert treatment protocols and bio-nutrient recommendations will appear here after analysis.</p>';
    recommendationContent.classList.add('empty');

    analyzeBtn.disabled = false;
    btnText.textContent = 'Capture & Analyze Plant';
});

analyzeBtn.addEventListener('click', async () => {
    if (!video.videoWidth) {
        alert("Webcam stream is initializing. Please ensure camera permissions are active.");
        return;
    }

    analyzeBtn.disabled = true;
    btnText.textContent = 'Neural Diagnosis Running...';
    btnSpinner.classList.remove('hidden');
    resetBtn.classList.remove('hidden');

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const snapshotDataUrl = canvas.toDataURL('image/jpeg', 0.9);
    imagePreview.src = snapshotDataUrl;
    imagePreview.classList.remove('hidden');
    video.pause();

    classificationResults.classList.remove('empty');
    classificationResults.innerHTML = `
        <div class="skeleton sk-title"></div>
        <div class="skeleton sk-text"></div>
        <div class="skeleton sk-text" style="height:2rem; margin-bottom:1.5rem"></div>
        <div class="skeleton sk-card"></div>
        <div class="skeleton sk-card"></div>
    `;

    recommendationContent.classList.remove('empty');
    recommendationContent.innerHTML = `
        <div class="skeleton sk-title"></div>
        <div class="skeleton sk-text" style="height:3rem"></div>
        <div class="skeleton sk-card"></div>
        <div class="skeleton sk-card"></div>
    `;

    canvas.toBlob(async (blob) => {
        if (!blob) {
            classificationResults.innerHTML = `<div class="error-msg">Frame Capture Failure</div>`;
            return;
        }

        const formData = new FormData();
        formData.append('file', blob, 'leaf_capture.jpg');

        const recFormData = new FormData();
        recFormData.append('file', blob, 'leaf_capture.jpg');

        const classifyReq = fetch(`${API_AI}/api/v1/vision/classify`, { method: 'POST', body: formData });
        const recommendReq = fetch(`${API_AI}/api/v1/recommendation/generate`, { method: 'POST', body: recFormData });

        try {
            const classRes = await classifyReq;
            if (!classRes.ok) throw new Error('Classification Service Error');
            const classData = await classRes.json();

            renderClassification(classData);
            saveScanToHistory(snapshotDataUrl, classData);

            try {
                const recRes = await recommendReq;
                const recData = await recRes.json();
                if (recRes.ok && recData.recommendation) {
                    renderRecommendation(recData);
                } else {
                    showRecommendationError(recData.detail || 'Recommendation service error');
                }
            } catch {
                showRecommendationError('AI Recommendations unavailable — check Groq LLM API connectivity');
            }

        } catch (err) {
            classificationResults.innerHTML = `<div class="error-msg">Pathology Engine Error: ${err.message}</div>`;
            recommendationContent.innerHTML = `<div class="error-msg">Analysis aborted</div>`;
        } finally {
            analyzeBtn.disabled = false;
            btnText.textContent = 'Capture & Analyze Plant';
            btnSpinner.classList.add('hidden');
        }
    }, 'image/jpeg', 0.95);
});

function renderClassification(data) {
    const formattedName = formatClassName(data.predicted_class || 'Healthy Foliage');
    const crop = data.crop || getCropType(data.predicted_class || '');
    const conf = (data.confidence * 100).toFixed(1);

    let barColor = '#ef4444';
    if (data.confidence > 0.8) barColor = '#10b981';
    else if (data.confidence > 0.5) barColor = '#f59e0b';

    let topKHtml = '';
    if (data.top_k && data.top_k.length > 0) {
        topKHtml = `
            <div class="predictions-list">
                ${data.top_k.map(p => `
                    <div class="prediction-item">
                        <span class="pred-name">${formatClassName(p.class)}</span>
                        <span class="pred-conf">${(p.confidence * 100).toFixed(1)}%</span>
                    </div>
                `).join('')}
            </div>
        `;
    }

    classificationResults.innerHTML = `
        <div class="classification-main">
            <div class="disease-name">${formattedName}</div>
            <div class="crop-name">Identified Crop: ${crop}</div>
            <div class="confidence-wrapper">
                <div class="confidence-bar" style="width: ${conf}%; background: ${barColor}"></div>
            </div>
            <div class="confidence-text">${conf}% Neural Confidence</div>
        </div>
        ${topKHtml}
    `;
}

function renderRecommendation(data) {
    const rec = data.recommendation;
    if (!rec || rec.error) {
        showRecommendationError(rec?.error || 'Invalid recommendation response');
        return;
    }

    const prioClass = rec.priority?.toLowerCase() || 'medium';

    let actionsHtml = '';
    if (rec.actions && rec.actions.length > 0) {
        actionsHtml = `
            <div class="rec-actions">
                <h3>Targeted Agricultural Protocols</h3>
                <ul class="action-list">
                    ${rec.actions.map((act, i) => `
                        <li class="action-item">
                            <div class="action-title"><span style="color:var(--accent)">${i+1}.</span> ${act.action}</div>
                            <div class="action-reason">${act.reason}</div>
                            ${act.source_ids && act.source_ids.length ? `<div class="action-sources">Verified Agronomy Sources: ${act.source_ids.join(', ')}</div>` : ''}
                        </li>
                    `).join('')}
                </ul>
            </div>
        `;
    }

    let warningsHtml = '';
    if (rec.warnings && rec.warnings.length > 0) {
        warningsHtml = `
            <div class="rec-warnings">
                <h3>Agronomic Risk Alerts</h3>
                <ul class="warning-list">
                    ${rec.warnings.map(w => `<li>${w}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    recommendationContent.innerHTML = `
        <div class="rec-header">
            <span class="badge ${prioClass}">${rec.priority || 'EVALUATED'} PRIORITY</span>
        </div>
        <div class="rec-summary">${rec.summary || ''}</div>
        ${actionsHtml}
        ${warningsHtml}
    `;
}

function showRecommendationError(msg) {
    recommendationContent.innerHTML = `<div class="error-msg">${msg}</div>`;
}

// =============================================================================
// Feature 5: AI Vision Scan History & Audit Log
// =============================================================================
function saveScanToHistory(imageDataUrl, classData) {
    const history = JSON.parse(localStorage.getItem('agroeye_scan_history') || '[]');
    const newScan = {
        id: `scan-${Date.now()}`,
        image: imageDataUrl,
        crop: classData.crop || getCropType(classData.predicted_class || ''),
        disease: formatClassName(classData.predicted_class || 'Healthy'),
        confidence: Math.round(classData.confidence * 100),
        timestamp: new Date().toISOString()
    };

    history.unshift(newScan);
    if (history.length > 12) history.pop();

    localStorage.setItem('agroeye_scan_history', JSON.stringify(history));
    loadScanHistory();
}

function loadScanHistory() {
    const history = JSON.parse(localStorage.getItem('agroeye_scan_history') || '[]');

    if (!history.length) {
        scanHistoryContainer.className = 'history-grid empty';
        scanHistoryContainer.innerHTML = `
            <div class="history-empty-placeholder">
                No plant inspection snapshots saved yet. Capture and analyze leaves to build your crop health timeline.
            </div>
        `;
        return;
    }

    scanHistoryContainer.className = 'history-grid';
    scanHistoryContainer.innerHTML = history.map(scan => {
        const timeAgo = formatTimeAgo(new Date(scan.timestamp));
        const isHealthy = scan.disease.toLowerCase().includes('healthy');
        const badgeColor = isHealthy ? 'background:#d1fae5; color:#059669;' : 'background:#fee2e2; color:#dc2626;';

        return `
            <div class="history-card">
                <img src="${scan.image}" alt="${scan.disease}" class="history-img-thumb">
                <div class="history-info-body">
                    <div class="history-disease-title" title="${scan.disease}">${scan.disease}</div>
                    <div class="history-meta-row">
                        <span class="history-time">${timeAgo}</span>
                        <span class="history-conf-badge" style="${badgeColor}">${scan.confidence}%</span>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function formatTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    if (seconds < 60) return 'Just now';
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
}

function formatClassName(className) {
    if (!className) return 'Healthy Foliage';
    return className.replace(/___/g, ' - ').replace(/_/g, ' ');
}

function getCropType(className) {
    if (!className) return 'Hydroponic Crop';
    if (className.includes('___')) return className.split('___')[0].replace(/_/g, ' ');
    return className.split('_')[0] || 'Hydroponic Crop';
}
