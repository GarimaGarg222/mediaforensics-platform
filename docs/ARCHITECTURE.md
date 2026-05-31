# Architecture

## System Overview

```
Browser (React)
    │ HTTP / REST
    ▼
FastAPI Backend (:8000)
    │                    │
    ▼                    ▼
MongoDB              Redis (Celery broker)
(job storage)            │
                         ▼
                   ML Worker (Celery)
                   ├── YOLOv8 (face detection)
                   ├── XceptionNet (deepfake classifier)
                   ├── ELA (JPEG tampering)
                   └── Grad-CAM (heatmap)
```

## Request Lifecycle

1. User uploads file via `POST /api/analyze`
2. Backend validates file (type, size, MIME)
3. File saved to `/uploads/{job_id}.{ext}`
4. Job document created in MongoDB with status `pending`
5. Celery task dispatched to Redis queue
6. Backend immediately returns `job_id` to client (202 Accepted)
7. Frontend polls `GET /api/results/{job_id}` every 2 seconds
8. ML Worker picks up task from Redis:
   - Extracts frames (video) or loads image
   - Runs YOLOv8 face detection
   - Runs XceptionNet inference per frame
   - Generates Grad-CAM heatmap
   - Runs ELA analysis
   - Aggregates scores
9. Worker updates MongoDB job document with status `completed` + results
10. Next poll returns full results to frontend

## Data Models

### AnalysisJob (MongoDB)
```json
{
  "job_id": "uuid4",
  "status": "pending | processing | completed | failed",
  "media": { "filename": "...", "mime_type": "...", ... },
  "result": {
    "authenticity_score": 94.5,
    "verdict": "authentic | suspicious | fake",
    "confidence": 0.97,
    "signals": { "face_swap": 0.03, ... },
    "frames_analyzed": 47,
    "frames_flagged": 2,
    "heatmap_url": "/uploads/{job_id}_heatmap.png"
  },
  "created_at": "ISO datetime",
  "completed_at": "ISO datetime"
}
```

## Environment Setup

See `.env.example` for all required environment variables.
