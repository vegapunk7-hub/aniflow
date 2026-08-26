"""HTTP client with retry logic and session management."""

from __future__ import annotations

import asyncio
from typing import Any

import aiohttp
from aiohttp import ClientSession, TCPConnector

from aniflow.config import get_config
from aniflow.tls import create_ssl_context


class HttpClient:
    """Async HTTP client with retry logic and connection pooling."""

    def __init__(self, max_retries: int = 5, timeout: int | None = None) -> None:
        """Initialize HTTP client.

        Args:
            max_retries: Maximum number of retry attempts
            timeout: Request timeout in seconds
        """
        self.max_retries = max_retries
        self.timeout = timeout or get_config().timeout_seconds
        self.session: ClientSession | None = None

    async def __aenter__(self) -> HttpClient:
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def start(self) -> None:
        """Start the HTTP session."""
        if self.session is None:
            connector = TCPConnector(
                limit=0,  # No global limit
                limit_per_host=get_config().hls_workers,
                ttl_dns_cache=300,
                ssl=create_ssl_context(),
            )
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = ClientSession(
                connector=connector,
                timeout=timeout,
                headers={"User-Agent": self._get_user_agent()},
            )

    async def close(self) -> None:
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None

    async def get(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> str:
        """Perform GET request with retry logic.

        Args:
            url: Target URL
            headers: Additional headers
            **kwargs: Additional aiohttp arguments

        Returns:
            Response text
        """
        if self.session is None:
            await self.start()

        merged_headers = self.session.headers.copy()
        if headers:
            merged_headers.update(headers)

        for attempt in range(self.max_retries):
            try:
                async with self.session.get(
                    url, headers=merged_headers, **kwargs
                ) as response:
                    response.raise_for_status()
                    return await response.text()
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt == self.max_retries - 1:
                    raise
                wait_time = 0.5 * (2 ** attempt)
                await asyncio.sleep(wait_time)

        raise RuntimeError(f"Failed to fetch {url} after {self.max_retries} attempts")

    async def get_bytes(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> bytes:
        """Perform GET request and return bytes with retry logic.

        Args:
            url: Target URL
            headers: Additional headers
            **kwargs: Additional aiohttp arguments

        Returns:
            Response bytes
        """
        if self.session is None:
            await self.start()

        merged_headers = self.session.headers.copy()
        if headers:
            merged_headers.update(headers)

        for attempt in range(self.max_retries):
            try:
                async with self.session.get(
                    url, headers=merged_headers, **kwargs
                ) as response:
                    response.raise_for_status()
                    return await response.read()
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt == self.max_retries - 1:
                    raise
                wait_time = 0.5 * (2 ** attempt)
                await asyncio.sleep(wait_time)

        raise RuntimeError(f"Failed to fetch {url} after {self.max_retries} attempts")

    async def post(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> str:
        """Perform POST request with retry logic.

        Args:
            url: Target URL
            data: POST data
            headers: Additional headers
            **kwargs: Additional aiohttp arguments

        Returns:
            Response text
        """
        if self.session is None:
            await self.start()

        merged_headers = self.session.headers.copy()
        if headers:
            merged_headers.update(headers)

        for attempt in range(self.max_retries):
            try:
                async with self.session.post(
                    url, json=data, headers=merged_headers, **kwargs
                ) as response:
                    response.raise_for_status()
                    return await response.text()
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt == self.max_retries - 1:
                    raise
                wait_time = 0.5 * (2 ** attempt)
                await asyncio.sleep(wait_time)

        raise RuntimeError(f"Failed to post to {url} after {self.max_retries} attempts")

    @staticmethod
    def _get_user_agent() -> str:
        """Get user agent string."""
        return (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )
