"""Episode metadata extraction."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any


class MetadataExtractor:
    """Extract metadata from episode information."""

    @staticmethod
    def parse_duration(duration_str: str | None) -> int | None:
        """Parse duration string to seconds.

        Formats:
        - "24:30" (mm:ss)
        - "1:24:30" (hh:mm:ss)
        - "1440" (seconds)

        Args:
            duration_str: Duration string

        Returns:
            Duration in seconds or None
        """
        if not duration_str:
            return None

        duration_str = duration_str.strip()

        # Try numeric (seconds)
        try:
            return int(duration_str)
        except ValueError:
            pass

        # Try mm:ss or hh:mm:ss
        parts = duration_str.split(":")
        try:
            if len(parts) == 2:
                minutes, seconds = int(parts[0]), int(parts[1])
                return minutes * 60 + seconds
            elif len(parts) == 3:
                hours, minutes, seconds = int(parts[0]), int(parts[1]), int(parts[2])
                return hours * 3600 + minutes * 60 + seconds
        except ValueError:
            pass

        return None

    @staticmethod
    def parse_release_date(date_str: str | None) -> datetime | None:
        """Parse release date from string.

        Formats:
        - "2023-01-15"
        - "January 15, 2023"
        - "15/01/2023"

        Args:
            date_str: Date string

        Returns:
            Datetime object or None
        """
        if not date_str:
            return None

        date_str = date_str.strip()

        # Try common formats
        formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%B %d, %Y",
            "%b %d, %Y",
            "%d %B %Y",
            "%d %b %Y",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return None

    @staticmethod
    def is_filler_episode(title: str | None, episode_num: int | None) -> bool:
        """Detect if episode is a filler episode.

        Args:
            title: Episode title
            episode_num: Episode number

        Returns:
            True if likely filler
        """
        if not title:
            return False

        title_lower = title.lower()
        filler_keywords = [
            "filler",
            "omake",
            "recap",
            "special",
            "ova",
            "extra",
        ]

        return any(keyword in title_lower for keyword in filler_keywords)

    @staticmethod
    def extract_quality_options(quality_str: str | None) -> list[int]:
        """Extract available quality options from string.

        Args:
            quality_str: Quality string (e.g., "360p, 720p, 1080p")

        Returns:
            List of quality integers
        """
        if not quality_str:
            return []

        qualities = []
        for match in re.finditer(r"(\d{3,4})(?:p)?", quality_str):
            quality = int(match.group(1))
            if quality in (360, 480, 720, 1080, 2160):
                qualities.append(quality)

        return sorted(list(set(qualities)), reverse=True)

    @staticmethod
    def extract_audio_tracks(audio_str: str | None) -> list[str]:
        """Extract available audio tracks.

        Args:
            audio_str: Audio string (e.g., "Japanese, English")

        Returns:
            List of audio track names
        """
        if not audio_str:
            return []

        tracks = []
        for track in audio_str.split(","):
            track = track.strip().lower()
            if track:
                tracks.append(track)

        return tracks
