import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from app.core.event_bus import EventBus
from app.core.gemini_client import GeminiClient
from app.database import get_supabase
from app.config import get_settings

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    def __init__(self, name: str, subscribed_events: list[str], use_tools: bool = False):
        self.name = name
        self.subscribed_events = subscribed_events
        self.use_tools = use_tools
        self.settings = get_settings()
        self.event_bus = EventBus()
        self.gemini = GeminiClient()
        self.supabase = get_supabase()
        self.running = False

    async def start(self):
        self.running = True
        logger.info(f"[{self.name}] Agent started, listening for: {self.subscribed_events}")
        await asyncio.gather(
            self._listen_loop(),
            self._heartbeat_loop()
        )

    async def stop(self):
        self.running = False
        logger.info(f"[{self.name}] Agent stopped")

    async def _listen_loop(self):
        while self.running:
            try:
                for event_type in self.subscribed_events:
                    messages = await self.event_bus.consume(
                        stream=event_type,
                        consumer_group=self.name,
                        count=10
                    )
                    for message in messages:
                        await self._process_with_tracking(message)
            except Exception as e:
                logger.error(f"[{self.name}] Listen error: {e}")
            await asyncio.sleep(0.5)

    async def _process_with_tracking(self, message: dict):
        start_time = datetime.utcnow()
        event_id = None
        try:
            result = self.supabase.table("agent_events").insert({
                "agent_name": self.name,
                "event_type": message.get("event_type") or message.get("_stream", "unknown"),
                "payload": message,
                "status": "processing"
            }).execute()
            event_id = result.data[0]["id"]

            output = await self.process(message)

            elapsed = (datetime.utcnow() - start_time).microseconds // 1000
            self.supabase.table("agent_events").update({
                "status": "success",
                "result": output,
                "processing_time_ms": elapsed
            }).eq("id", event_id).execute()

        except Exception as e:
            logger.error(f"[{self.name}] Processing error: {e}")
            if event_id:
                self.supabase.table("agent_events").update({
                    "status": "failed",
                    "error_message": str(e)
                }).eq("id", event_id).execute()

    async def publish(self, event_type: str, payload: dict):
        await self.event_bus.publish(event_type, {
            "source_agent": self.name,
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            **payload
        })

    async def _heartbeat_loop(self):
        while self.running:
            await asyncio.sleep(30)
            logger.debug(f"[{self.name}] heartbeat")

    @abstractmethod
    async def process(self, message: dict) -> dict:
        pass
