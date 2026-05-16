from fastapi import APIRouter, Depends, HTTPException
from app.database import get_supabase
from app.models.procurement import ProcurementRequestCreate, ProcurementRequestUpdate
from app.core.security import get_current_user
from app.core.event_bus import EventBus, Events
from app.core.email_service import EmailService

router = APIRouter()


@router.get("/requests")
async def list_procurement_requests(current_user=Depends(get_current_user)):
    supabase = get_supabase()
    return supabase.table("procurement_requests").select(
        "*, employees(full_name), vendors(name)"
    ).order("created_at", desc=True).execute().data


@router.post("/request")
async def create_procurement_request(
    data: ProcurementRequestCreate,
    current_user=Depends(get_current_user)
):
    supabase = get_supabase()
    event_bus = EventBus()

    req = supabase.table("procurement_requests").insert({
        "requested_by": current_user["id"],
        "department_id": data.department_id,
        "product_name": data.product_name,
        "description": data.description,
        "quantity": data.quantity,
        "estimated_budget": data.estimated_budget,
        "urgency": data.urgency,
        "status": "pending"
    }).execute().data[0]

    await event_bus.publish(Events.PROCUREMENT_REQUEST, {
        "procurement_request": {**req, "category": data.category}
    })

    return {"id": req["id"], "status": "ai_processing"}


@router.get("/purchase-orders")
async def list_purchase_orders(current_user=Depends(get_current_user)):
    supabase = get_supabase()
    return supabase.table("purchase_orders").select(
        "*, vendors(name, email)"
    ).order("created_at", desc=True).execute().data


@router.get("/purchase-orders/{po_id}/email-draft")
async def get_po_email_draft(po_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase()
    po = supabase.table("purchase_orders").select("*").eq("id", po_id).single().execute().data
    if not po:
        raise HTTPException(status_code=404, detail="PO not found")
    return {"email_draft": po["ai_email_draft"], "po_number": po["po_number"]}


@router.post("/purchase-orders/{po_id}/send-email")
async def send_po_email(po_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase()
    email_svc = EmailService()

    po = supabase.table("purchase_orders").select(
        "*, vendors(*)"
    ).eq("id", po_id).single().execute().data
    if not po:
        raise HTTPException(status_code=404, detail="PO not found")

    await email_svc.send(
        to=po["vendors"]["email"],
        subject=f"Procurement Inquiry - {po['po_number']}",
        body=po["ai_email_draft"]
    )

    supabase.table("purchase_orders").update({
        "status": "sent",
        "email_sent_at": "now()"
    }).eq("id", po_id).execute()

    return {"status": "sent"}
