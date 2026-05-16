from fastapi import APIRouter, Depends, HTTPException, Query
from app.database import get_supabase
from app.models.task import TaskCreate, TaskUpdate
from app.core.security import get_current_user
from app.core.event_bus import EventBus, Events

router = APIRouter()


@router.get("/")
async def list_tasks(
    status: str = Query(None),
    assigned_to: str = Query(None),
    priority: str = Query(None),
    current_user=Depends(get_current_user)
):
    supabase = get_supabase()
    query = supabase.table("tasks").select("*, employees!tasks_assigned_to_fkey(full_name)")

    if status:
        query = query.eq("status", status)
    if assigned_to:
        query = query.eq("assigned_to", assigned_to)
    if priority:
        query = query.eq("priority", priority)

    return query.order("due_date", desc=False).execute().data


@router.get("/{task_id}")
async def get_task(task_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase()
    result = supabase.table("tasks").select("*").eq("id", task_id).single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Task not found")
    return result.data


@router.post("/")
async def create_task(data: TaskCreate, current_user=Depends(get_current_user)):
    from fastapi.encoders import jsonable_encoder
    supabase = get_supabase()
    event_bus = EventBus()

    task_data = jsonable_encoder(data)
    
    if task_data.get("assigned_to") == "":
        task_data["assigned_to"] = None
    if task_data.get("project_id") == "":
        task_data["project_id"] = None

    task = supabase.table("tasks").insert(task_data).execute().data[0]

    if task.get("assigned_to"):
        await event_bus.publish(Events.TASK_ASSIGNED, {"task": task})

    return task


@router.patch("/{task_id}")
async def update_task(
    task_id: str,
    data: TaskUpdate,
    current_user=Depends(get_current_user)
):
    supabase = get_supabase()
    update_data = data.dict(exclude_none=True)

    # Log update
    task = supabase.table("tasks").select("*").eq("id", task_id).single().execute().data
    if data.status and task.get("status") != data.status:
        supabase.table("task_updates").insert({
            "task_id": task_id,
            "employee_id": current_user["id"],
            "update_type": "status_change",
            "old_value": task.get("status"),
            "new_value": data.status
        }).execute()

    result = supabase.table("tasks").update(update_data).eq("id", task_id).execute()
    return result.data[0]
