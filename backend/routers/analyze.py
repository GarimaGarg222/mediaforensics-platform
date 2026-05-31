from fastapi import APIRouter, UploadFile, File, HTTPException, status
from datetime import datetime
import os
import uuid

from ..config import settings
from ..database import get_collection
from ..models.job import AnalysisJob, AnalysisJobResponse, JobStatus, MediaMetadata

router = APIRouter()

ALLOWED_MIME_PREFIXES = ("image/", "video/")


def validate_file(file: UploadFile) -> None:
    """Raise HTTPException if file type or extension is not allowed."""
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in settings.allowed_extensions_list:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type '.{ext}' is not supported. Allowed: {settings.allowed_extensions}",
        )


@router.post("/analyze", response_model=AnalysisJobResponse, status_code=202)
async def upload_and_analyze(file: UploadFile = File(...)):
    """
    Upload a media file and start an analysis job.
    Returns a job_id to poll for results.
    """
    validate_file(file)

    # Read file content
    content = await file.read()
    file_size = len(content)

    if file_size > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {settings.max_file_size_mb}MB.",
        )

    # Save file to disk
    job_id = str(uuid.uuid4())
    ext = file.filename.rsplit(".", 1)[-1].lower()
    save_path = os.path.join(settings.upload_dir, f"{job_id}.{ext}")

    with open(save_path, "wb") as f:
        f.write(content)

    # Determine media type
    is_video = ext in ("mp4", "mov", "avi", "mkv")

    # Create job document in MongoDB
    job = AnalysisJob(
        job_id=job_id,
        status=JobStatus.PENDING,
        media=MediaMetadata(
            filename=file.filename,
            file_size_bytes=file_size,
            mime_type=file.content_type or f"{'video' if is_video else 'image'}/{ext}",
        ),
    )

    collection = get_collection("jobs")
    await collection.insert_one(job.model_dump())

    # TODO (Day 3): Dispatch Celery task here
    # from ml.worker import run_analysis
    # run_analysis.delay(job_id, save_path)

    return AnalysisJobResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
        message="Analysis job queued. Poll /api/results/{job_id} for status.",
        created_at=job.created_at,
    )
