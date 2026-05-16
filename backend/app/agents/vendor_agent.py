import logging
from app.agents.base_agent import BaseAgent
from app.core.event_bus import Events

logger = logging.getLogger(__name__)

VENDOR_ANALYSIS_PROMPT = """
You are a procurement intelligence AI. Analyze available vendor data for: {product_name}

Category: {category}
Budget: {budget}
Quantity needed: {quantity}

Vendor candidates from DB:
{vendors}

Evaluate each vendor on:
- Price competitiveness
- Reliability indicators
- Quality signals
- Delivery reliability

Recommend the TOP 3 vendors. Return JSON:
{{
  "top_vendors": [
    {{
      "vendor_id": "...",
      "vendor_name": "...",
      "score": 0.85,
      "estimated_unit_price": 1500,
      "rationale": "...",
      "risks": "..."
    }}
  ],
  "recommendation_summary": "...",
  "suggested_quantity": 100
}}
"""

VENDOR_SCORE_UPDATE_PROMPT = """
Based on these market trends, update vendor scores for the relevant categories.

Trends: {trends}
Current vendors: {vendors}

Return JSON array of vendor updates:
[
  {{
    "vendor_id": "...",
    "price_competitiveness": 0.0-1.0,
    "reliability_score": 0.0-1.0,
    "quality_score": 0.0-1.0,
    "analysis_notes": "..."
  }}
]
"""


class VendorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="vendor_agent",
            subscribed_events=["agent:vendor_agent"]
        )

    async def process(self, message: dict) -> dict:
        event_type = message.get("event_type")

        if event_type == Events.PROCUREMENT_REQUEST:
            return await self._analyze_for_request(message)
        elif event_type == Events.TREND_FOUND:
            return await self._update_vendor_scores_for_trends(message)

        return {"status": "unhandled"}

    async def _analyze_for_request(self, message: dict) -> dict:
        req = message.get("procurement_request", {})
        product_name = req.get("product_name")
        category = req.get("category", "")

        vendors = self.supabase.table("vendors").select(
            "*, vendor_products(*)"
        ).eq("category", category).execute().data

        if not vendors:
            vendors = self.supabase.table("vendors").select("*, vendor_products(*)").execute().data

        prompt = VENDOR_ANALYSIS_PROMPT.format(
            product_name=product_name,
            category=category,
            budget=req.get("estimated_budget", "Not specified"),
            quantity=req.get("quantity", 1),
            vendors=str(vendors)[:6000]
        )

        recommendation = await self.gemini.generate_json(prompt)

        self.supabase.table("procurement_requests").update({
            "ai_recommendation": recommendation,
            "status": "ai_processed"
        }).eq("id", req["id"]).execute()

        await self.publish(Events.VENDOR_ANALYZED, {
            "procurement_request": req,
            "recommendation": recommendation
        })

        return recommendation

    async def _update_vendor_scores_for_trends(self, message: dict) -> dict:
        trends = message.get("trends", [])
        vendors = self.supabase.table("vendors").select("id, name, category").execute().data

        prompt = VENDOR_SCORE_UPDATE_PROMPT.format(
            trends=str(trends)[:3000],
            vendors=str(vendors)[:3000]
        )

        updates = await self.gemini.generate_json(prompt)
        if not isinstance(updates, list):
            return {"status": "no_updates"}

        for update in updates:
            vendor_id = update.pop("vendor_id", None)
            if vendor_id:
                self.supabase.table("vendors").update({
                    "price_competitiveness": update.get("price_competitiveness"),
                    "reliability_score": update.get("reliability_score"),
                    "quality_score": update.get("quality_score"),
                    "ai_analysis": update
                }).eq("id", vendor_id).execute()

        return {"updated": len(updates)}
