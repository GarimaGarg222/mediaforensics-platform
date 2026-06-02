from fastapi import APIRouter, HTTPException, status
from ..database import get_collection
from ..models.job import JobStatusResponse

router = APIRouter()

PROGRESS_MAP = {
    "pending": 5,
    "processing": 55,
    "completed": 100,
    "failed": 0,
}


@router.get("/results/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Poll for analysis results.
    Status transitions: pending → processing → completed | failed
    """
    collection = get_collection("jobs")
    job = await collection.find_one({"job_id": job_id}, {"_id": 0})

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found.",
        )

    job["progress_pct"] = PROGRESS_MAP.get(job.get("status", "pending"), 0)
    return JobStatusResponse(**job)
