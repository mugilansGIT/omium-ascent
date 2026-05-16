from fastapi import APIRouter, Depends, HTTPException
from app.database import get_supabase
from app.models.payroll import PayrollPeriodCreate, PayrollRecordCreate
from app.core.security import get_current_user
from app.core.gemini_client import GeminiClient

router = APIRouter()

PAYROLL_AI_PROMPT = """
Review this payroll record and provide notes.

Employee: {employee_name}
Base Salary: {base_salary}
Attendance: {attendance_days}/{working_days} days
Deductions: {deductions}
Bonuses: {bonuses}
Gross Salary: {gross_salary}
Net Salary: {net_salary}

Provide brief notes on anomalies, compliance checks, or observations.
Return JSON: {{"notes": "...", "flag": true/false, "flag_reason": "..."}}
"""


@router.get("/periods")
async def list_periods(current_user=Depends(get_current_user)):
    supabase = get_supabase()
    return supabase.table("payroll_periods").select("*").order(
        "start_date", desc=True
    ).execute().data


@router.post("/periods")
async def create_period(data: PayrollPeriodCreate, current_user=Depends(get_current_user)):
    supabase = get_supabase()
    return supabase.table("payroll_periods").insert(data.dict()).execute().data[0]


@router.get("/periods/{period_id}/records")
async def get_period_records(period_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase()
    return supabase.table("payroll_records").select(
        "*, employees(full_name, employee_code, department_id)"
    ).eq("period_id", period_id).execute().data


@router.post("/records")
async def create_payroll_record(
    data: PayrollRecordCreate,
    current_user=Depends(get_current_user)
):
    supabase = get_supabase()
    gemini = GeminiClient()

    emp = supabase.table("employees").select("full_name").eq(
        "id", data.employee_id
    ).single().execute().data

    # Calculate salary
    working_days = data.working_days or 22
    attendance_days = data.attendance_days or working_days
    gross = (data.base_salary / working_days) * attendance_days

    total_deductions = sum(data.deductions.values()) if data.deductions else 0
    total_bonuses = sum(data.bonuses.values()) if data.bonuses else 0
    net = gross - total_deductions + total_bonuses

    # AI notes
    prompt = PAYROLL_AI_PROMPT.format(
        employee_name=emp.get("full_name", ""),
        base_salary=data.base_salary,
        attendance_days=attendance_days,
        working_days=working_days,
        deductions=data.deductions,
        bonuses=data.bonuses,
        gross_salary=round(gross, 2),
        net_salary=round(net, 2)
    )
    ai_result = await gemini.generate_json(prompt)

    record = supabase.table("payroll_records").insert({
        "period_id": data.period_id,
        "employee_id": data.employee_id,
        "base_salary": data.base_salary,
        "attendance_days": attendance_days,
        "working_days": working_days,
        "gross_salary": round(gross, 2),
        "deductions": data.deductions,
        "bonuses": data.bonuses,
        "net_salary": round(net, 2),
        "ai_notes": ai_result.get("notes", ""),
        "status": "draft"
    }).execute().data[0]

    return record
