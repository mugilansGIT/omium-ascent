import logging
from datetime import datetime, timezone
from app.agents.base_agent import BaseAgent
from app.core.event_bus import Events

logger = logging.getLogger(__name__)


class OrchestratorAgent(BaseAgent):
    ROUTING_TABLE = {
        Events.LEAVE_REQUESTED:     "hr_agent",
        Events.TASK_OVERDUE:        "notification_agent",
        Events.MEETING_TRANSCRIPT:  "meeting_agent",
        Events.PROCUREMENT_REQUEST: "vendor_agent",
        Events.VENDOR_ANALYZED:     "procurement_agent",
        Events.TREND_SCAN_START:    "trend_agent",
        Events.TREND_FOUND:         "vendor_agent",
        Events.NOTIFY_USER:         "notification_agent",
    }

    def __init__(self):
        super().__init__(
            name="orchestrator",
            subscribed_events=list(self.ROUTING_TABLE.keys())
        )

    async def process(self, message: dict) -> dict:
        event_type = message.get("event_type")
        target_agent = self.ROUTING_TABLE.get(event_type)

        if not target_agent:
            logger.warning(f"[Orchestrator] No handler for event: {event_type}")
            return {"status": "no_handler"}

        logger.info(f"[Orchestrator] Routing {event_type} → {target_agent}")
        await self.publish(
            event_type=f"agent:{target_agent}",
            payload=message
        )
        return {"routed_to": target_agent, "event": event_type}

    async def trigger_daily_tasks(self):
        await self.publish(Events.TREND_SCAN_START, {"trigger": "daily_cron"})
        await self._check_overdue_tasks()
        await self._send_daily_summary()

    async def _check_overdue_tasks(self):
        result = self.supabase.table("tasks").select("*").lt(
            "due_date", datetime.now(timezone.utc).isoformat()
        ).neq("status", "done").execute()

        for task in result.data:
            await self.publish(Events.TASK_OVERDUE, {"task": task})

    async def _send_daily_summary(self):
        logger.info("[Orchestrator] Daily summary triggered")
