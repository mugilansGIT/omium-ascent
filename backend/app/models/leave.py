from pydantic import BaseModel
from typing import Optional
from datetime import date


class LeaveRequestCreate(BaseModel):
    policy_id: str
    start_date: date
    end_date: date
    total_days: float
    reason: Optional[str] = None

class LeaveRequestUpdate(BaseModel):
    status: Optional[str] = None
    rejection_reason: Optional[str] = None
