from fastapi import APIRouter, Query, Depends
from typing import Optional
from ..database import get_collection
from ..auth import get_current_user

router = APIRouter()


@router.get("/history")
async def get_analysis_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    verdict: Optional[str] = Query(None, description="authentic | suspicious | fake"),
    media_type: Optional[str] = Query(None, description="image | video"),
    current_user: dict = Depends(get_current_user),
):
    """Paginated analysis history, newest first."""
    collection = get_collection("jobs")

    # Build filter query
    query: dict = {}
    if verdict:
        query["result.verdict"] = verdict
    if media_type:
        query["media.mime_type"] = {"$regex": f"^{media_type}/"}

    # Fetch results
    cursor = (
        collection.find(query, {"_id": 0})
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )
    jobs = await cursor.to_list(length=limit)
    total = await collection.count_documents(query)

    # Summary stats
    stats = {
        "total": await collection.count_documents({}),
        "fake": await collection.count_documents({"result.verdict": "fake"}),
        "suspicious": await collection.count_documents({"result.verdict": "suspicious"}),
        "authentic": await collection.count_documents({"result.verdict": "authentic"}),
    }

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "stats": stats,
        "results": jobs,
    }
