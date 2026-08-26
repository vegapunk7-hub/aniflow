"""Pytest configuration and fixtures."""

from __future__ import annotations

import pytest

from aniflow.models import AnimeInfo, EpisodeInfo, AudioLanguage


@pytest.fixture
def sample_episode() -> EpisodeInfo:
    """Create a sample episode for testing."""
    return EpisodeInfo(
        episode_number=1,
        title="Episode 1: Beginning",
        url="https://example.com/ep1",
        duration_seconds=1440,
        available_qualities=[720, 1080],
        available_audio=[AudioLanguage.JAPANESE, AudioLanguage.ENGLISH],
    )


@pytest.fixture
def sample_anime() -> AnimeInfo:
    """Create a sample anime for testing."""
    return AnimeInfo(
        title="Attack on Titan",
        url="https://example.com/attack-on-titan",
        source="animepahe",
        total_episodes=139,
        genres=["Action", "Drama", "Fantasy"],
        year=2013,
        season="Fall",
        rating=8.9,
    )
