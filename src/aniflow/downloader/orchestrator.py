"""Download orchestrator for multi-source batch downloads."""

from __future__ import annotations

import asyncio
import uuid
from pathlib import Path
from typing import Any

from aniflow.config import get_config
from aniflow.db import SessionModel, get_session, init_database
from aniflow.models import AnimeInfo, DownloadMetrics, DownloadSession, DownloadStatus, EpisodeInfo
from aniflow.sources.registry import get_registry


class DownloadOrchestrator:
    """Orchestrates multi-stage download pipeline."""

    def __init__(self) -> None:
        """Initialize download orchestrator."""
        self.registry = get_registry()
        self.config = get_config()
        init_database()

    async def start_download(
        self,
        anime: AnimeInfo,
        episodes: list[int],
        quality: int = 1080,
        sources: list[str] | None = None,
        output_dir: str | None = None,
    ) -> DownloadSession:
        """Start a new download session.

        Args:
            anime: Anime information
            episodes: Episode numbers to download
            quality: Video quality
            sources: Preferred sources (None = auto)
            output_dir: Output directory

        Returns:
            Download session
        """
        session_id = str(uuid.uuid4())
        output_dir = output_dir or str(self.config.output_dir)

        download_session = DownloadSession(
            session_id=session_id,
            anime_info=anime,
            episodes_to_download=episodes,
            status=DownloadStatus.IN_PROGRESS,
            metadata={
                "quality": quality,
                "sources": sources or [self.registry.list_sources()[0]],
                "output_dir": output_dir,
            },
        )

        # Persist to database
        db_session = get_session()
        db_session_model = SessionModel(
            id=session_id,
            series_name=anime.title,
            series_url=anime.url,
            source=anime.source,
            total_episodes=len(episodes),
            quality=quality,
            output_dir=output_dir,
        )
        db_session.add(db_session_model)
        db_session.commit()
        db_session.close()

        return download_session

    async def download_episodes(
        self,
        session: DownloadSession,
        concurrent_episodes: int | None = None,
    ) -> None:
        """Download episodes for a session.

        Args:
            session: Download session
            concurrent_episodes: Number of concurrent episode downloads
        """
        concurrent_episodes = concurrent_episodes or self.config.max_parallel_episodes
        semaphore = asyncio.Semaphore(concurrent_episodes)

        tasks = []
        for ep_num in session.episodes_to_download:
            episode = next(
                (e for e in session.anime_info.episodes if e.episode_number == ep_num),
                None,
            )
            if episode:
                tasks.append(self._download_episode(session, episode, semaphore))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Update session status
        for result in results:
            if isinstance(result, Exception):
                session.failed_episodes.append(result)
            else:
                session.completed_episodes.append(result)

    async def _download_episode(
        self,
        session: DownloadSession,
        episode: EpisodeInfo,
        semaphore: asyncio.Semaphore,
    ) -> int:
        """Download a single episode.

        Args:
            session: Download session
            episode: Episode to download
            semaphore: Concurrency semaphore

        Returns:
            Episode number on success
        """
        async with semaphore:
            try:
                # TODO: Implement actual segment download
                # For now, just mark as completed
                return episode.episode_number
            except Exception as e:
                raise RuntimeError(
                    f"Failed to download episode {episode.episode_number}: {e}"
                )

    async def resume_session(self, session_id: str) -> DownloadSession:
        """Resume a previous download session.

        Args:
            session_id: Session ID

        Returns:
            Resume download session
        """
        db_session = get_session()
        db_model = db_session.query(SessionModel).filter_by(id=session_id).first()
        db_session.close()

        if not db_model:
            raise ValueError(f"Session not found: {session_id}")

        # TODO: Reconstruct session from database
        raise NotImplementedError("Session resumption under development")

    async def get_metrics(self, session_id: str) -> DownloadMetrics:
        """Get download metrics for a session.

        Args:
            session_id: Session ID

        Returns:
            Download metrics
        """
        # TODO: Calculate metrics from session data
        return DownloadMetrics(
            total_size_bytes=0,
            downloaded_bytes=0,
            speed_mbps=0.0,
            eta_seconds=None,
            success_rate=0.0,
            segments_total=0,
            segments_downloaded=0,
            segments_failed=0,
        )
