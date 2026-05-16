from fastapi import APIRouter, Depends, Query
from app.database import get_supabase
from app.core.security import get_current_user
from app.core.gemini_client import GeminiClient
from datetime import datetime, timedelta

router = APIRouter()

REPORT_PROMPT = """
Generate an executive summary report for this company data.

Period: {period}
Data:
{data}

Return JSON:
{{
  "executive_summary": "...",
  "highlights": ["..."],
  "concerns": ["..."],
  "recommendations": ["..."],
  "kpis": {{
    "overall_health": "good/warning/critical",
    "productivity_score": 0-100,
    "attendance_rate": "...",
    "tasks_completion_rate": "..."
  }}
}}
"""


@router.get("/dashboard")
async def get_dashboard_stats(current_user=Depends(get_current_user)):
    supabase = get_supabase()

    employees = supabase.table("employees").select("id, status").execute().data
    tasks = supabase.table("tasks").select("id, status, priority").execute().data
    leaves = supabase.table("leaves").select("id, status").execute().data
    procurements = supabase.table("procurement_requests").select("id, status").execute().data

    return {
        "employees": {
            "total": len(employees),
            "active": len([e for e in employees if e["status"] == "active"]),
        },
        "tasks": {
            "total": len(tasks),
            "in_progress": len([t for t in tasks if t["status"] == "in_progress"]),
            "done": len([t for t in tasks if t["status"] == "done"]),
            "overdue": len([t for t in tasks if t["status"] not in ["done", "cancelled"]]),
        },
        "leaves": {
            "pending": len([l for l in leaves if l["status"] == "pending"]),
            "approved": len([l for l in leaves if "approved" in l["status"]]),
        },
        "procurement": {
            "pending": len([p for p in procurements if p["status"] == "pending"]),
            "total": len(procurements)
        }
    }


@router.get("/ai-summary")
async def get_ai_summary(current_user=Depends(get_current_user)):
    supabase = get_supabase()
    gemini = GeminiClient()

    since = (datetime.utcnow() - timedelta(days=7)).isoformat()

    tasks = supabase.table("tasks").select("title, status, priority, due_date").gte(
        "created_at", since
    ).execute().data

    leaves = supabase.table("leaves").select(
        "total_days, status, start_date"
    ).gte("created_at", since).execute().data

    agent_events = supabase.table("agent_events").select(
        "agent_name, status, created_at"
    ).gte("created_at", since).execute().data

    data = {"tasks": tasks[:20], "leaves": leaves[:20], "agent_events": agent_events[:20]}

    prompt = REPORT_PROMPT.format(
        period="Last 7 days",
        data=str(data)[:5000]
    )

    report = await gemini.generate_json(prompt)
    return report

@router.get("/agent-events")
async def get_agent_events(
    limit: int = Query(20),
    current_user=Depends(get_current_user)
):
    supabase = get_supabase()
    result = supabase.table("agent_events").select("*").order(
        "created_at", desc=True
    ).limit(limit).execute()
    return result.data
