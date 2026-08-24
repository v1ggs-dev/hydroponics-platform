# Production Dockerfile for AI AgroEye Service (FastAPI + YOLO + RAG)
FROM python:3.11-slim

WORKDIR /app

# Install system graphics libraries for OpenCV and PyTorch
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies with pip cache disabled for minimal image size
COPY ai/requirements.txt ./ai_requirements.txt
RUN pip install --no-cache-dir -r ./ai_requirements.txt

# Copy AI application, models, and RAG knowledge datasets
COPY ai ./ai
COPY models ./models
COPY data ./data

ENV PYTHONUNBUFFERED=1
ENV PORT=8000

EXPOSE 8000

CMD ["uvicorn", "ai.main:app", "--host", "0.0.0.0", "--port", "8000"]
