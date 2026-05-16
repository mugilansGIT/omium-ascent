import logging
import omium
from app.agents.base_agent import BaseAgent
from app.core.event_bus import Events

logger = logging.getLogger(__name__)

LEAVE_POLICY_PROMPT = """
You are an HR policy AI for a company. Evaluate this leave request.

Employee: {employee_name}
Leave type: {leave_type}
Duration: {total_days} days ({start_date} to {end_date})
Reason: {reason}
Remaining balance: {remaining_balance} days
Team size: {team_size}
Others on leave same period: {others_on_leave}

Rules:
1. Auto-approve if <= 2 days AND reason is valid AND balance is sufficient AND <50% team on leave
2. Reject if balance insufficient
3. Escalate if > 5 days OR critical project deadline within period OR full team overlap

Respond in JSON:
{{
  "decision": "auto_approve" | "reject" | "escalate",
  "confidence": 0.0-1.0,
  "reason": "short explanation",
  "notify_manager": true/false
}}
"""

ONBOARDING_PROMPT = """
Create a personalized onboarding checklist and welcome message for a new employee.

Name: {full_name}
Role: {role}
Department: {department}
Start Date: {join_date}

Return JSON:
{{
  "welcome_message": "...",
  "checklist": ["item1", "item2", ...],
  "first_week_goals": ["goal1", "goal2", ...]
}}
"""


class HRAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="hr_agent",
            subscribed_events=["agent:hr_agent"]
        )

    async def process(self, message: dict) -> dict:
        event_type = message.get("event_type")

        if event_type == Events.LEAVE_REQUESTED:
            return await self._handle_leave_request(message)
        elif event_type == Events.EMPLOYEE_ONBOARDED:
            return await self._handle_onboarding(message)

        return {"status": "unhandled"}

    @omium.trace(name="Handle Leave Request")
    async def _handle_leave_request(self, message: dict) -> dict:
        leave_data = message.get("leave_request", {})
        employee_id = leave_data.get("employee_id")

        emp = self.supabase.table("employees").select(
            "*, departments!employees_department_id_fkey(name)"
        ).eq("id", employee_id).single().execute().data

        balance_data = self.supabase.table("leave_balances").select("*").eq(
            "employee_id", employee_id
        ).eq("policy_id", leave_data["policy_id"]).execute().data
        
        balance = balance_data[0] if balance_data else None

        team_leaves = self.supabase.table("leaves").select("id").eq(
            "status", "approved"
        ).execute()

        prompt = LEAVE_POLICY_PROMPT.format(
            employee_name=emp["full_name"],
            leave_type=leave_data.get("leave_type", ""),
            total_days=leave_data["total_days"],
            start_date=leave_data["start_date"],
            end_date=leave_data["end_date"],
            reason=leave_data.get("reason", "Not provided"),
            remaining_balance=(balance["total_days"] - balance["used_days"]) if balance else 0,
            team_size=10,
            others_on_leave=len(team_leaves.data) if team_leaves.data else 0
        )

        try:
            ai_response = await self.gemini.generate_json(prompt)
            decision = ai_response.get("decision")
        except Exception as e:
            logger.warning(f"[HRAgent] Gemini failed, using rule-based fallback: {e}")
            # Fallback rules
            if leave_data["total_days"] <= 2:
                decision = "auto_approve"
                reason = "Request is for 2 days or less. Auto-approved via fallback policy."
            else:
                decision = "escalate"
                reason = "Request duration requires manager review. Escalated via fallback policy."
            
            ai_response = {
                "decision": decision,
                "confidence": 0.5,
                "reason": reason,
                "notify_manager": decision == "escalate"
            }

        new_status = {
            "auto_approve": "ai_approved",
            "reject": "rejected",
            "escalate": "escalated"
        }.get(decision, "escalated")

        self.supabase.table("leaves").update({
            "status": new_status,
            "ai_decision": ai_response
        }).eq("id", leave_data["id"]).execute()

        await self.publish(Events.NOTIFY_USER, {
            "recipient_id": employee_id,
            "type": f"leave_{new_status}",
            "title": f"Leave Request {new_status.replace('_', ' ').title()}",
            "body": ai_response.get("reason", "")
        })

        return {"decision": new_status, "ai_response": ai_response}

    async def _handle_onboarding(self, message: dict) -> dict:
        emp = message.get("employee", {})
        prompt = ONBOARDING_PROMPT.format(
            full_name=emp.get("full_name", ""),
            role=emp.get("role", ""),
            department=emp.get("department", ""),
            join_date=emp.get("join_date", "")
        )
        result = await self.gemini.generate_json(prompt)

        self.supabase.table("employees").update({
            "metadata": {"onboarding": result}
        }).eq("id", emp["id"]).execute()

        await self.publish(Events.NOTIFY_USER, {
            "recipient_id": emp["id"],
            "type": "onboarding_welcome",
            "title": f"Welcome to {self.settings.COMPANY_NAME}, {emp.get('full_name')}!",
            "body": result.get("welcome_message", "")
        })

        return result
