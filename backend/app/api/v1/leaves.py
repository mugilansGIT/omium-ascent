from fastapi import APIRouter, Depends, HTTPException, Query
from app.database import get_supabase
from app.models.leave import LeaveRequestCreate, LeaveRequestUpdate
from app.core.security import get_current_user
from app.core.event_bus import EventBus, Events

router = APIRouter()


@router.get("/")
async def list_leave_requests(
    status: str = Query(None),
    employee_id: str = Query(None),
    current_user=Depends(get_current_user)
):
    supabase = get_supabase()
    query = supabase.table("leaves").select(
        "*, employees(full_name, email), leave_policies(name, leave_type)"
    )
    if status:
        query = query.eq("status", status)
    if employee_id:
        query = query.eq("employee_id", employee_id)
    return query.order("created_at", desc=True).execute().data


@router.post("/request")
async def submit_leave_request(
    data: LeaveRequestCreate,
    current_user=Depends(get_current_user)
):
    supabase = get_supabase()
    event_bus = EventBus()

    leave = supabase.table("leaves").insert({
        "employee_id": current_user["id"],
        "policy_id": data.policy_id if data.policy_id else "annual",
        "start_date": str(data.start_date),
        "end_date": str(data.end_date),
        "total_days": data.total_days,
        "reason": data.reason,
        "status": "pending"
    }).execute().data[0]

    await event_bus.publish(Events.LEAVE_REQUESTED, {
        "event_type": Events.LEAVE_REQUESTED,
        "leave_request": leave
    })

    return {"id": leave["id"], "status": "pending", "message": "AI is processing your request"}


@router.get("/balances")
async def get_leave_balances(current_user=Depends(get_current_user)):
    supabase = get_supabase()
    return supabase.table("leave_balances").select(
        "*, leave_policies(name, leave_type)"
    ).eq("employee_id", current_user["id"]).execute().data


@router.patch("/{leave_id}")
async def update_leave_request(
    leave_id: str,
    data: LeaveRequestUpdate,
    current_user=Depends(get_current_user)
):
    supabase = get_supabase()
    result = supabase.table("leaves").update(
        data.dict(exclude_none=True)
    ).eq("id", leave_id).execute()
    return result.data[0]
