from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
import uuid


class EmployeeBase(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    department_id: Optional[str] = None
    role: str
    designation: Optional[str] = None
    employment_type: str = "full_time"
    salary_base: Optional[float] = None
    join_date: date
    manager_id: Optional[str] = None

class EmployeeCreate(EmployeeBase):
    employee_code: str
    password: str

class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    department_id: Optional[str] = None
    role: Optional[str] = None
    designation: Optional[str] = None
    status: Optional[str] = None
    salary_base: Optional[float] = None

class EmployeeResponse(EmployeeBase):
    id: str
    employee_code: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
