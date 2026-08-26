"""Scheduler for automatic episode downloads."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Callable

import schedule

logger = logging.getLogger(__name__)


class ScheduleJob:
    """A scheduled download job."""

    def __init__(
        self,
        series_title: str,
        job_id: str,
        callback: Callable[..., Any],
        quality: int = 1080,
        sources: list[str] | None = None,
    ) -> None:
        """Initialize schedule job.

        Args:
            series_title: Anime series title
            job_id: Unique job ID
            callback: Async callback function
            quality: Video quality
            sources: Preferred sources
        """
        self.series_title = series_title
        self.job_id = job_id
        self.callback = callback
        self.quality = quality
        self.sources = sources or []
        self.last_run: datetime | None = None
        self.next_run: datetime | None = None
        self.is_active = True


class EpisodeScheduler:
    """Schedule and track automatic episode downloads."""

    def __init__(self) -> None:
        """Initialize scheduler."""
        self.jobs: dict[str, ScheduleJob] = {}
        self.scheduler = schedule.Scheduler()
        self._running = False

    def schedule_series(
        self,
        series_title: str,
        callback: Callable[..., Any],
        run_time: str = "02:00",  # HH:MM format
        quality: int = 1080,
        sources: list[str] | None = None,
    ) -> str:
        """Schedule a series for automatic downloads.

        Args:
            series_title: Anime series title
            callback: Async callback function
            run_time: Time to run job (HH:MM)
            quality: Video quality
            sources: Preferred sources

        Returns:
            Job ID
        """
        job_id = f"series_{series_title.replace(' ', '_')}"
        job = ScheduleJob(series_title, job_id, callback, quality, sources)

        self.jobs[job_id] = job
        self.scheduler.every().day.at(run_time).do(
            self._run_job, job_id=job_id
        )

        logger.info(f"Scheduled {series_title} for daily download at {run_time}")
        return job_id

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a scheduled job.

        Args:
            job_id: Job ID

        Returns:
            True if cancelled
        """
        if job_id in self.jobs:
            self.jobs[job_id].is_active = False
            # Remove from schedule
            self.scheduler.jobs = [
                j for j in self.scheduler.jobs
                if j.job_func.keywords.get("job_id") != job_id
            ]
            logger.info(f"Cancelled job {job_id}")
            return True
        return False

    def list_jobs(self) -> list[ScheduleJob]:
        """List all scheduled jobs.

        Returns:
            List of jobs
        """
        return list(self.jobs.values())

    async def start(self) -> None:
        """Start the scheduler."""
        self._running = True
        logger.info("Episode scheduler started")

        while self._running:
            self.scheduler.run_pending()
            await asyncio.sleep(60)  # Check every minute

    async def stop(self) -> None:
        """Stop the scheduler."""
        self._running = False
        logger.info("Episode scheduler stopped")

    def _run_job(self, job_id: str) -> None:
        """Run a scheduled job.

        Args:
            job_id: Job ID
        """
        if job_id not in self.jobs:
            return

        job = self.jobs[job_id]
        if not job.is_active:
            return

        logger.info(f"Running scheduled job: {job.series_title}")
        job.last_run = datetime.now()
        job.next_run = datetime.now() + timedelta(days=1)

        # Execute callback (should be async)
        try:
            asyncio.create_task(job.callback())
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}")
