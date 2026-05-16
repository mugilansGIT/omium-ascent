import httpx
import logging
import re
from app.agents.base_agent import BaseAgent
from app.core.event_bus import Events

logger = logging.getLogger(__name__)

TREND_ANALYSIS_PROMPT = """
Analyze these product mentions from the internet and identify trending products.

Data collected:
{raw_data}

For each trending product, assess:
1. Trend score (0-1): How much is this being talked about?
2. Longevity: short_term (< 3 months), medium_term (3-12 months), long_term (> 1 year)
3. Sustainability score (0-1): Is this a fad or durable trend?
4. Category

Return JSON array:
[
  {{
    "product_name": "...",
    "category": "...",
    "trend_score": 0.85,
    "longevity_estimate": "medium_term",
    "sustainability_score": 0.72,
    "summary": "..."
  }}
]
"""


class TrendAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="trend_agent",
            subscribed_events=["agent:trend_agent"],
            use_tools=True
        )

    async def process(self, message: dict) -> dict:
        trend_data = await self._collect_trend_signals()

        prompt = TREND_ANALYSIS_PROMPT.format(raw_data=str(trend_data)[:8000])
        trends = await self.gemini.generate_json(prompt)

        if not isinstance(trends, list):
            trends = [trends] if trends else []

        for trend in trends:
            if trend.get("product_name"):
                self.supabase.table("product_trends").upsert(
                    trend, on_conflict="product_name"
                ).execute()

        await self.publish(Events.TREND_FOUND, {"trends": trends})
        return {"trends_found": len(trends)}

    async def _collect_trend_signals(self) -> dict:
        signals = {}

        async with httpx.AsyncClient(timeout=10) as client:
            try:
                r = await client.get(
                    "https://www.reddit.com/r/technology/hot.json?limit=25",
                    headers={"User-Agent": "TrendBot/1.0"}
                )
                posts = r.json().get("data", {}).get("children", [])
                signals["reddit"] = [p["data"]["title"] for p in posts[:20]]
            except Exception as e:
                logger.warning(f"Reddit fetch failed: {e}")
                signals["reddit"] = []

            try:
                r = await client.get(
                    "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US"
                )
                titles = re.findall(r'<title><!\[CDATA\[(.*?)\]\]>', r.text)
                signals["google_trends"] = titles[:20]
            except Exception as e:
                logger.warning(f"Google Trends fetch failed: {e}")
                signals["google_trends"] = []

        return signals
