from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from ..database import get_collection
import os

router = APIRouter()


@router.get("/report/{job_id}/pdf")
async def download_forensic_report(job_id: str):
    """
    Download a PDF forensic report for a completed analysis job.
    PDF generation is implemented on Day 5.
    """
    collection = get_collection("jobs")
    job = await collection.find_one({"job_id": job_id})

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found.",
        )

    if job.get("status") != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Report not ready — analysis is not yet completed.",
        )

    report_path = f"./reports/{job_id}.pdf"

    if not os.path.exists(report_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF report not yet generated. Retry in a moment.",
        )

    filename = f"forensic-report-{job_id[:8]}.pdf"
    return FileResponse(report_path, media_type="application/pdf", filename=filename)
