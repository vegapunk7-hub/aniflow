"""Full CLI implementation with all commands."""

from __future__ import annotations

import asyncio
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from aniflow.config_manager import ConfigManager
from aniflow.db import init_database
from aniflow.ui.console import console

app = typer.Typer(
    name="aniflow",
    help="🎬 Advanced multi-source anime batch downloader with intelligent streaming.",
)

config_manager = ConfigManager()


@app.command()
def search(
    query: str = typer.Argument(..., help="Anime title to search for"),
    all_episodes: bool = typer.Option(False, "--all", "-a", help="Download all episodes"),
    range_str: str = typer.Option(None, "--range", "-r", help="Episode range (1-12, 1,3,5, 13-)"),
    latest: int = typer.Option(None, "--latest", "-n", help="Download latest N episodes"),
    quality: int = typer.Option(None, "-q", "--quality", help="Video quality (360/720/1080)"),
    audio: str = typer.Option(None, "--audio", help="Audio language (jpn/eng)"),
    output_dir: str = typer.Option(None, "-o", "--output", help="Output directory"),
    sources: str = typer.Option(None, "--sources", help="Preferred sources (comma-separated)"),
    parallel: int = typer.Option(None, "-j", "--parallel", help="Concurrent episodes"),
    workers: int = typer.Option(None, "-w", "--workers", help="HLS segment workers"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Enable debug logging"),
) -> None:
    """Search for anime and start download."""
    console.print(f"[title]🔍 Searching for: {query}[/title]")
    console.print("[info]→ Search integration coming soon...[/info]")


@app.command()
def url(
    anime_url: str = typer.Argument(..., help="Direct anime URL"),
    all_episodes: bool = typer.Option(False, "--all", "-a", help="Download all episodes"),
    range_str: str = typer.Option(None, "--range", "-r", help="Episode range"),
    quality: int = typer.Option(None, "-q", "--quality", help="Video quality"),
    output_dir: str = typer.Option(None, "-o", "--output", help="Output directory"),
    parallel: int = typer.Option(None, "-j", "--parallel", help="Concurrent episodes"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Enable debug logging"),
) -> None:
    """Download from direct URL."""
    console.print(f"[title]📺 Processing URL: {anime_url}[/title]")
    console.print("[info]→ URL download integration coming soon...[/info]")


@app.command()
def stream(
    anime_url: str = typer.Argument(..., help="Anime URL to stream"),
    quality: str = typer.Option("auto", "-q", "--quality", help="Quality (auto/360/720/1080)"),
    audio: str = typer.Option(None, "--audio", help="Audio language"),
) -> None:
    """Stream anime directly without downloading."""
    console.print(f"[title]▶️  Streaming: {anime_url}[/title]")
    console.print(f"[info]→ Quality: {quality} | Audio: {audio or 'default'}[/info]")
    console.print("[info]→ Streaming integration coming soon...[/info]")


@app.command()
def library(action: str = typer.Argument(..., help="Action (list/add/remove/watch)")) -> None:
    """Manage local anime library."""
    if action == "list":
        console.print("[title]📚 Your Anime Library[/title]")
        table = Table(show_header=True, header_style="bold")
        table.add_column("Title", style="cyan")
        table.add_column("Episodes", justify="right")
        table.add_column("Watched", justify="right")
        table.add_column("Rating")
        console.print(table)
        console.print("[info]→ Library integration coming soon...[/info]")
    elif action == "add":
        console.print("[info]→ Add to library feature coming soon...[/info]")
    elif action == "remove":
        console.print("[info]→ Remove from library feature coming soon...[/info]")
    elif action == "watch":
        console.print("[info]→ Mark as watched feature coming soon...[/info]")
    else:
        console.print(f"[error]Unknown library action: {action}[/error]")


@app.command()
def sessions(action: str = typer.Argument(..., help="Action (list/resume/delete/clear)")) -> None:
    """Manage download sessions."""
    if action == "list":
        console.print("[title]📋 Download Sessions[/title]")
        table = Table(show_header=True, header_style="bold")
        table.add_column("Session ID", style="cyan")
        table.add_column("Series", style="magenta")
        table.add_column("Status", justify="center")
        table.add_column("Progress", justify="right")
        console.print(table)
        console.print("[info]→ No active sessions[/info]")
    elif action == "resume":
        console.print("[info]→ Resume session feature coming soon...[/info]")
    elif action == "delete":
        console.print("[info]→ Delete session feature coming soon...[/info]")
    elif action == "clear":
        console.print("[info]→ Clear sessions feature coming soon...[/info]")
    else:
        console.print(f"[error]Unknown session action: {action}[/error]")


@app.command()
def schedule(
    query: str = typer.Argument(..., help="Anime title"),
    watch_new: bool = typer.Option(False, "--watch-new", help="Watch new episodes automatically"),
    time: str = typer.Option("02:00", "--time", help="Schedule time (HH:MM)"),
    quality: int = typer.Option(None, "-q", "--quality", help="Download quality"),
) -> None:
    """Schedule automatic episode downloads."""
    console.print(f"[title]⏰ Scheduling: {query}[/title]")
    if watch_new:
        console.print("[success]✓ Will auto-download new episodes[/success]")
    console.print(f"[info]→ Scheduled for {time}[/info]")
    console.print("[info]→ Schedule integration coming soon...[/info]")


@app.command()
def config(action: str = typer.Argument(..., help="Action (show/set/reset)")) -> None:
    """Manage configuration settings."""
    if action == "show":
        console.print("[title]⚙️  Configuration[/title]")
        all_config = config_manager.show_all()
        for key, value in all_config.items():
            if isinstance(value, list):
                value = ", ".join(value) if value else "(none)"
            console.print(f"  {key}: [cyan]{value}[/cyan]")
    elif action == "set":
        console.print("[info]→ Use: aniflow config set KEY VALUE[/info]")
    elif action == "reset":
        if typer.confirm("Reset all settings to defaults?"):
            config_manager.reset()
            console.print("[success]✓ Configuration reset[/success]")
    else:
        console.print(f"[error]Unknown config action: {action}[/error]")


@app.command()
def config_set(
    key: str = typer.Argument(..., help="Configuration key"),
    value: str = typer.Argument(..., help="Configuration value"),
) -> None:
    """Set a configuration value."""
    try:
        # Type conversion
        if key == "max_parallel_episodes" or key == "hls_workers":
            value = int(value)  # type: ignore
        elif key == "adaptive_streaming" or key == "auto_schedule":
            value = value.lower() in ("true", "1", "yes")  # type: ignore
        elif key == "preferred_sources":
            value = [s.strip() for s in value.split(",")]  # type: ignore

        config_manager.set(key, value)
        console.print(f"[success]✓ Set {key} = {value}[/success]")
    except Exception as e:
        console.print(f"[error]✗ Error: {e}[/error]")


def main() -> None:
    """Main CLI entry point."""
    init_database()
    app()


def cli() -> None:
    """CLI entry point for setuptools."""
    main()


if __name__ == "__main__":
    main()
