from fastapi import APIRouter, Depends, Query
from app.database import get_supabase
from app.core.security import get_current_user
from app.core.event_bus import EventBus, Events

router = APIRouter()


@router.get("/")
async def list_trends(
    category: str = Query(None),
    min_score: float = Query(None),
    current_user=Depends(get_current_user)
):
    supabase = get_supabase()
    query = supabase.table("product_trends").select("*")

    if category:
        query = query.eq("category", category)
    if min_score:
        query = query.gte("trend_score", min_score)

    return query.order("trend_score", desc=True).execute().data


@router.post("/scan")
async def trigger_trend_scan(current_user=Depends(get_current_user)):
    event_bus = EventBus()
    await event_bus.publish(Events.TREND_SCAN_START, {
        "trigger": "manual",
        "requested_by": current_user["id"]
    })
    return {"status": "scan_triggered", "message": "Trend scan started"}
