from fastapi import APIRouter, HTTPException, status
from ..database import get_collection
from ..models.job import JobStatusResponse

router = APIRouter()


@router.get("/results/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Poll this endpoint for analysis results.
    Status will transition: pending → processing → completed | failed
    """
    collection = get_collection("jobs")
    job = await collection.find_one({"job_id": job_id})

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found.",
        )

    job.pop("_id", None)

    # Calculate progress percentage based on status
    progress_map = {
        "pending": 5,
        "processing": 50,
        "completed": 100,
        "failed": 0,
    }
    job["progress_pct"] = progress_map.get(job.get("status", "pending"), 0)

    return JobStatusResponse(**job)
