# MediaForensics Platform

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?logo=fastapi)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)
![PyTorch](https://img.shields.io/badge/PyTorch-2.1-EE4C2C?logo=pytorch)
![MongoDB](https://img.shields.io/badge/MongoDB-7.0-47A248?logo=mongodb)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)
![License](https://img.shields.io/badge/License-MIT-yellow)

AI-powered platform to detect manipulated and AI-generated images and videos (deepfakes). Performs frame-level and facial analysis using YOLO, XceptionNet, and ELA forensics. Generates authenticity scores, confidence metrics, and forensic heatmaps.

---

## Features

- Upload images and video files for instant analysis
- Face detection using YOLOv8
- Deepfake classification via FaceForensics++ XceptionNet model
- GAN fingerprint detection using ResNet-50
- Error Level Analysis (ELA) for JPEG tampering
- Grad-CAM forensic heatmaps showing manipulated regions
- Frame-by-frame timeline for video analysis
- Downloadable PDF forensic reports
- JWT authentication
- Analysis history dashboard

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI + Uvicorn |
| ML Inference | PyTorch, YOLOv8, OpenCV |
| Task Queue | Celery + Redis |
| Database | MongoDB (Motor async) |
| Frontend | React 18 + Vite + Tailwind CSS |
| Containerization | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| Deployment | Render (backend) + Vercel (frontend) + MongoDB Atlas |

## Project Structure

```
mediaforensics-platform/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Settings and env vars
│   ├── database.py          # MongoDB connection
│   ├── auth.py              # JWT authentication
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── routers/
│   │   ├── analyze.py       # Upload & analysis endpoints
│   │   ├── results.py       # Job status & results
│   │   ├── history.py       # Analysis history
│   │   ├── reports.py       # PDF report download
│   │   └── auth.py          # Register/login
│   ├── models/
│   │   ├── job.py           # AnalysisJob Pydantic model
│   │   └── user.py          # User model
│   ├── services/
│   │   └── report_generator.py
│   └── tests/
│       ├── conftest.py
│       └── test_api.py
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api/client.js
│   │   ├── context/AuthContext.jsx
│   │   ├── components/
│   │   └── pages/
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── ml/
│   ├── pipeline.py          # Main inference pipeline
│   ├── face_detector.py     # YOLOv8 wrapper
│   ├── classifier.py        # XceptionNet deepfake classifier
│   ├── ela.py               # Error Level Analysis
│   ├── gradcam.py           # Grad-CAM heatmap generator
│   ├── worker.py            # Celery worker
│   ├── aggregator.py        # Score aggregation
│   └── requirements-ml.txt
├── docs/
│   ├── ARCHITECTURE.md
│   └── API.md
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
├── .gitignore
└── README.md
```

## Quick Start (Docker)

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/mediaforensics-platform.git
cd mediaforensics-platform

# 2. Copy env file and fill in values
cp .env.example .env

# 3. Start all services
docker-compose up --build

# 4. Open the app
#    Frontend:  http://localhost:5173
#    API docs:  http://localhost:8000/docs
```

## Manual Setup (Development)

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### ML Worker
```bash
cd ml
pip install -r requirements-ml.txt
celery -A worker.celery_app worker --loglevel=info
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

See `.env.example` for all required variables. Key ones:

| Variable | Description |
|---|---|
| `MONGO_URI` | MongoDB connection string |
| `SECRET_KEY` | JWT signing secret (generate with `openssl rand -hex 32`) |
| `REDIS_URL` | Redis connection for Celery |
| `MODEL_PATH` | Path to downloaded XceptionNet weights |
| `MAX_FILE_SIZE_MB` | Upload size limit (default: 500) |

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/analyze` | Upload media for analysis |
| GET | `/api/results/{job_id}` | Get job status and results |
| GET | `/api/history` | Paginated analysis history |
| GET | `/api/report/{job_id}/pdf` | Download forensic PDF report |
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login and get JWT token |
| GET | `/api/health` | Health check |

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/your-feature`)
3. Commit changes (`git commit -m 'feat: add your feature'`)
4. Push to branch (`git push origin feat/your-feature`)
5. Open a Pull Request

## License

MIT — see [LICENSE](LICENSE) for details.
