import logging
from app.agents.base_agent import BaseAgent
from app.core.event_bus import Events
from app.core.email_service import EmailService

logger = logging.getLogger(__name__)


class NotificationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="notification_agent",
            subscribed_events=["agent:notification_agent"]
        )
        self.email_service = EmailService()

    async def process(self, message: dict) -> dict:
        event_type = message.get("event_type")

        if event_type == Events.NOTIFY_USER:
            return await self._send_notification(message)
        elif event_type == Events.TASK_OVERDUE:
            return await self._send_task_overdue(message)

        return {"status": "unhandled"}

    async def _send_notification(self, message: dict) -> dict:
        recipient_id = message.get("recipient_id")
        notif_type = message.get("type", "general")
        title = message.get("title", "")
        body = message.get("body", "")
        data = message.get("data", {})

        # Store in DB
        notif = self.supabase.table("notifications").insert({
            "recipient_id": recipient_id,
            "type": notif_type,
            "title": title,
            "body": body,
            "data": data,
            "sent_via": ["in_app"]
        }).execute().data[0]

        # Fetch employee email for email notification
        try:
            emp = self.supabase.table("employees").select("email, full_name").eq(
                "id", recipient_id
            ).single().execute().data

            # Target Email for Live Demo
            target_email = "23aids065@act.edu.in"
            
            # Send to both the actual employee AND the HR test email
            recipients = [target_email]
            if emp and emp.get("email"):
                recipients.append(emp["email"])

            for email_to in set(recipients):
                await self.email_service.send(
                    to=email_to,
                    subject=f"[AI OPS] {title}",
                    body=f"Hi {emp['full_name'] if emp else 'User'},\n\n{body}\n\n---\nSent by Stark AI Automation"
                )
            
            self.supabase.table("notifications").update({
                "sent_via": ["in_app", "email"]
            }).eq("id", notif["id"]).execute()

        except Exception as e:
            logger.warning(f"[NotificationAgent] Email send failed: {e}")

        return {"notification_id": notif["id"], "status": "sent"}

    async def _send_task_overdue(self, message: dict) -> dict:
        task = message.get("task", {})
        if task.get("assigned_to"):
            return await self._send_notification({
                "recipient_id": task["assigned_to"],
                "type": "task_overdue",
                "title": f"Task Overdue: {task.get('title', '')}",
                "body": f"Your task '{task.get('title')}' was due on {task.get('due_date')} and is still not completed.",
                "data": {"task_id": task.get("id")}
            })
        return {"status": "no_assignee"}
