import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from ai.routes import vision, recommendation
from ai.config import ROOT_DIR

app = FastAPI(
    title="AgroEye AI Service",
    description="AI-powered hydroponics: plant disease classification + RAG recommendations",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vision.router)
app.include_router(recommendation.router)

# Mount the static Dashboard UI
DASHBOARD_DIR = ROOT_DIR / "dashboard"
if DASHBOARD_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(DASHBOARD_DIR)), name="static")

@app.get("/")
async def root():
    index_file = DASHBOARD_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {
        "name": "AgroEye AI Service",
        "version": "2.0.0",
        "endpoints": {
            "vision": "/api/v1/vision/classify",
            "recommendation": "/api/v1/recommendation/generate",
            "sensors_proxy": "/api/v1/recommendation/sensors"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
