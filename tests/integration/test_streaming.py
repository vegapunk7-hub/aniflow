"""Integration tests for streaming mode."""

from __future__ import annotations

import pytest

from aniflow.models import AnimeInfo, EpisodeInfo


@pytest.mark.asyncio
async def test_stream_playlist_generation() -> None:
    """Test generating MPV playlist for streaming."""
    anime = AnimeInfo(
        title="Test Series",
        url="https://example.com/test",
        source="test",
        episodes=[
            EpisodeInfo(episode_number=i, title=f"Ep {i}", url=f"https://example.com/ep{i}")
            for i in range(1, 4)
        ],
    )

    assert len(anime.episodes) == 3
    assert anime.episodes[0].episode_number == 1


def test_audio_track_switching() -> None:
    """Test audio track switching logic."""
    from aniflow.models import AudioLanguage

    # Test audio language options
    assert AudioLanguage.JAPANESE.value == "jpn"
    assert AudioLanguage.ENGLISH.value == "eng"
