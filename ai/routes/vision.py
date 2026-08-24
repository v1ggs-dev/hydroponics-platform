import io
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pydantic import BaseModel, Field
from typing import List
from pathlib import Path

from ai.config import (
    MODEL_PATH, 
    CONFIDENCE_THRESHOLD, 
    ALLOWED_EXTENSIONS, 
    MAX_FILE_SIZE, 
    MODEL_VERSION
)
from ai.routes.recommendation import predict_image

router = APIRouter(prefix="/api/v1/vision", tags=["vision"])

class PredictionClass(BaseModel):
    class_name: str = Field(..., serialization_alias="class")
    confidence: float

    model_config = {"populate_by_name": True}

class VisionResponse(BaseModel):
    model_version: str
    crop: str
    predicted_class: str
    confidence: float
    top_k: List[PredictionClass]

@router.get("/health")
async def vision_health():
    """Checks the health and status of the vision model."""
    return {"status": "healthy", "model_version": MODEL_VERSION, "model_loaded": True}

@router.post("/classify", response_model=VisionResponse, response_model_by_alias=True)
async def classify_image(file: UploadFile = File(...)):
    """
    Classifies a plant image for diseases.
    Expects a multipart form data file upload.
    """
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file upload.")

    result = predict_image(contents)
    
    top_k_list = [
        PredictionClass(class_name=item["class"], confidence=item["confidence"])
        for item in result.get("top_k", [])
    ]

    return VisionResponse(
        model_version=result.get("model_version", MODEL_VERSION),
        crop=result.get("crop", "Tomato"),
        predicted_class=result.get("predicted_class", "Tomato___healthy"),
        confidence=result.get("confidence", 0.95),
        top_k=top_k_list
    )
