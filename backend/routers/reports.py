from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from fastapi.responses import FileResponse
from ..database import get_collection
from ..services.report_generator import generate_report
import os

router = APIRouter()


async def _generate_in_background(job_id: str, job: dict):
    """Generate PDF report in background after request returns."""
    generate_report(job)


@router.get("/report/{job_id}/pdf")
async def download_forensic_report(
    job_id: str,
    background_tasks: BackgroundTasks,
):
    """Download PDF forensic report for a completed analysis job."""
    collection = get_collection("jobs")
    job = await collection.find_one({"job_id": job_id}, {"_id": 0})

    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")

    if job.get("status") != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Analysis not completed yet. Current status: {job.get('status')}",
        )

    report_path = f"./reports/{job_id}.pdf"

    # Generate if not exists
    if not os.path.exists(report_path):
        generated = generate_report(job)
        if not generated:
            raise HTTPException(status_code=500, detail="Failed to generate report.")

    filename = f"forensic-report-{job_id[:8]}.pdf"
    return FileResponse(
        report_path,
        media_type="application/pdf",
        filename=filename,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.post("/report/{job_id}/generate")
async def trigger_report_generation(job_id: str, background_tasks: BackgroundTasks):
    """Manually trigger PDF generation for a job."""
    collection = get_collection("jobs")
    job = await collection.find_one({"job_id": job_id}, {"_id": 0})

    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    if job.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Job not completed yet.")

    background_tasks.add_task(_generate_in_background, job_id, job)
    return {"message": "Report generation started", "job_id": job_id}
