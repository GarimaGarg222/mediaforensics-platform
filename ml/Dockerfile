# Use CPU-only base for compatibility; swap to pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime for GPU
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-ml.txt .
RUN pip install --no-cache-dir -r requirements-ml.txt

COPY . .

RUN mkdir -p weights uploads

CMD ["celery", "-A", "worker.celery_app", "worker", "--loglevel=info", "--concurrency=2"]
