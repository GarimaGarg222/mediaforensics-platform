"""
Celery worker — runs ML analysis and generates PDF report.
"""
import os
import logging
from datetime import datetime, timezone
from celery import Celery
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL",    "redis://localhost:6379/0")
MONGO_URI = os.getenv("MONGO_URI",    "mongodb://localhost:27017")
MONGO_DB  = os.getenv("MONGO_DB_NAME","mediaforensics")

celery_app = Celery(
    "mediaforensics",
    broker=REDIS_URL,
    backend=REDIS_URL,
)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    task_track_started=True,
    worker_prefetch_multiplier=1,
)


def _get_collection(name: str):
    from pymongo import MongoClient
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    return client[MONGO_DB][name]


def _update_job(job_id: str, update: dict):
    _get_collection("jobs").update_one({"job_id": job_id}, {"$set": update})


@celery_app.task(bind=True, max_retries=2, name="run_analysis")
def run_analysis(self, job_id: str, file_path: str):
    """Main Celery task — ML pipeline + PDF report generation."""
    logger.info(f"[Worker] Starting job {job_id}")

    try:
        # Mark processing
        _update_job(job_id, {
            "status": "processing",
            "updated_at": datetime.now(timezone.utc),
        })

        # Run ML pipeline
        from .pipeline import get_pipeline
        pipeline = get_pipeline()
        result = pipeline.analyze(job_id, file_path)

        # Save result
        _update_job(job_id, {
            "status": "completed",
            "result": result,
            "updated_at": datetime.now(timezone.utc),
            "completed_at": datetime.now(timezone.utc),
        })

        # Generate PDF report
        try:
            jobs = _get_collection("jobs")
            job  = jobs.find_one({"job_id": job_id}, {"_id": 0})
            if job:
                from backend.services.report_generator import generate_report
                generate_report(job)
                logger.info(f"[Worker] PDF report generated for {job_id}")
        except Exception as e:
            logger.warning(f"[Worker] PDF generation failed (non-fatal): {e}")

        logger.info(f"[Worker] Job {job_id} done — verdict: {result['verdict']}")
        return {"job_id": job_id, "verdict": result["verdict"]}

    except Exception as e:
        logger.error(f"[Worker] Job {job_id} failed: {e}", exc_info=True)
        _update_job(job_id, {
            "status": "failed",
            "error_message": str(e),
            "updated_at": datetime.now(timezone.utc),
        })
        raise self.retry(exc=e, countdown=10)
