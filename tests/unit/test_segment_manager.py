"""Tests for segment manager."""

from __future__ import annotations

import pytest

from aniflow.downloader.segment_manager import SegmentManager


@pytest.mark.asyncio
async def test_parse_encryption_key_hex() -> None:
    """Test parsing hex encryption key."""
    key_str = "0x1234567890abcdef1234567890abcdef"
    key = SegmentManager.parse_encryption_key(key_str)
    assert len(key) == 16
    assert key == bytes.fromhex("1234567890abcdef1234567890abcdef")


@pytest.mark.asyncio
async def test_hash_segment() -> None:
    """Test segment hashing."""
    data = b"test segment data"
    hash_val = SegmentManager.hash_segment(data)
    assert len(hash_val) == 64  # SHA256 hex string
    assert isinstance(hash_val, str)


def test_get_downloaded_segments_empty(tmp_path) -> None:
    """Test getting downloaded segments from empty directory."""
    manager = SegmentManager(cache_dir=tmp_path)
    downloaded = manager.get_downloaded_segments(tmp_path)
    assert downloaded == set()


def test_get_downloaded_segments(tmp_path) -> None:
    """Test getting downloaded segments."""
    manager = SegmentManager(cache_dir=tmp_path)
    segment_dir = tmp_path / "segments"
    segment_dir.mkdir()

    # Create some segment files
    (segment_dir / "000000.ts").touch()
    (segment_dir / "000001.ts").touch()
    (segment_dir / "000002.ts").touch()

    downloaded = manager.get_downloaded_segments(segment_dir)
    assert downloaded == {0, 1, 2}
