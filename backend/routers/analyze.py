from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from datetime import datetime, timezone
import os
import uuid
import mimetypes

from ..config import settings
from ..database import get_collection
from ..models.job import AnalysisJob, AnalysisJobResponse, JobStatus, MediaMetadata
from ..auth import get_current_user

router = APIRouter()

IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}
VIDEO_EXTENSIONS = {"mp4", "mov", "avi", "mkv"}


def validate_file(filename: str) -> str:
    """Validate extension and return it. Raises 415 if not allowed."""
    if "." not in filename:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File has no extension.",
        )
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext not in settings.allowed_extensions_list:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"'.{ext}' is not supported. Allowed: {settings.allowed_extensions}",
        )
    return ext


def get_mime_type(filename: str, ext: str) -> str:
    mime, _ = mimetypes.guess_type(filename)
    return mime or f"{'video' if ext in VIDEO_EXTENSIONS else 'image'}/{ext}"


@router.post("/analyze", response_model=AnalysisJobResponse, status_code=202)
async def upload_and_analyze(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """
    Upload a media file and queue it for analysis.
    Authentication optional — jobs are tracked by job_id.
    """
    ext = validate_file(file.filename)

    # Read and size-check
    content = await file.read()
    file_size = len(content)

    if file_size > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Max size is {settings.max_file_size_mb}MB.",
        )

    # Save to disk
    job_id = str(uuid.uuid4())
    save_path = os.path.join(settings.upload_dir, f"{job_id}.{ext}")
    os.makedirs(settings.upload_dir, exist_ok=True)

    with open(save_path, "wb") as f:
        f.write(content)

    # Build metadata
    media = MediaMetadata(
        filename=file.filename,
        file_size_bytes=file_size,
        mime_type=get_mime_type(file.filename, ext),
    )

    # Create job in MongoDB
    job = AnalysisJob(
        job_id=job_id,
        user_id=current_user.get("sub") if current_user else None,
        status=JobStatus.PENDING,
        media=media,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    collection = get_collection("jobs")
    await collection.insert_one(job.model_dump())

    # Dispatch Celery task (Day 3)
    # from ml.worker import run_analysis
    # run_analysis.delay(job_id, save_path)

    return AnalysisJobResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
        message="Job queued. Poll /api/results/{job_id} for updates.",
        created_at=job.created_at,
    )
