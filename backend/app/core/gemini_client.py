import json
import logging
import google.generativeai as genai
from app.config import get_settings
from app.core.tools import TOOLS_SCHEMA, TOOL_MAP

logger = logging.getLogger(__name__)


class GeminiClient:
    def __init__(self):
        settings = get_settings()
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model_name = settings.GEMINI_MODEL
        # Default model without tools for basic tasks
        self.model = genai.GenerativeModel(self.model_name)
        # Model with tools for agentic tasks
        self.agent_model = genai.GenerativeModel(
            model_name=self.model_name,
            tools=TOOLS_SCHEMA
        )

    async def generate_text(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini text error: {e}")
            raise

    async def generate_json(self, prompt: str) -> dict | list:
        json_prompt = prompt + "\n\nIMPORTANT: Respond ONLY with valid JSON. No markdown, no explanation."
        try:
            response = self.model.generate_content(json_prompt)
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            return json.loads(text.strip())
        except json.JSONDecodeError as e:
            logger.error(f"Gemini JSON parse error: {e}")
            return {}
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            raise

    async def generate_with_tools(self, prompt: str) -> str:
        """
        Handles LLM generation with automatic tool execution (Function Calling).
        """
        try:
            chat = self.agent_model.start_chat(enable_automatic_function_calling=True)
            # We use a wrapper or manual loop if automatic calling is tricky in this env,
            # but enable_automatic_function_calling=True usually works well in recent SDK versions.
            response = chat.send_message(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini tool-calling error: {e}")
            return f"Error during agent execution: {str(e)}"
