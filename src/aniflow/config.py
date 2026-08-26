"""Configuration management for AniFlow."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class AppConfig:
    """Application configuration."""

    # Download settings
    default_quality: int = 1080
    preferred_sources: list[str] | None = None
    output_dir: Path = Path("./downloads")
    max_parallel_episodes: int = 2
    hls_workers: int = 24
    output_format: str = "mp4"

    # Audio/Subtitle settings
    preferred_audio: str = "jpn"
    subtitle_tracks: list[str] | None = None

    # Session settings
    cache_ttl_minutes: int = 60
    auto_cleanup_hours: int = 24

    # Streaming settings
    adaptive_streaming: bool = True
    bandwidth_limit_mbps: int | None = None

    # Scheduling settings
    auto_schedule: bool = False
    schedule_time: str = "02:00"  # 2 AM

    # Advanced settings
    verbose: bool = False
    flaresolverr_url: str = "http://localhost:8191"
    timeout_seconds: int = 30

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if self.default_quality not in (360, 720, 1080):
            raise ValueError(f"Invalid quality: {self.default_quality}")
        if self.max_parallel_episodes < 1 or self.max_parallel_episodes > 8:
            raise ValueError(f"Invalid parallel episodes: {self.max_parallel_episodes}")
        if self.hls_workers < 8 or self.hls_workers > 64:
            raise ValueError(f"Invalid HLS workers: {self.hls_workers}")
        if self.output_format not in ("mp4", "mkv", "webm"):
            raise ValueError(f"Invalid output format: {self.output_format}")


# Global configuration instance
_config: AppConfig | None = None


def get_config() -> AppConfig:
    """Get the current application configuration."""
    global _config
    if _config is None:
        _config = AppConfig()
    return _config


def set_config(config: AppConfig) -> None:
    """Set the application configuration."""
    global _config
    _config = config
