import logging
from app.agents.base_agent import BaseAgent
from app.core.event_bus import Events

logger = logging.getLogger(__name__)

PROCUREMENT_EMAIL_PROMPT = """
You are a professional procurement manager. Draft a formal vendor inquiry email.

Company: {company_name}
Address: {company_address}
Contact: {company_contact}

Product Required: {product_name}
Quantity: {quantity}
Target Budget: {budget} per unit
Delivery Required By: {delivery_date}
Specifications: {specifications}

Vendor: {vendor_name}
Vendor Contact: {vendor_email}

Write a professional, concise procurement inquiry email that:
1. Introduces our company
2. Specifies exact product requirements and quantity
3. Requests pricing, lead time, and MOQ
4. Mentions our target budget range
5. Asks about quality certifications
6. Requests sample availability
7. Provides our contact information

Return ONLY the email body (no subject line).
"""


class ProcurementAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="procurement_agent",
            subscribed_events=["agent:procurement_agent"]
        )

    async def process(self, message: dict) -> dict:
        req = message.get("procurement_request", {})
        recommendation = message.get("recommendation", {})

        top_vendor = recommendation.get("top_vendors", [{}])[0] if recommendation.get("top_vendors") else {}
        vendor_id = top_vendor.get("vendor_id")

        if not vendor_id:
            logger.warning("[ProcurementAgent] No vendor_id in recommendation")
            return {"status": "no_vendor"}

        vendor = self.supabase.table("vendors").select("*").eq(
            "id", vendor_id
        ).single().execute().data

        prompt = PROCUREMENT_EMAIL_PROMPT.format(
            company_name=self.settings.COMPANY_NAME,
            company_address=self.settings.COMPANY_ADDRESS,
            company_contact=self.settings.COMPANY_PHONE,
            product_name=req.get("product_name", ""),
            quantity=req.get("quantity", 1),
            budget=top_vendor.get("estimated_unit_price", "TBD"),
            delivery_date="30 days from confirmation",
            specifications=req.get("description", "Standard specifications"),
            vendor_name=vendor.get("name", ""),
            vendor_email=vendor.get("email", "")
        )

        email_body = await self.gemini.generate_text(prompt)

        po_number = f"PO-{self.settings.COMPANY_NAME[:3].upper()}-{req['id'][:8].upper()}"
        unit_price = top_vendor.get("estimated_unit_price", 0) or 0
        quantity = req.get("quantity", 1) or 1

        po = self.supabase.table("purchase_orders").insert({
            "po_number": po_number,
            "procurement_request_id": req["id"],
            "vendor_id": vendor_id,
            "items": [{
                "product": req.get("product_name"),
                "qty": quantity,
                "unit_price": unit_price,
                "total": quantity * unit_price
            }],
            "subtotal": quantity * unit_price,
            "tax": round(quantity * unit_price * 0.18, 2),
            "total": round(quantity * unit_price * 1.18, 2),
            "status": "draft",
            "ai_email_draft": email_body
        }).execute().data[0]

        await self.publish(Events.PO_DRAFT_READY, {
            "po_id": po["id"],
            "vendor": vendor,
            "email_draft": email_body
        })

        # Notify requester
        if req.get("requested_by"):
            await self.publish(Events.NOTIFY_USER, {
                "recipient_id": req["requested_by"],
                "type": "po_draft_ready",
                "title": f"Purchase Order Draft Ready: {po_number}",
                "body": f"Vendor: {vendor.get('name')}. Estimated total: ₹{quantity * unit_price:,.2f}"
            })

        return {"po_number": po_number, "status": "draft_created"}
