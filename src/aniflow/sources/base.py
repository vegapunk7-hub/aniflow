"""Base class for anime sources."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from aniflow.models import AnimeInfo, EpisodeInfo


class BaseSource(ABC):
    """Abstract base class for anime sources."""

    source_name: str
    supported_qualities: list[int] = [360, 720, 1080]

    @abstractmethod
    async def search(self, query: str) -> list[AnimeInfo]:
        """Search for anime by title."""
        pass

    @abstractmethod
    async def get_anime_info(self, url: str) -> AnimeInfo:
        """Get detailed anime information from URL."""
        pass

    @abstractmethod
    async def get_episode_stream(self, episode: EpisodeInfo, quality: int) -> str:
        """Get M3U8 stream URL for episode."""
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if source is currently accessible."""
        pass


class SourceUnavailableError(Exception):
    """Raised when source is unavailable."""

    pass


class StreamNotFoundError(Exception):
    """Raised when stream cannot be found."""

    pass
