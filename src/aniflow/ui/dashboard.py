"""Live download dashboard."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, ProgressColumn, Task, TaskProgressColumn
from rich.table import Table
from rich.text import Text

from aniflow.models import DownloadSession, EpisodeInfo
from aniflow.ui.console import console


class DownloadDashboard:
    """Live progress dashboard for downloads."""

    def __init__(self, session: DownloadSession) -> None:
        """Initialize dashboard.

        Args:
            session: Download session
        """
        self.session = session
        self.progress = Progress(
            TaskProgressColumn(text_format="[progress.percentage]{task.percentage:>3.0f}%"),
        )
        self.live = Live(
            self._create_layout(),
            console=console,
            refresh_per_second=2,
        )
        self.episode_progress: dict[int, dict[str, Any]] = {}

    def _create_layout(self) -> Layout:
        """Create dashboard layout.

        Returns:
            Layout object
        """
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="episodes"),
            Layout(name="stats", size=4),
        )
        return layout

    def start(self) -> None:
        """Start dashboard."""
        self.live.start()

    def stop(self) -> None:
        """Stop dashboard."""
        self.live.stop()

    def update_episode(
        self,
        episode_num: int,
        status: str,
        progress: float = 0.0,
        speed: float = 0.0,
        eta: int | None = None,
    ) -> None:
        """Update episode progress.

        Args:
            episode_num: Episode number
            status: Status (downloading, completed, failed)
            progress: Download progress (0-100)
            speed: Download speed in MB/s
            eta: Estimated time in seconds
        """
        self.episode_progress[episode_num] = {
            "status": status,
            "progress": progress,
            "speed": speed,
            "eta": eta,
            "updated_at": datetime.now(),
        }
        self.live.update(self._create_layout())

    def _render_header(self) -> Panel:
        """Render header panel.

        Returns:
            Header panel
        """
        title = f"🎬 {self.session.anime_info.title}"
        subtitle = f"Episodes: {len(self.session.completed_episodes)}/{len(self.session.episodes_to_download)}"
        return Panel(f"{title}\n{subtitle}", style="title")

    def _render_episodes(self) -> Table:
        """Render episodes table.

        Returns:
            Episodes table
        """
        table = Table(title="Episodes", show_header=True, header_style="bold")
        table.add_column("Ep", width=4)
        table.add_column("Status", width=12)
        table.add_column("Progress", width=20)
        table.add_column("Speed", width=10)
        table.add_column("ETA", width=10)

        for ep_num in sorted(self.episode_progress.keys()):
            info = self.episode_progress[ep_num]
            status_text = self._get_status_text(info["status"])
            progress_bar = self._create_progress_bar(info["progress"])
            speed_str = f"{info['speed']:.2f}MB/s"
            eta_str = self._format_eta(info.get("eta"))

            table.add_row(
                str(ep_num).zfill(2),
                status_text,
                progress_bar,
                speed_str,
                eta_str,
            )

        return table

    def _render_stats(self) -> Panel:
        """Render statistics panel.

        Returns:
            Stats panel
        """
        total = len(self.session.episodes_to_download)
        completed = len(self.session.completed_episodes)
        failed = len(self.session.failed_episodes)
        success_rate = (completed / total * 100) if total > 0 else 0

        stats_text = f"""Completed: {completed}/{total}
Failed: {failed}
Success Rate: {success_rate:.1f}%
Started: {self.session.created_at.strftime('%Y-%m-%d %H:%M:%S')}"""

        return Panel(stats_text, title="Statistics", style="info")

    @staticmethod
    def _get_status_text(status: str) -> Text:
        """Get colored status text.

        Args:
            status: Status string

        Returns:
            Colored text
        """
        colors = {
            "downloading": "downloading",
            "completed": "completed",
            "failed": "failed",
            "pending": "pending",
        }
        style = colors.get(status, "info")
        return Text(status.upper(), style=style)

    @staticmethod
    def _create_progress_bar(progress: float) -> str:
        """Create progress bar string.

        Args:
            progress: Progress percentage (0-100)

        Returns:
            Progress bar string
        """
        filled = int(progress / 5)
        empty = 20 - filled
        bar = "█" * filled + "░" * empty
        return f"{bar} {progress:.0f}%"

    @staticmethod
    def _format_eta(eta_seconds: int | None) -> str:
        """Format ETA.

        Args:
            eta_seconds: ETA in seconds

        Returns:
            Formatted ETA
        """
        if eta_seconds is None:
            return "--:--"
        hours = eta_seconds // 3600
        minutes = (eta_seconds % 3600) // 60
        seconds = eta_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
