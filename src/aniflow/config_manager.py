"""Configuration manager with TOML persistence."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # type: ignore

import tomli_w

from aniflow.config import AppConfig


class ConfigManager:
    """Manage application configuration with TOML persistence."""

    def __init__(self, config_file: Path | None = None) -> None:
        """Initialize config manager.

        Args:
            config_file: Path to TOML config file
        """
        self.config_file = config_file or Path("./aniflow.toml")
        self.config = self._load_config()

    def _load_config(self) -> AppConfig:
        """Load configuration from file or create default.

        Returns:
            AppConfig instance
        """
        if self.config_file.exists():
            try:
                with open(self.config_file, "rb") as f:
                    data = tomllib.load(f)
                return AppConfig(
                    default_quality=data.get("default_quality", 1080),
                    preferred_sources=data.get("preferred_sources", []),
                    output_dir=Path(data.get("output_dir", "./downloads")),
                    max_parallel_episodes=data.get("max_parallel_episodes", 2),
                    hls_workers=data.get("hls_workers", 24),
                    output_format=data.get("output_format", "mp4"),
                    preferred_audio=data.get("preferred_audio", "jpn"),
                    subtitle_tracks=data.get("subtitle_tracks"),
                    cache_ttl_minutes=data.get("cache_ttl_minutes", 60),
                    auto_cleanup_hours=data.get("auto_cleanup_hours", 24),
                    adaptive_streaming=data.get("adaptive_streaming", True),
                    bandwidth_limit_mbps=data.get("bandwidth_limit_mbps"),
                    auto_schedule=data.get("auto_schedule", False),
                    schedule_time=data.get("schedule_time", "02:00"),
                    verbose=data.get("verbose", False),
                    flaresolverr_url=data.get("flaresolverr_url", "http://localhost:8191"),
                    timeout_seconds=data.get("timeout_seconds", 30),
                )
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")
                return AppConfig()
        else:
            return AppConfig()

    def save(self) -> None:
        """Save configuration to TOML file."""
        config_dict = {
            "default_quality": self.config.default_quality,
            "preferred_sources": self.config.preferred_sources or [],
            "output_dir": str(self.config.output_dir),
            "max_parallel_episodes": self.config.max_parallel_episodes,
            "hls_workers": self.config.hls_workers,
            "output_format": self.config.output_format,
            "preferred_audio": self.config.preferred_audio,
            "cache_ttl_minutes": self.config.cache_ttl_minutes,
            "auto_cleanup_hours": self.config.auto_cleanup_hours,
            "adaptive_streaming": self.config.adaptive_streaming,
            "auto_schedule": self.config.auto_schedule,
            "schedule_time": self.config.schedule_time,
            "verbose": self.config.verbose,
            "flaresolverr_url": self.config.flaresolverr_url,
            "timeout_seconds": self.config.timeout_seconds,
        }

        if self.config.subtitle_tracks:
            config_dict["subtitle_tracks"] = self.config.subtitle_tracks
        if self.config.bandwidth_limit_mbps:
            config_dict["bandwidth_limit_mbps"] = self.config.bandwidth_limit_mbps

        with open(self.config_file, "wb") as f:
            tomli_w.dump(config_dict, f)

    def get(self, key: str) -> Any:
        """Get configuration value.

        Args:
            key: Config key

        Returns:
            Config value
        """
        return getattr(self.config, key, None)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value.

        Args:
            key: Config key
            value: Config value
        """
        if hasattr(self.config, key):
            # Validate and clamp values
            if key == "default_quality":
                if value not in (360, 720, 1080):
                    raise ValueError(f"Invalid quality: {value}")
            elif key == "max_parallel_episodes":
                value = max(1, min(8, int(value)))
            elif key == "hls_workers":
                value = max(8, min(64, int(value)))
            elif key == "output_format":
                if value not in ("mp4", "mkv", "webm"):
                    raise ValueError(f"Invalid format: {value}")

            setattr(self.config, key, value)
            self.save()
        else:
            raise KeyError(f"Unknown config key: {key}")

    def reset(self) -> None:
        """Reset configuration to defaults."""
        self.config = AppConfig()
        self.save()

    def show_all(self) -> dict[str, Any]:
        """Get all configuration values.

        Returns:
            Dictionary of all config values
        """
        return {
            "default_quality": self.config.default_quality,
            "preferred_sources": self.config.preferred_sources,
            "output_dir": str(self.config.output_dir),
            "max_parallel_episodes": self.config.max_parallel_episodes,
            "hls_workers": self.config.hls_workers,
            "output_format": self.config.output_format,
            "preferred_audio": self.config.preferred_audio,
            "subtitle_tracks": self.config.subtitle_tracks,
            "cache_ttl_minutes": self.config.cache_ttl_minutes,
            "auto_cleanup_hours": self.config.auto_cleanup_hours,
            "adaptive_streaming": self.config.adaptive_streaming,
            "bandwidth_limit_mbps": self.config.bandwidth_limit_mbps,
            "auto_schedule": self.config.auto_schedule,
            "schedule_time": self.config.schedule_time,
            "verbose": self.config.verbose,
            "flaresolverr_url": self.config.flaresolverr_url,
            "timeout_seconds": self.config.timeout_seconds,
        }
