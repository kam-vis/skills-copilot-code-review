"""Announcement management endpoints for the school app."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query

from ..database import announcements_collection, teachers_collection

router = APIRouter(
    prefix="/announcements",
    tags=["announcements"],
)


@router.get("", response_model=List[Dict[str, Any]])
@router.get("/", response_model=List[Dict[str, Any]])
def get_announcements() -> List[Dict[str, Any]]:
    """Return all announcements sorted by expiration date."""
    announcements = []
    for announcement in announcements_collection.find().sort("expires_at", 1):
        announcements.append(dict(announcement))
    return announcements


@router.get("/active", response_model=List[Dict[str, Any]])
def get_active_announcements() -> List[Dict[str, Any]]:
    """Return announcements that are currently in effect."""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    announcements = []
    for announcement in announcements_collection.find({
        "expires_at": {"$gte": today},
        "$or": [
            {"start_date": {"$exists": False}},
            {"start_date": {"$lt": today}},
            {"start_date": None},
            {"start_date": ""},
        ],
    }).sort("expires_at", 1):
        announcements.append(dict(announcement))
    return announcements


@router.post("", status_code=201)
def create_announcement(
    message: str = Query(..., min_length=1),
    expires_at: str = Query(...),
    start_date: Optional[str] = Query(None),
    teacher_username: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Create an announcement. Requires authenticated teacher/admin."""
    if not teacher_username:
        raise HTTPException(status_code=401, detail="Authentication required")

    teacher = teachers_collection.find_one({"_id": teacher_username})
    if not teacher:
        raise HTTPException(status_code=401, detail="Invalid teacher credentials")

    # Require an expiration date and validate format
    try:
        datetime.strptime(expires_at, "%Y-%m-%d")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Expiration date must be YYYY-MM-DD") from exc

    if start_date:
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Start date must be YYYY-MM-DD") from exc

    announcement = {
        "_id": f"announcement-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}",
        "message": message.strip(),
        "start_date": start_date,
        "expires_at": expires_at,
    }

    announcements_collection.insert_one(announcement)
    return {"message": "Announcement created successfully", "announcement": {"_id": announcement["_id"], "message": announcement["message"], "start_date": announcement["start_date"], "expires_at": announcement["expires_at"]}}


@router.put("/{announcement_id}")
def update_announcement(
    announcement_id: str,
    message: str = Query(..., min_length=1),
    expires_at: str = Query(...),
    start_date: Optional[str] = Query(None),
    teacher_username: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Update an announcement. Requires authenticated teacher/admin."""
    if not teacher_username:
        raise HTTPException(status_code=401, detail="Authentication required")

    teacher = teachers_collection.find_one({"_id": teacher_username})
    if not teacher:
        raise HTTPException(status_code=401, detail="Invalid teacher credentials")

    try:
        datetime.strptime(expires_at, "%Y-%m-%d")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Expiration date must be YYYY-MM-DD") from exc

    if start_date:
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Start date must be YYYY-MM-DD") from exc

    existing = announcements_collection.find_one({"_id": announcement_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Announcement not found")

    result = announcements_collection.update_one(
        {"_id": announcement_id},
        {"$set": {
            "message": message.strip(),
            "start_date": start_date,
            "expires_at": expires_at,
        }},
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")

    return {"message": "Announcement updated successfully"}


@router.delete("/{announcement_id}")
def delete_announcement(
    announcement_id: str,
    teacher_username: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Delete an announcement. Requires authenticated teacher/admin."""
    if not teacher_username:
        raise HTTPException(status_code=401, detail="Authentication required")

    teacher = teachers_collection.find_one({"_id": teacher_username})
    if not teacher:
        raise HTTPException(status_code=401, detail="Invalid teacher credentials")

    result = announcements_collection.delete_one({"_id": announcement_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")

    return {"message": "Announcement deleted successfully"}
