"""Data models for AniFlow."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class DownloadStatus(Enum):
    """Download status enumeration."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AudioLanguage(Enum):
    """Available audio languages."""

    JAPANESE = "jpn"
    ENGLISH = "eng"
    ALL = "all"


@dataclass
class EpisodeInfo:
    """Information about a single episode."""

    episode_number: int
    title: str
    url: str
    duration_seconds: int | None = None
    release_date: datetime | None = None
    filler: bool = False
    available_qualities: list[int] = field(default_factory=list)
    available_audio: list[AudioLanguage] = field(default_factory=list)

    def __hash__(self) -> int:
        """Hash by episode number and title."""
        return hash((self.episode_number, self.title))


@dataclass
class AnimeInfo:
    """Information about an anime series."""

    title: str
    url: str
    source: str  # e.g., "animepahe", "9anime"
    episodes: list[EpisodeInfo] = field(default_factory=list)
    total_episodes: int | None = None
    genres: list[str] = field(default_factory=list)
    year: int | None = None
    season: str | None = None
    rating: float | None = None
    description: str | None = None
    cover_url: str | None = None


@dataclass
class StreamInfo:
    """Stream information for an episode."""

    m3u8_url: str
    quality: int
    audio_language: AudioLanguage
    headers: dict[str, str] = field(default_factory=dict)
    segments: list[str] = field(default_factory=list)
    duration_seconds: int | None = None
    encryption_key: str | None = None


@dataclass
class DownloadSession:
    """Persistent download session."""

    session_id: str
    anime_info: AnimeInfo
    episodes_to_download: list[int]
    status: DownloadStatus = DownloadStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_episodes: list[int] = field(default_factory=list)
    failed_episodes: list[int] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DownloadMetrics:
    """Metrics for a download."""

    total_size_bytes: int
    downloaded_bytes: int
    speed_mbps: float
    eta_seconds: int | None
    success_rate: float
    segments_total: int
    segments_downloaded: int
    segments_failed: int
