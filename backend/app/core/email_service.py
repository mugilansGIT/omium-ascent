import logging
import resend
from app.config import get_settings

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        settings = get_settings()
        resend.api_key = settings.RESEND_API_KEY
        self.from_email = settings.EMAIL_FROM

    async def send(self, to: str, subject: str, body: str, html: str = None) -> dict:
        settings = get_settings()
        if not settings.RESEND_API_KEY or settings.RESEND_API_KEY == "your_resend_api_key":
             # If it looks like a placeholder or is missing, simulate
             logger.info(f"--- SIMULATED EMAIL ---")
             logger.info(f"To: {to}")
             logger.info(f"Subject: {subject}")
             logger.info(f"Body: {body}")
             logger.info(f"-----------------------")
             return {"id": "simulated", "status": "sent"}

        try:
            params = {
                "from": self.from_email,
                "to": [to],
                "subject": subject,
            }
            if html:
                params["html"] = html
            else:
                params["text"] = body

            response = resend.Emails.send(params)
            logger.info(f"Email sent to {to}: {response}")
            return response
        except Exception as e:
            logger.error(f"Email send error: {e}")
            # Even on error, log the content for the demo
            logger.info(f"--- EMAIL CONTENT (Failed to send) ---")
            logger.info(f"To: {to}\nSubject: {subject}\nBody: {body}")
            logger.info(f"---------------------------------------")
            return {"status": "failed", "error": str(e)}
