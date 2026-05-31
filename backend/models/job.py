from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum
import uuid


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Verdict(str, Enum):
    AUTHENTIC = "authentic"
    SUSPICIOUS = "suspicious"
    FAKE = "fake"


class FrameResult(BaseModel):
    frame_index: int
    timestamp_sec: float
    is_manipulated: bool
    confidence: float
    face_detected: bool


class DetectionSignals(BaseModel):
    face_swap: float = 0.0          # 0-1 probability
    gan_artifacts: float = 0.0
    temporal_inconsistency: float = 0.0
    blink_anomaly: float = 0.0
    jpeg_artifacts: float = 0.0


class DetectionResult(BaseModel):
    authenticity_score: float       # 0-100, higher = more authentic
    verdict: Verdict
    confidence: float               # Overall confidence in verdict
    signals: DetectionSignals
    frames_analyzed: int = 0
    frames_flagged: int = 0
    heatmap_url: Optional[str] = None
    frame_results: List[FrameResult] = []


class MediaMetadata(BaseModel):
    filename: str
    file_size_bytes: int
    mime_type: str
    duration_sec: Optional[float] = None   # Video only
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[float] = None
    codec: Optional[str] = None
    has_gps_data: bool = False
    creation_date: Optional[str] = None
    exif_consistent: bool = True


class AnalysisJob(BaseModel):
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    status: JobStatus = JobStatus.PENDING
    media: Optional[MediaMetadata] = None
    result: Optional[DetectionResult] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    model_config = {"use_enum_values": True}


class AnalysisJobResponse(BaseModel):
    """Returned to client after upload."""
    job_id: str
    status: str
    message: str
    created_at: datetime


class JobStatusResponse(BaseModel):
    """Returned when polling for results."""
    job_id: str
    status: str
    progress_pct: Optional[int] = None
    result: Optional[DetectionResult] = None
    media: Optional[MediaMetadata] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
