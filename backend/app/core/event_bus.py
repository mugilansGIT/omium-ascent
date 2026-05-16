import json
import redis.asyncio as aioredis
from app.config import get_settings


class Events:
    # HR Events
    LEAVE_REQUESTED     = "hr:leave:requested"
    LEAVE_APPROVED      = "hr:leave:approved"
    LEAVE_REJECTED      = "hr:leave:rejected"
    EMPLOYEE_ONBOARDED  = "hr:employee:onboarded"

    # Task Events
    TASK_ASSIGNED       = "task:assigned"
    TASK_OVERDUE        = "task:overdue"
    TASK_COMPLETED      = "task:completed"

    # Meeting Events
    MEETING_TRANSCRIPT  = "meeting:transcript_ready"
    MEETING_SUMMARIZED  = "meeting:summarized"

    # Procurement Events
    PROCUREMENT_REQUEST = "procurement:requested"
    VENDOR_ANALYZED     = "procurement:vendor_analyzed"
    PO_DRAFT_READY      = "procurement:po_draft_ready"

    # Trend Events
    TREND_SCAN_START    = "trend:scan_requested"
    TREND_FOUND         = "trend:found"

    # Notifications
    NOTIFY_USER         = "notification:send"


class EventBus:
    def __init__(self):
        self.settings = get_settings()
        self._redis = None

    async def get_redis(self):
        if not self._redis:
            self._redis = await aioredis.from_url(
                self.settings.REDIS_URL,
                decode_responses=True
            )
        return self._redis

    async def publish(self, stream: str, payload: dict) -> str:
        r = await self.get_redis()
        msg_id = await r.xadd(stream, {"data": json.dumps(payload)})
        return msg_id

    async def consume(
        self,
        stream: str,
        consumer_group: str,
        count: int = 10,
        block_ms: int = 100
    ) -> list[dict]:
        r = await self.get_redis()

        try:
            await r.xgroup_create(stream, consumer_group, id="0", mkstream=True)
        except Exception:
            pass

        messages = await r.xreadgroup(
            groupname=consumer_group,
            consumername=consumer_group,
            streams={stream: ">"},
            count=count,
            block=block_ms
        )

        result = []
        for stream_name, stream_messages in (messages or []):
            for msg_id, fields in stream_messages:
                try:
                    data = json.loads(fields["data"])
                    data["_redis_id"] = msg_id
                    data["_stream"] = stream_name
                    result.append(data)
                    await r.xack(stream_name, consumer_group, msg_id)
                except Exception:
                    pass

        return result
