from pydantic import BaseModel
from typing import Optional
from datetime import date


class PayrollPeriodCreate(BaseModel):
    period_name: str
    start_date: date
    end_date: date
    payment_date: Optional[date] = None

class PayrollRecordCreate(BaseModel):
    period_id: str
    employee_id: str
    base_salary: float
    attendance_days: Optional[int] = None
    working_days: Optional[int] = None
    deductions: Optional[dict] = {}
    bonuses: Optional[dict] = {}
