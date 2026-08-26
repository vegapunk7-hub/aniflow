"""HLS manifest parsing and segment extraction."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass
class M3U8Playlist:
    """Parsed M3U8 playlist information."""

    segments: list[str]
    duration: float
    encryption_key: str | None = None
    encryption_iv: str | None = None


class M3U8Parser:
    """Parse HLS M3U8 manifests."""

    @staticmethod
    def parse(content: str) -> M3U8Playlist:
        """Parse M3U8 playlist content.

        Args:
            content: M3U8 playlist content

        Returns:
            Parsed playlist information
        """
        lines = content.strip().split("\n")
        segments = []
        duration = 0.0
        encryption_key = None
        encryption_iv = None

        for i, line in enumerate(lines):
            line = line.strip()

            # Parse duration
            if line.startswith("#EXTINF:"):
                match = re.search(r"#EXTINF:([\d.]+)", line)
                if match:
                    duration += float(match.group(1))

            # Parse encryption key
            elif line.startswith("#EXT-X-KEY:"):
                key_match = re.search(r'URI="([^"]+)"', line)
                if key_match:
                    encryption_key = key_match.group(1)

                iv_match = re.search(r"IV=0x([A-Fa-f0-9]+)", line)
                if iv_match:
                    encryption_iv = iv_match.group(1)

            # Collect segment URLs
            elif line and not line.startswith("#"):
                segments.append(line)

        return M3U8Playlist(
            segments=segments,
            duration=duration,
            encryption_key=encryption_key,
            encryption_iv=encryption_iv,
        )

    @staticmethod
    def find_master_variant(content: str) -> str | None:
        """Extract highest quality variant from master playlist.

        Args:
            content: Master M3U8 content

        Returns:
            URL of highest quality variant or None
        """
        lines = content.strip().split("\n")
        variants = []

        for i, line in enumerate(lines):
            if line.startswith("#EXT-X-STREAM-INF:"):
                # Get bandwidth and resolution
                bandwidth_match = re.search(r"BANDWIDTH=([\d]+)", line)
                resolution_match = re.search(r'RESOLUTION=([\dx]+)', line)

                if i + 1 < len(lines):
                    url = lines[i + 1].strip()
                    if url and not url.startswith("#"):
                        variants.append(
                            {
                                "url": url,
                                "bandwidth": int(bandwidth_match.group(1))
                                if bandwidth_match
                                else 0,
                                "resolution": resolution_match.group(1)
                                if resolution_match
                                else None,
                            }
                        )

        # Return highest bandwidth variant
        if variants:
            return max(variants, key=lambda x: x["bandwidth"])["url"]
        return None
