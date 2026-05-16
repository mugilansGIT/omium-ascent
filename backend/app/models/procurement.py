from pydantic import BaseModel
from typing import Optional


class ProcurementRequestCreate(BaseModel):
    department_id: Optional[str] = None
    product_name: str
    description: Optional[str] = None
    quantity: int
    estimated_budget: Optional[float] = None
    urgency: str = "normal"
    category: Optional[str] = None

class ProcurementRequestUpdate(BaseModel):
    status: Optional[str] = None
    selected_vendor_id: Optional[str] = None
