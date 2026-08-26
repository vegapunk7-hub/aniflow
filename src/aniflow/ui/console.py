"""Rich terminal UI components."""

from __future__ import annotations

from rich.console import Console
from rich.theme import Theme

# Define custom theme
ANIFLOW_THEME = Theme(
    {
        "title": "bold cyan",
        "success": "bold green",
        "error": "bold red",
        "warning": "bold yellow",
        "info": "bold blue",
        "subtle": "dim white",
        "pending": "yellow",
        "downloading": "cyan",
        "completed": "green",
        "failed": "red",
    }
)

# Global console instance
console = Console(theme=ANIFLOW_THEME, force_terminal=True)
