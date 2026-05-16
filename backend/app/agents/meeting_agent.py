import logging
from app.agents.base_agent import BaseAgent
from app.core.event_bus import Events

logger = logging.getLogger(__name__)

MEETING_SUMMARY_PROMPT = """
You are an executive assistant AI. Analyze this meeting transcript and extract key information.

Meeting Title: {title}
Meeting Type: {meeting_type}
Attendees: {attendees}
Transcript:
{transcript}

Extract and return JSON:
{{
  "summary": "2-3 sentence executive summary",
  "key_decisions": ["decision1", "decision2"],
  "action_items": [
    {{
      "description": "...",
      "assigned_to_name": "...",
      "due_date": "YYYY-MM-DD or null",
      "priority": "high/medium/low"
    }}
  ],
  "follow_up_meeting_needed": true/false,
  "sentiment": "positive/neutral/negative",
  "topics_discussed": ["topic1", "topic2"]
}}
"""


class MeetingAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="meeting_agent",
            subscribed_events=["agent:meeting_agent"]
        )

    async def process(self, message: dict) -> dict:
        event_type = message.get("event_type")

        if event_type == Events.MEETING_TRANSCRIPT:
            return await self._process_transcript(message)

        return {"status": "unhandled"}

    async def _process_transcript(self, message: dict) -> dict:
        meeting_id = message.get("meeting_id")
        transcript = message.get("transcript", "")

        meeting = self.supabase.table("meetings").select(
            "*, meeting_attendees(employee_id, employees(full_name))"
        ).eq("id", meeting_id).single().execute().data

        attendees = [
            a["employees"]["full_name"]
            for a in meeting.get("meeting_attendees", [])
            if a.get("employees")
        ]

        prompt = MEETING_SUMMARY_PROMPT.format(
            title=meeting.get("title", ""),
            meeting_type=meeting.get("meeting_type", ""),
            attendees=", ".join(attendees),
            transcript=transcript[:6000]
        )

        analysis = await self.gemini.generate_json(prompt)

        # Update meeting with AI summary
        self.supabase.table("meetings").update({
            "ai_summary": analysis.get("summary", ""),
            "action_items": analysis.get("action_items", []),
            "status": "completed"
        }).eq("id", meeting_id).execute()

        # Create action item tasks
        for item in analysis.get("action_items", []):
            self.supabase.table("meeting_action_items").insert({
                "meeting_id": meeting_id,
                "description": item.get("description", ""),
                "due_date": item.get("due_date"),
                "status": "open"
            }).execute()

        # Notify organizer
        await self.publish(Events.NOTIFY_USER, {
            "recipient_id": meeting.get("organizer_id"),
            "type": "meeting_summarized",
            "title": f"Meeting Summary Ready: {meeting.get('title')}",
            "body": analysis.get("summary", "")
        })

        await self.publish(Events.MEETING_SUMMARIZED, {
            "meeting_id": meeting_id,
            "analysis": analysis
        })

        return analysis
