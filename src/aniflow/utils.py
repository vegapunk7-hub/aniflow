"""Utilities module."""

from __future__ import annotations

import re
from pathlib import Path


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for filesystem.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, "", filename)
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(" .")
    return sanitized or "unnamed"


def format_bytes(bytes_count: int) -> str:
    """Format bytes to human readable string.

    Args:
        bytes_count: Number of bytes

    Returns:
        Formatted string
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_count < 1024:
            return f"{bytes_count:.2f}{unit}"
        bytes_count /= 1024
    return f"{bytes_count:.2f}TB"


def parse_episode_range(range_str: str) -> list[int]:
    """Parse episode range string.

    Examples:
        "1-12" -> [1, 2, ..., 12]
        "1,3,5" -> [1, 3, 5]
        "1-6,10,13-15" -> [1, 2, 3, 4, 5, 6, 10, 13, 14, 15]

    Args:
        range_str: Range string

    Returns:
        List of episode numbers
    """
    episodes = set()

    for part in range_str.split(","):
        part = part.strip()
        if "-" in part:
            start_str, end_str = part.split("-", 1)
            start = int(start_str.strip())
            # Handle open-ended ranges like "13-"
            end = int(end_str.strip()) if end_str.strip() else float("inf")
            episodes.update(range(start, int(end) + 1))
        else:
            episodes.add(int(part))

    return sorted(list(episodes))
