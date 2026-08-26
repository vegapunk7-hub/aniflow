"""FlareSolverr client for Cloudflare bypass."""

from __future__ import annotations

import asyncio
from typing import Any

from aniflow.config import get_config
from aniflow.http import HttpClient


class FlareSolverrError(Exception):
    """Raised when FlareSolverr request fails."""

    pass


class FlareSolverrClient:
    """Client for FlareSolverr Cloudflare bypass service."""

    def __init__(self, base_url: str | None = None) -> None:
        """Initialize FlareSolverr client.

        Args:
            base_url: FlareSolverr API base URL
        """
        self.base_url = base_url or get_config().flaresolverr_url
        self.http = HttpClient(max_retries=3)
        self.session_id: str | None = None

    async def start(self) -> None:
        """Start HTTP session."""
        await self.http.start()

    async def close(self) -> None:
        """Close HTTP session."""
        await self.http.close()

    async def check_health(self) -> bool:
        """Check if FlareSolverr is running.

        Returns:
            True if FlareSolverr is accessible
        """
        try:
            await self.start()
            response = await self.http.get(f"{self.base_url}/v1/healthcheck")
            return "OK" in response
        except Exception:
            return False
        finally:
            await self.close()

    async def create_session(self) -> str:
        """Create a new FlareSolverr session.

        Returns:
            Session ID
        """
        await self.start()
        payload = {"cmd": "sessions.create"}

        try:
            response_text = await self.http.post(f"{self.base_url}/v1", data=payload)
            # Response format: {"success": true, "session": "session_id", ...}
            import json
            response_data = json.loads(response_text)
            if response_data.get("success"):
                self.session_id = response_data.get("session")
                return self.session_id
            else:
                raise FlareSolverrError(
                    f"Failed to create session: {response_data.get('message')}"
                )
        except Exception as e:
            raise FlareSolverrError(f"Session creation failed: {e}")

    async def fetch_page(
        self,
        url: str,
        max_timeout: int = 60000,
    ) -> dict[str, Any]:
        """Fetch a page through FlareSolverr with Cloudflare bypass.

        Args:
            url: Target URL
            max_timeout: Maximum timeout in milliseconds

        Returns:
            Response data with cookies and content
        """
        if not self.session_id:
            await self.create_session()

        await self.start()
        payload = {
            "cmd": "request.get",
            "url": url,
            "maxTimeout": max_timeout,
            "session": self.session_id,
        }

        try:
            response_text = await self.http.post(f"{self.base_url}/v1", data=payload)
            import json
            response_data = json.loads(response_text)

            if response_data.get("success"):
                return response_data.get("solution", {})
            else:
                error_msg = response_data.get("message", "Unknown error")
                if "session" in error_msg.lower():
                    # Session expired, create new one
                    self.session_id = None
                    return await self.fetch_page(url, max_timeout)
                raise FlareSolverrError(f"Page fetch failed: {error_msg}")
        except Exception as e:
            raise FlareSolverrError(f"Page fetch error: {e}")

    async def get_page_content(
        self,
        url: str,
        max_timeout: int = 60000,
    ) -> tuple[str, dict[str, str]]:
        """Get page content and cookies from URL.

        Args:
            url: Target URL
            max_timeout: Maximum timeout in milliseconds

        Returns:
            Tuple of (page content, cookies dict)
        """
        solution = await self.fetch_page(url, max_timeout)
        content = solution.get("pageContent", "")
        cookies_str = solution.get("cookies", "")

        # Parse cookies from string format
        cookies = {}
        if cookies_str:
            for cookie in cookies_str.split("; "):
                if "=" in cookie:
                    key, value = cookie.split("=", 1)
                    cookies[key.strip()] = value.strip()

        return content, cookies
