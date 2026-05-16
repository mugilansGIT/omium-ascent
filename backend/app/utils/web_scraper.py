import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)


async def scrape_url(url: str, headers: Optional[dict] = None) -> str:
    """Fetch raw HTML content from a URL."""
    default_headers = {"User-Agent": "Mozilla/5.0 (compatible; AIOpsScraper/1.0)"}
    if headers:
        default_headers.update(headers)

    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        response = await client.get(url, headers=default_headers)
        response.raise_for_status()
        return response.text


async def scrape_json(url: str, headers: Optional[dict] = None) -> dict:
    """Fetch JSON from a URL."""
    default_headers = {"User-Agent": "Mozilla/5.0 (compatible; AIOpsScraper/1.0)"}
    if headers:
        default_headers.update(headers)

    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        response = await client.get(url, headers=default_headers)
        response.raise_for_status()
        return response.json()
