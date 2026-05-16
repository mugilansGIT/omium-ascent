from fastapi import APIRouter, Depends, HTTPException
from app.database import get_supabase
from app.models.meeting import MeetingCreate, MeetingTranscriptUpload
from app.core.security import get_current_user
from app.core.event_bus import EventBus, Events

router = APIRouter()


@router.get("/")
async def list_meetings(current_user=Depends(get_current_user)):
    supabase = get_supabase()
    return supabase.table("meetings").select(
        "*, employees!meetings_organizer_id_fkey(full_name)"
    ).order("scheduled_at", desc=True).execute().data


@router.get("/{meeting_id}")
async def get_meeting(meeting_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase()
    result = supabase.table("meetings").select(
        "*, meeting_attendees(*, employees(full_name, email))"
    ).eq("id", meeting_id).single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return result.data


@router.post("/")
async def create_meeting(data: MeetingCreate, current_user=Depends(get_current_user)):
    supabase = get_supabase()

    meeting_data = data.dict(exclude={"attendee_ids"})
    meeting_data["organizer_id"] = current_user["id"]
    meeting = supabase.table("meetings").insert(meeting_data).execute().data[0]

    # Add attendees
    for emp_id in (data.attendee_ids or []):
        supabase.table("meeting_attendees").insert({
            "meeting_id": meeting["id"],
            "employee_id": emp_id
        }).execute()

    return meeting


@router.post("/transcript")
async def upload_transcript(
    data: MeetingTranscriptUpload,
    current_user=Depends(get_current_user)
):
    supabase = get_supabase()
    event_bus = EventBus()

    supabase.table("meetings").update({
        "transcript": data.transcript
    }).eq("id", data.meeting_id).execute()

    await event_bus.publish(Events.MEETING_TRANSCRIPT, {
        "meeting_id": data.meeting_id,
        "transcript": data.transcript
    })

    return {"status": "processing", "message": "AI is summarizing the meeting"}
