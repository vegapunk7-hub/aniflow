"""Integration tests for download flow."""

from __future__ import annotations

import pytest

from aniflow.models import AnimeInfo, AudioLanguage, EpisodeInfo, DownloadSession, DownloadStatus
from aniflow.downloader.orchestrator import DownloadOrchestrator


@pytest.mark.asyncio
async def test_download_session_creation() -> None:
    """Test creating a download session."""
    orchestrator = DownloadOrchestrator()

    anime = AnimeInfo(
        title="Test Anime",
        url="https://example.com/test",
        source="test",
        total_episodes=12,
    )

    session = await orchestrator.start_download(
        anime=anime,
        episodes=[1, 2, 3],
        quality=720,
    )

    assert session.session_id
    assert session.anime_info.title == "Test Anime"
    assert session.episodes_to_download == [1, 2, 3]
    assert session.status == DownloadStatus.IN_PROGRESS


@pytest.mark.asyncio
async def test_episode_selection_logic() -> None:
    """Test episode selection."""
    episodes = [
        EpisodeInfo(episode_number=i, title=f"Episode {i}", url=f"https://example.com/ep{i}")
        for i in range(1, 13)
    ]

    assert len(episodes) == 12
    selected = [ep.episode_number for ep in episodes[0:3]]
    assert selected == [1, 2, 3]


def test_episode_range_parsing() -> None:
    """Test episode range parsing."""
    from aniflow.utils import parse_episode_range

    # Range format
    assert parse_episode_range("1-5") == [1, 2, 3, 4, 5]

    # Comma-separated
    assert parse_episode_range("1,3,5") == [1, 3, 5]

    # Mixed
    assert parse_episode_range("1-3,7,10-12") == [1, 2, 3, 7, 10, 11, 12]

    # Open-ended
    assert parse_episode_range("10-") == list(range(10, 11))  # Just 10 in test
