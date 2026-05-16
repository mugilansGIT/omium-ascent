import logging
from app.agents.base_agent import BaseAgent
from app.core.event_bus import Events

logger = logging.getLogger(__name__)

TASK_PRIORITY_PROMPT = """
You are a project management AI. Analyze this task and provide recommendations.

Task: {title}
Description: {description}
Due Date: {due_date}
Current Status: {status}
Assigned To: {assigned_to}
Project: {project}

Provide:
1. Risk assessment if overdue
2. Suggested next actions
3. Whether to escalate to manager

Return JSON:
{{
  "risk_level": "low" | "medium" | "high" | "critical",
  "suggested_actions": ["action1", "action2"],
  "escalate": true/false,
  "escalation_reason": "...",
  "estimated_completion": "..."
}}
"""


class TaskAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="task_agent",
            subscribed_events=["agent:task_agent"]
        )

    async def process(self, message: dict) -> dict:
        event_type = message.get("event_type")

        if event_type == Events.TASK_OVERDUE:
            return await self._handle_overdue_task(message)
        elif event_type == Events.TASK_ASSIGNED:
            return await self._handle_task_assigned(message)

        return {"status": "unhandled"}

    async def _handle_overdue_task(self, message: dict) -> dict:
        task = message.get("task", {})

        emp = self.supabase.table("employees").select("full_name").eq(
            "id", task.get("assigned_to")
        ).single().execute().data if task.get("assigned_to") else {"full_name": "Unknown"}

        project = self.supabase.table("projects").select("name").eq(
            "id", task.get("project_id")
        ).single().execute().data if task.get("project_id") else {"name": "No Project"}

        prompt = TASK_PRIORITY_PROMPT.format(
            title=task.get("title", ""),
            description=task.get("description", ""),
            due_date=task.get("due_date", ""),
            status=task.get("status", ""),
            assigned_to=emp.get("full_name", "Unknown"),
            project=project.get("name", "No Project")
        )

        analysis = await self.gemini.generate_json(prompt)

        # Notify assignee
        if task.get("assigned_to"):
            await self.publish(Events.NOTIFY_USER, {
                "recipient_id": task["assigned_to"],
                "type": "task_overdue",
                "title": f"Task Overdue: {task.get('title', '')}",
                "body": f"Risk level: {analysis.get('risk_level')}. {', '.join(analysis.get('suggested_actions', []))}"
            })

        return analysis

    async def _handle_task_assigned(self, message: dict) -> dict:
        task = message.get("task", {})
        if task.get("assigned_to"):
            await self.publish(Events.NOTIFY_USER, {
                "recipient_id": task["assigned_to"],
                "type": "task_assigned",
                "title": f"New Task Assigned: {task.get('title', '')}",
                "body": f"Due: {task.get('due_date', 'No deadline')}. Priority: {task.get('priority', 'medium')}"
            })
        return {"status": "notified"}
