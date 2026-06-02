from datetime import datetime, timezone
from typing import Optional
from ..database import get_collection
from ..models.job import JobStatus, DetectionResult


async def get_job(job_id: str) -> Optional[dict]:
    """Fetch a job document by job_id."""
    collection = get_collection("jobs")
    return await collection.find_one({"job_id": job_id}, {"_id": 0})


async def update_job_status(job_id: str, status: JobStatus, error: str = None):
    """Update job status and timestamp."""
    collection = get_collection("jobs")
    update = {
        "$set": {
            "status": status.value,
            "updated_at": datetime.now(timezone.utc),
        }
    }
    if error:
        update["$set"]["error_message"] = error
    await collection.update_one({"job_id": job_id}, update)


async def save_job_result(job_id: str, result: DetectionResult):
    """Save completed analysis result to the job document."""
    collection = get_collection("jobs")
    await collection.update_one(
        {"job_id": job_id},
        {
            "$set": {
                "status": JobStatus.COMPLETED.value,
                "result": result.model_dump(),
                "updated_at": datetime.now(timezone.utc),
                "completed_at": datetime.now(timezone.utc),
            }
        },
    )


async def update_job_media(job_id: str, media_update: dict):
    """Update media metadata fields (e.g. after extracting video info)."""
    collection = get_collection("jobs")
    await collection.update_one(
        {"job_id": job_id},
        {"$set": {f"media.{k}": v for k, v in media_update.items()}},
    )
