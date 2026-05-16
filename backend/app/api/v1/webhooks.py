from fastapi import APIRouter, Request, Header, HTTPException
from app.core.event_bus import EventBus
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/receive/{source}")
async def receive_webhook(
    source: str, 
    request: Request,
    x_webhook_secret: str = Header(None)
):
    """
    Generic webhook receiver. 
    Publishes incoming payload to the event bus.
    """
    payload = await request.json()
    
    logger.info(f"Received webhook from {source}")
    
    event_bus = EventBus()
    await event_bus.publish(
        stream=f"webhook:{source}",
        payload={
            "event_type": f"webhook:{source}",
            "source": source,
            "data": payload,
            "received_at": request.state.__dict__.get("start_time", None)
        }
    )
    
    return {"status": "accepted", "source": source}
