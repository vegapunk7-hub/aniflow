# AniFlow

Advanced multi-source anime batch downloader with intelligent parallel processing, comprehensive session management, and adaptive streaming capabilities.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Table of Contents

- [About](#about)
- [Key Features](#key-features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Feature Tour](#feature-tour)
- [CLI Reference](#cli-reference)
- [Architecture](#architecture)
- [Package Structure](#package-structure)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

---

## About

**AniFlow** is a next-generation terminal application for batch-downloading anime from multiple sources. It extends the concept of single-site downloaders with:

- **Multi-source support** - AnimePahe, 9anime, GoGoAnime, and more (extensible plugin architecture)
- **Intelligent source selection** - Automatically selects best available source based on quality, speed, and availability
- **Advanced caching** - Smart segment deduplication across sources
- **Adaptive streaming** - Auto-adjust quality based on network conditions
- **Concurrent multi-source downloads** - Download same episode from multiple sources simultaneously for redundancy
- **Enhanced session persistence** - Resume across different sources, track download metrics
- **Rich metadata** - Fetch and organize by genres, release year, season, cast
- **Scheduled batch downloads** - Download new episodes automatically on release
- **Subtitle management** - Download, sync, and manage multiple subtitle tracks
- **Library management** - Track watched episodes, ratings, watch history

---

## Key Features

### Multi-Source Architecture
- **Plugin-based source system** - Easy to add new anime sources
- **Fallback strategy** - If primary source fails, automatically tries secondary sources
- **Quality negotiation** - Each source has different quality/speed tradeoffs
- **Unified metadata** - Normalizes episode info across sources

### Enhanced Download Engine
- **Parallel HLS with segment-level recovery** - Crash-resistant downloads
- **Adaptive bitrate selection** - Automatically adjust quality mid-download
- **Concurrent multi-source fetching** - Download redundantly for reliability
- **Smart retry with exponential backoff** - Intelligent failure handling
- **Bandwidth throttling** - Respect ISP/server limits

### Session & State Management
- **Persistent session store** - SQLite-based session tracking
- **Download analytics** - Speed, success rate, quality metrics
- **Resume granularity** - Resume by episode, season, or series
- **Cross-session deduplication** - Reuse segments across downloads
- **Automatic cleanup** - Orphan detection and removal

### User Experience
- **Rich interactive TUI** - Real-time progress, live dashboards
- **Multi-format output** - MP4, MKV, WebM with customizable codecs
- **Subtitle synchronization** - Auto-sync or manual offset
- **Watch history & ratings** - Track viewing progress
- **Scheduled downloads** - Cron-like episode release notifications

### Advanced Streaming
- **Adaptive playback** - Auto-quality adjustment during streaming
- **Multi-audio tracks** - Switch between SUB/DUB on-the-fly
- **Subtitle overlays** - Live subtitle management during playback
- **Playlist management** - Create custom playlists across series
- **Playback analytics** - Track watch time, resume points

---

## Prerequisites

| Requirement | Purpose | Install |
|---|---|---|
| **[FlareSolverr](https://github.com/FlareSolverr/FlareSolverr)** | Cloudflare bypass (headless Chromium) | `docker run -d --name=flaresolverr -p 8191:8191 ghcr.io/flaresolverr/flaresolverr` |
| **[FFmpeg](https://ffmpeg.org/)** | Video transcoding and muxing | `sudo apt install ffmpeg` (Linux) / `brew install ffmpeg` (macOS) |
| **[MPV](https://mpv.io/)** | Streaming playback | `sudo apt install mpv` / `brew install mpv` |
| **[SQLite3](https://www.sqlite.org/)** | Session persistence | Built-in on most systems |
| **Python 3.11+** | Runtime | `python3 --version` |

---

## Installation

```bash
git clone https://github.com/vegapunk7-hub/aniflow.git
cd aniflow
```

### Option A: Makefile (zero-config)

```bash
make install      # Create venv and install dependencies
make run          # Interactive wizard
make run URL="https://..."  # Direct series download
make test         # Run all tests
make lint         # Code quality checks
```

### Option B: pipx (isolated global install)

```bash
pipx install .
aniflow
```

### Option C: pip editable (development)

```bash
pip install -e ".[dev]"
aniflow
```

---

## Quick Start

```bash
# Interactive wizard - search and configure
aniflow

# Download entire series, 720p, auto-best source
aniflow search "Attack on Titan" --all -q 720

# Download with source preference
aniflow search "Demon Slayer" --range 1-12 -q 1080 --sources animepahe,9anime

# Stream with adaptive quality
aniflow search "Jujutsu Kaisen" --stream -q auto

# Download with redundancy (from 2 sources)
aniflow search "One Piece" --latest 5 --redundant 2

# Schedule automatic episode downloads
aniflow schedule "My Hero Academia" --watch-new --quality 720

# View library and watch history
aniflow library list
aniflow watch "Attack on Titan" 3  # Mark episode 3 as watched

# Configure defaults
aniflow config set default_quality 720
aniflow config set preferred_sources animepahe,9anime
aniflow config set output_dir ~/anime
```

---

## Feature Tour

### Download Mode

**Multi-source selection:**
- Automatic source ranking (quality, speed, reliability)
- Manual source preference
- Fallback source on failure
- Parallel fetching from multiple sources

**Advanced episode selection:**
- By range, latest, specific episodes
- By season and year
- By genre and tags
- Smart resuming

**Quality negotiation:**
- Per-source quality availability
- Adaptive bitrate during download
- Fallback to lower quality if unavailable
- Format conversion (MP4, MKV, WebM)

### Stream Mode

**Adaptive streaming:**
- Real-time quality adjustment based on bandwidth
- Multiple audio track switching (SUB/DUB/other languages)
- Subtitle management with sync control
- Playback resume from last position

### Session & Library Management

**Enhanced session tracking:**
- SQLite-based persistence
- Download metrics and analytics
- Resume granularity (episode/season/series)
- Cross-session segment reuse

**Library features:**
- Track watched episodes
- User ratings and reviews
- Watch history timeline
- Personalized recommendations

### Scheduled Downloads

**Episode release tracking:**
- Automatic new episode notifications
- Scheduled batch downloads
- Configurable download time (off-peak hours)
- Email/webhook notifications

---

## CLI Reference

```
aniflow [COMMAND] [OPTIONS]
```

### Main Commands

| Command | Description |
|---------|-------------|
| `search QUERY` | Search and download by title |
| `url URL` | Download from direct URL |
| `library` | Manage local library |
| `schedule` | Configure scheduled downloads |
| `config` | Manage settings |
| `sessions` | Manage download sessions |
| `stream URL` | Stream directly without downloading |

### Download Options

| Flag | Description | Default |
|------|-------------|----------|
| `--all` | Download all episodes | |
| `--range RANGE` | Episode range (1-12, 1,4,7, 13-) | |
| `--latest N` | Last N episodes | |
| `-q, --quality` | Resolution (360/720/1080/auto) | 1080 |
| `--sources` | Preferred sources (comma-separated) | auto |
| `--redundant N` | Download from N sources simultaneously | 1 |
| `--audio` | Audio track (jpn/eng/all) | jpn |
| `-o, --output` | Output directory | ./downloads |
| `-j, --parallel` | Concurrent episodes (1-8) | 2 |
| `-w, --workers` | HLS segment workers (8-64) | 24 |
| `--format` | Output format (mp4/mkv/webm) | mp4 |
| `--subs` | Subtitle tracks (comma-separated) | none |
| `-v, --verbose` | Debug logging | off |

### Configuration

```bash
aniflow config show                              # Display all settings
aniflow config set default_quality 720           # Set default quality
aniflow config set preferred_sources animepahe,9anime  # Source preference
aniflow config set output_dir ~/anime             # Output directory
aniflow config set auto_schedule true             # Auto-download new episodes
aniflow config reset                              # Restore defaults
```

---

## Architecture

### Multi-Source Plugin System

```
┌─────────────────────────────────────────────┐
│  Source Abstraction Layer                   │
│  (BaseSource, SourceRegistry)               │
└─────────────────────────────────────────────┘
         ↓              ↓              ↓
   ┌─────────┐  ┌──────────┐  ┌──────────────┐
   │AnimePahe│  │9Anime    │  │GoGoAnime     │
   │Plugin   │  │Plugin    │  │Plugin        │
   └─────────┘  └──────────┘  └──────────────┘
```

### Three-Stage Download Pipeline

```
┌─────────────────────────────────────────────────────────┐
│ Stage 1: Source Selection & Metadata Fetch              │
│ - Query multiple sources in parallel                     │
│ - Rank by quality, speed, reliability                   │
│ - Select primary + fallback sources                     │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ Stage 2: URL Resolution (Parallel across sources)       │
│ - Resolve to M3U8/direct URLs                           │
│ - Handle Cloudflare via FlareSolverr                   │
│ - Extract stream metadata                               │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ Stage 3: Segment Download (Multi-source redundancy)     │
│ - Adaptive quality selection                            │
│ - Concurrent segment fetching                           │
│ - Multi-source fallback                                 │
│ - Atomic writes with crash recovery                     │
└─────────────────────────────────────────────────────────┘
```

### Session Persistence Layer

```
aniflow_db.sqlite
├── sessions (id, series_name, url, status, created_at, updated_at)
├── episodes (session_id, episode_num, title, downloaded, quality, source)
├── segments (episode_id, segment_index, hash, source, status)
├── library (series_id, title, genres, rating, watched_episodes)
└── watch_history (library_id, episode_num, watched_at, duration)
```

---

## Package Structure

```
src/aniflow/
├── __init__.py                    # Package metadata
├── __main__.py                    # Entry point
├── main.py                        # CLI dispatcher
├── models.py                      # Data models
├── config.py                      # Configuration management
├── utils.py                       # Utilities
├── tls.py                         # TLS/SSL hardening
├── http.py                        # HTTP client with retry
├── cache.py                       # Caching layer
├── db.py                          # Database models & queries
├── sources/                       # Multi-source plugin system
│   ├── __init__.py
│   ├── base.py                    # BaseSource interface
│   ├── registry.py                # Source registration
│   ├── animepahe.py               # AnimePahe plugin
│   ├── nineanime.py               # 9Anime plugin
│   └── gogoanime.py               # GoGoAnime plugin
├── extractors/                    # Metadata extractors
│   ├── kwik.py                    # Kwik URL extraction
│   ├── m3u8.py                    # HLS manifest parsing
│   └── metadata.py                # Episode metadata
├── downloader/                    # Download engine
│   ├── orchestrator.py            # Download coordination
│   ├── episode_downloader.py      # Per-episode downloader
│   ├── segment_manager.py         # Segment storage & dedup
│   └── stream.py                  # MPV streaming
├── scheduler/                     # Scheduled downloads
│   ├── scheduler.py               # Cron-like scheduler
│   ├── release_tracker.py         # Episode release detection
│   └── notifications.py           # Email/webhook notifications
├── library/                       # Library management
│   ├── manager.py                 # Library operations
│   ├── watch_history.py           # Watch tracking
│   └── recommendations.py         # Smart recommendations
├── ui/                            # Terminal UI
│   ├── console.py                 # Rich console
│   ├── dashboard.py               # Live dashboards
│   ├── tables.py                  # Table rendering
│   ├── prompts.py                 # Interactive prompts
│   └── themes.py                  # UI themes
└── session/                       # Session management
    ├── manager.py                 # Session persistence
    └── analytics.py               # Download metrics

tests/
├── conftest.py                    # Fixtures & mocks
├── unit/
│   ├── test_sources.py
│   ├── test_downloader.py
│   ├── test_cache.py
│   ├── test_config.py
│   └── test_db.py
├── integration/
│   ├── test_multi_source.py
│   ├── test_download_flow.py
│   └── test_streaming.py
└── fixtures/                      # Test data

Makefile                          # Common tasks
pyproject.toml                    # Project metadata
requirements.txt                  # Dependencies
requirements-dev.txt              # Dev dependencies
.github/workflows/                # CI/CD pipelines
```

---

## Development

```bash
make install          # Install dependencies
make test             # Run tests
make lint             # Code quality
make typecheck        # Type checking
make dev              # Install with dev tools
make clean            # Clean build artifacts
```

---

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Install dev dependencies: `pip install -e ".[dev]"`
4. Make changes and add tests
5. Ensure `make lint` and `make test` pass
6. Submit a pull request

---

## License

MIT License - See [LICENSE](LICENSE) for details.

This tool is for personal and educational use. Users are responsible for complying with terms of service of websites they access. Support official creators.
