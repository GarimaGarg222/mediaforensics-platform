# API Reference

Base URL: `http://localhost:8000` (dev) | `https://your-app.onrender.com` (prod)

Interactive docs available at `/docs` (Swagger UI) and `/redoc`.

---

## Health

### GET /api/health
Returns server status.

**Response 200**
```json
{ "status": "ok", "app": "MediaForensics", "env": "development", "version": "1.0.0" }
```

---

## Analysis

### POST /api/analyze
Upload a media file for analysis.

**Request** — multipart/form-data
| Field | Type | Required | Description |
|---|---|---|---|
| file | File | Yes | Image or video file |

**Response 202**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Analysis job queued. Poll /api/results/{job_id} for status.",
  "created_at": "2026-05-29T10:00:00Z"
}
```

**Errors**
- 413 — File exceeds 500MB limit
- 415 — File type not supported

---

### GET /api/results/{job_id}
Poll for analysis results.

**Response 200**
```json
{
  "job_id": "550e8400-...",
  "status": "completed",
  "progress_pct": 100,
  "media": {
    "filename": "video.mp4",
    "file_size_bytes": 14876543,
    "mime_type": "video/mp4",
    "duration_sec": 47.0,
    "width": 1920,
    "height": 1080
  },
  "result": {
    "authenticity_score": 6.2,
    "verdict": "fake",
    "confidence": 0.94,
    "signals": {
      "face_swap": 0.94,
      "gan_artifacts": 0.87,
      "temporal_inconsistency": 0.79,
      "blink_anomaly": 0.66,
      "jpeg_artifacts": 0.31
    },
    "frames_analyzed": 47,
    "frames_flagged": 31,
    "heatmap_url": "/uploads/550e8400_heatmap.png"
  },
  "created_at": "2026-05-29T10:00:00Z",
  "completed_at": "2026-05-29T10:00:08Z"
}
```

**Verdict thresholds**
| Score | Verdict |
|---|---|
| 0–40 | fake |
| 41–70 | suspicious |
| 71–100 | authentic |

---

## History

### GET /api/history
Paginated list of past analyses.

**Query params**
| Param | Default | Description |
|---|---|---|
| skip | 0 | Records to skip |
| limit | 20 | Max records (1–100) |
| verdict | — | Filter: authentic, suspicious, fake |
| media_type | — | Filter: image, video |

---

## Reports

### GET /api/report/{job_id}/pdf
Download PDF forensic report for a completed job.

**Response** — application/pdf binary download
