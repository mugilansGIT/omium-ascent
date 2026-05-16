from fastapi import APIRouter, Depends, HTTPException, Query
from app.database import get_supabase
from app.models.vendor import VendorCreate, VendorUpdate, VendorProductCreate
from app.core.security import get_current_user

router = APIRouter()


@router.get("/")
async def list_vendors(
    category: str = Query(None),
    verified: bool = Query(None),
    current_user=Depends(get_current_user)
):
    supabase = get_supabase()
    query = supabase.table("vendors").select("*, vendor_products(*)")

    if category:
        query = query.eq("category", category)
    if verified is not None:
        query = query.eq("verified", verified)

    return query.order("reliability_score", desc=True).execute().data


@router.get("/{vendor_id}")
async def get_vendor(vendor_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase()
    result = supabase.table("vendors").select(
        "*, vendor_products(*)"
    ).eq("id", vendor_id).single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return result.data


@router.post("/")
async def create_vendor(data: VendorCreate, current_user=Depends(get_current_user)):
    supabase = get_supabase()
    return supabase.table("vendors").insert(data.dict()).execute().data[0]


@router.patch("/{vendor_id}")
async def update_vendor(
    vendor_id: str,
    data: VendorUpdate,
    current_user=Depends(get_current_user)
):
    supabase = get_supabase()
    return supabase.table("vendors").update(
        data.dict(exclude_none=True)
    ).eq("id", vendor_id).execute().data[0]


@router.post("/products")
async def add_vendor_product(data: VendorProductCreate, current_user=Depends(get_current_user)):
    supabase = get_supabase()
    return supabase.table("vendor_products").insert(data.dict()).execute().data[0]
