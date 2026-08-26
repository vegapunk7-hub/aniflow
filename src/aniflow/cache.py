"""In-memory TTL cache with async safety."""

from __future__ import annotations

import asyncio
import time
from collections import OrderedDict
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class TTLCache(Generic[T]):
    """Thread-safe TTL cache with LRU eviction."""

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600) -> None:
        """Initialize cache.

        Args:
            max_size: Maximum cache size
            ttl_seconds: Time-to-live for entries in seconds
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: OrderedDict[str, tuple[T, float]] = OrderedDict()
        self.lock = asyncio.Lock()

    async def get(self, key: str) -> T | None:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        async with self.lock:
            if key not in self.cache:
                return None

            value, timestamp = self.cache[key]
            if time.time() - timestamp > self.ttl_seconds:
                del self.cache[key]
                return None

            # Move to end (LRU)
            self.cache.move_to_end(key)
            return value

    async def set(self, key: str, value: T) -> None:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        async with self.lock:
            if key in self.cache:
                del self.cache[key]
            elif len(self.cache) >= self.max_size:
                # Remove oldest (LRU)
                self.cache.popitem(last=False)

            self.cache[key] = (value, time.time())

    async def clear(self) -> None:
        """Clear all cache entries."""
        async with self.lock:
            self.cache.clear()

    async def size(self) -> int:
        """Get current cache size."""
        async with self.lock:
            return len(self.cache)
