from fastapi import APIRouter, HTTPException
from app.core.event_bus import EventBus, Events
from app.core.tools import web_search
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/trigger/webhook")
async def demo_webhook():
    """Simulates an incoming webhook from GitHub."""
    bus = EventBus()
    await bus.publish("webhook:github", {
        "event_type": "webhook:github",
        "action": "demo_trigger",
        "message": "This is a simulated webhook for demonstration."
    })
    return {"status": "success", "message": "Simulated GitHub webhook published to EventBus"}

@router.post("/trigger/search")
async def demo_search(query: str = "Latest AI trends 2024"):
    """Demonstrates the Web Search tool (Tavily) directly."""
    try:
        result = await web_search(query)
        return {"status": "success", "query": query, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trigger/task-agent")
async def demo_task_agent():
    """Triggers the Task Agent to check for overdue tasks (Long Task demo)."""
    bus = EventBus()
    await bus.publish(Events.TASK_OVERDUE, {
        "event_type": Events.TASK_OVERDUE,
        "task_id": "demo-task-id",
        "title": "Demonstration Task",
        "due_date": "2020-01-01" # Clearly overdue
    })
    return {"status": "success", "message": "Overdue task event published. Task Agent will now process it in background."}

@router.post("/trigger/trend-scan")
async def demo_trend_scan():
    """Triggers the Trend Agent to perform a full web scan (Tool Calling demo)."""
    bus = EventBus()
    await bus.publish(Events.TREND_SCAN_START, {
        "event_type": Events.TREND_SCAN_START,
        "trigger": "manual_demo"
    })
    return {"status": "success", "message": "Trend scan started. Trend Agent will use Web Search + Gemini Tool Calling."}

@router.post("/trigger/leave-request")
async def demo_leave_request(email: str = "peter@stark.com"):
    """Simulates an employee requesting leave to trigger HR Agent."""
    from app.database import get_supabase
    supabase = get_supabase()
    
    # Get employee
    emp = supabase.table("employees").select("*").eq("email", email).single().execute().data
    if not emp:
        raise HTTPException(status_code=404, detail="Seeded employee not found. Run seed_data.sql first.")
    
    # Create leave entry
    leave = supabase.table("leaves").insert({
        "employee_id": emp["id"],
        "leave_type": "vacation",
        "policy_id": "annual",
        "start_date": "2024-06-01",
        "end_date": "2024-06-05",
        "total_days": 4,
        "reason": "Family trip to Queens",
        "status": "pending"
    }).execute().data[0]
    
    bus = EventBus()
    await bus.publish(Events.LEAVE_REQUESTED, {
        "event_type": Events.LEAVE_REQUESTED,
        "leave_request": leave
    })
    
    return {
        "status": "success", 
        "message": f"Leave requested for {emp['full_name']}. HR Agent is now evaluating it.",
        "leave_id": leave["id"]
    }

@router.post("/trigger/meeting-sync")
async def demo_meeting_sync():
    """Simulates a meeting transcript being saved to trigger Meeting Agent."""
    bus = EventBus()
    await bus.publish(Events.MEETING_TRANSCRIPT, {
        "event_type": Events.MEETING_TRANSCRIPT,
        "meeting_id": "arc-reactor-sync-001",
        "title": "Arc Reactor Core Sync",
        "transcript": "Tony: We need the thermal shielding done by Friday. Peter: I'm on it, but I need Bruce to sign off on the alloys. Bruce: Sign-off granted. Happy, make sure the perimeter is secure for the test."
    })
    return {"status": "success", "message": "Meeting transcript published. Meeting Agent will now extract action items."}
