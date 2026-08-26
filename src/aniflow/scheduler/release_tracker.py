"""Release tracker for new episode detection."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

from aniflow.db import EpisodeModel, SessionModel, get_session

logger = logging.getLogger(__name__)


class ReleaseTracker:
    """Track and detect new episode releases."""

    def __init__(self, check_interval_hours: int = 6) -> None:
        """Initialize release tracker.

        Args:
            check_interval_hours: Hours between release checks
        """
        self.check_interval = timedelta(hours=check_interval_hours)
        self.tracked_series: dict[str, datetime] = {}
        self._running = False

    async def track_series(self, series_url: str, series_title: str) -> None:
        """Start tracking a series for new releases.

        Args:
            series_url: Anime URL
            series_title: Series title
        """
        self.tracked_series[series_url] = datetime.now()
        logger.info(f"Now tracking: {series_title}")

    async def check_for_releases(
        self,
        source_checker: Any,  # Source plugin instance
    ) -> dict[str, list[int]]:
        """Check tracked series for new episodes.

        Args:
            source_checker: Source plugin to check episodes

        Returns:
            Dict of {series_url: [new_episode_numbers]}
        """
        new_episodes: dict[str, list[int]] = {}
        db_session = get_session()

        for series_url, last_check in self.tracked_series.items():
            # Skip if checked recently
            if datetime.now() - last_check < self.check_interval:
                continue

            try:
                # Get current episodes from source
                current_episodes = await source_checker.get_anime_info(series_url)
                current_ep_nums = {
                    ep.episode_number for ep in current_episodes.episodes
                }

                # Get downloaded episodes from database
                session = db_session.query(SessionModel).filter_by(
                    series_url=series_url
                ).first()

                if session:
                    downloaded = set(
                        ep.episode_num
                        for ep in db_session.query(EpisodeModel).filter_by(
                            session_id=session.id
                        )
                    )
                    new_ep_nums = sorted(list(current_ep_nums - downloaded))

                    if new_ep_nums:
                        new_episodes[series_url] = new_ep_nums
                        logger.info(
                            f"Found new episodes for {series_url}: {new_ep_nums}"
                        )

                self.tracked_series[series_url] = datetime.now()
            except Exception as e:
                logger.error(f"Error checking releases for {series_url}: {e}")

        db_session.close()
        return new_episodes

    def untrack_series(self, series_url: str) -> None:
        """Stop tracking a series.

        Args:
            series_url: Anime URL
        """
        if series_url in self.tracked_series:
            del self.tracked_series[series_url]
            logger.info(f"Stopped tracking: {series_url}")

    def list_tracked_series(self) -> list[str]:
        """Get list of tracked series.

        Returns:
            List of series URLs
        """
        return list(self.tracked_series.keys())
