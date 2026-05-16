import httpx
import logging
from app.config import get_settings

logger = logging.getLogger(__name__)

async def web_search(query: str) -> str:
    """
    Searches the web for the given query using Tavily API.
    
    Args:
        query: The search query string.
        
    Returns:
        A summary of the search results or an error message.
    """
    settings = get_settings()
    api_key = settings.TAVILY_API_KEY.strip()
    if not api_key:
        logger.warning("TAVILY_API_KEY not set. Web search tool is disabled.")
        return "Error: Web search is currently disabled (missing API key)."

    logger.info(f"Performing web search for: {query}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": api_key,
                    "query": query,
                    "search_depth": "advanced",
                    "include_answer": True
                },
                timeout=15.0
            )
            if response.status_code != 200:
                logger.error(f"Tavily Error Details: {response.text}")
            response.raise_for_status()
            data = response.json()
            
            # Prefer the direct answer if available
            if data.get("answer"):
                return data["answer"]
            
            # Otherwise, concatenate snippets
            results = data.get("results", [])
            if not results:
                return "No relevant search results found."
                
            summary = "\n".join([f"- {r['title']}: {r['content']} ({r['url']})" for r in results[:3]])
            return summary
            
        except Exception as e:
            logger.error(f"Tavily search error: {e}")
            return f"Error occurred while searching: {str(e)}"

# Registry of tools for Gemini
# Note: In a real app, this could be more sophisticated with auto-schema generation
TOOLS_SCHEMA = [
    {
        "function_declarations": [
            {
                "name": "web_search",
                "description": "Search the internet for real-time information, news, and facts.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query."
                        }
                    },
                    "required": ["query"]
                }
            }
        ]
    }
]

# Mapping of tool names to actual functions
TOOL_MAP = {
    "web_search": web_search
}
