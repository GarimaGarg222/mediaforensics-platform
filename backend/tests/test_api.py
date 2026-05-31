import pytest
import io
from datetime import datetime, timezone
from unittest.mock import AsyncMock


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


@pytest.mark.asyncio
async def test_upload_valid_image(client, mock_db):
    image_data = io.BytesIO(b"\xff\xd8\xff" + b"\x00" * 100)
    response = await client.post(
        "/api/analyze",
        files={"file": ("test_image.jpg", image_data, "image/jpeg")},
    )
    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_upload_invalid_extension(client):
    bad_file = io.BytesIO(b"some content")
    response = await client.post(
        "/api/analyze",
        files={"file": ("malware.exe", bad_file, "application/octet-stream")},
    )
    assert response.status_code == 415


@pytest.mark.asyncio
async def test_upload_file_too_large(client):
    large_file = io.BytesIO(b"x" * (501 * 1024 * 1024))
    response = await client.post(
        "/api/analyze",
        files={"file": ("big_video.mp4", large_file, "video/mp4")},
    )
    assert response.status_code in (413, 422)


@pytest.mark.asyncio
async def test_get_results_not_found(client, mock_db):
    mock_db.find_one = AsyncMock(return_value=None)
    response = await client.get("/api/results/nonexistent-job-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_results_found(client, mock_db):
    mock_db.find_one = AsyncMock(side_effect=lambda query: {
        "job_id": "test-job-123",
        "status": "completed",
        "created_at": datetime.now(timezone.utc),
        "media": {
            "filename": "test.jpg",
            "file_size_bytes": 1024,
            "mime_type": "image/jpeg",
            "has_gps_data": False,
            "exif_consistent": True,
        },
        "result": {
            "authenticity_score": 94.5,
            "verdict": "authentic",
            "confidence": 0.97,
            "signals": {
                "face_swap": 0.03, "gan_artifacts": 0.05,
                "temporal_inconsistency": 0.02, "blink_anomaly": 0.01,
                "jpeg_artifacts": 0.08,
            },
            "frames_analyzed": 1,
            "frames_flagged": 0,
        },
    })
    response = await client.get("/api/results/test-job-123")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["progress_pct"] == 100


@pytest.mark.asyncio
async def test_history_returns_list(client, mock_db):
    mock_db.count_documents = AsyncMock(return_value=0)
    mock_db.find.return_value.sort.return_value.skip.return_value.limit.return_value.to_list = AsyncMock(return_value=[])

    response = await client.get("/api/history")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_history_pagination_params(client, mock_db):
    mock_db.count_documents = AsyncMock(return_value=0)
    mock_db.find.return_value.sort.return_value.skip.return_value.limit.return_value.to_list = AsyncMock(return_value=[])

    response = await client.get("/api/history?skip=10&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["skip"] == 10
    assert data["limit"] == 5
