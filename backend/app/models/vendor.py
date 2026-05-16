from pydantic import BaseModel
from typing import Optional


class VendorCreate(BaseModel):
    name: str
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    category: Optional[str] = None

class VendorUpdate(BaseModel):
    name: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    category: Optional[str] = None
    verified: Optional[bool] = None

class VendorProductCreate(BaseModel):
    vendor_id: str
    product_name: str
    sku: Optional[str] = None
    unit_price: Optional[float] = None
    currency: str = "INR"
    minimum_order_quantity: int = 1
    lead_time_days: Optional[int] = None
