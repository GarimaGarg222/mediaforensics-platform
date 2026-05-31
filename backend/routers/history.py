from fastapi import APIRouter, Query
from typing import List, Optional
from ..database import get_collection

router = APIRouter()


@router.get("/history")
async def get_analysis_history(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Max records to return"),
    verdict: Optional[str] = Query(None, description="Filter by verdict: authentic | suspicious | fake"),
    media_type: Optional[str] = Query(None, description="Filter by type: image | video"),
):
    """
    Return paginated analysis history, newest first.
    """
    collection = get_collection("jobs")

    query: dict = {}
    if verdict:
        query["result.verdict"] = verdict
    if media_type:
        query["media.mime_type"] = {"$regex": f"^{media_type}/"}

    cursor = collection.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit)
    jobs = await cursor.to_list(length=limit)

    total = await collection.count_documents(query)

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "results": jobs,
    }
