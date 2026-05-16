from fastapi import APIRouter, Depends, HTTPException, Query
from app.database import get_supabase
from app.models.employee import EmployeeCreate, EmployeeUpdate
from app.core.security import get_current_user
from app.core.event_bus import EventBus, Events

router = APIRouter()


@router.get("/")
async def list_employees(
    status: str = Query(None),
    department_id: str = Query(None),
    current_user=Depends(get_current_user)
):
    supabase = get_supabase()
    query = supabase.table("employees").select("*, departments!employees_department_id_fkey(name)")

    if status:
        query = query.eq("status", status)
    if department_id:
        query = query.eq("department_id", department_id)

    result = query.execute()
    return result.data


@router.get("/{employee_id}")
async def get_employee(employee_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase()
    result = supabase.table("employees").select(
        "*, departments!employees_department_id_fkey(name)"
    ).eq("id", employee_id).single().execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Employee not found")
    return result.data


@router.post("/")
async def create_employee(data: EmployeeCreate, current_user=Depends(get_current_user)):
    from fastapi.encoders import jsonable_encoder
    supabase = get_supabase()
    event_bus = EventBus()

    import uuid

    # Mock the auth user creation since we disabled real login for the demo
    # This prevents Supabase free-tier permission errors
    mock_auth_id = str(uuid.uuid4())

    emp_data = jsonable_encoder(data, exclude={"password"})
    emp_data["auth_user_id"] = mock_auth_id

    emp = supabase.table("employees").insert(emp_data).execute().data[0]

    await event_bus.publish(Events.EMPLOYEE_ONBOARDED, {"employee": emp})
    return emp


@router.patch("/{employee_id}")
async def update_employee(
    employee_id: str,
    data: EmployeeUpdate,
    current_user=Depends(get_current_user)
):
    supabase = get_supabase()
    result = supabase.table("employees").update(
        data.dict(exclude_none=True)
    ).eq("id", employee_id).execute()
    return result.data[0]
