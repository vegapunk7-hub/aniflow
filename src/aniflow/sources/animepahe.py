"""AnimePahe source plugin."""

from __future__ import annotations

import asyncio
import json
import re
from typing import Any

from aniflow.http import HttpClient
from aniflow.models import AnimeInfo, AudioLanguage, EpisodeInfo
from aniflow.sources.base import BaseSource, StreamNotFoundError, SourceUnavailableError


class AnimepaheSource(BaseSource):
    """AnimePahe anime source plugin."""

    source_name = "animepahe"
    base_url = "https://animepahe.com"
    api_url = "https://animepahe.com/api"

    def __init__(self) -> None:
        """Initialize AnimePahe source."""
        self.http = HttpClient(max_retries=5)

    async def search(self, query: str) -> list[AnimeInfo]:
        """Search for anime by title.

        Args:
            query: Search query

        Returns:
            List of matching anime
        """
        try:
            await self.http.start()
            url = f"{self.api_url}/anime?query={query}&limit=20"
            response_text = await self.http.get(url)
            data = json.loads(response_text)

            results = []
            for item in data.get("data", []):
                anime = AnimeInfo(
                    title=item["title"],
                    url=f"{self.base_url}/anime/{item['slug']}",
                    source=self.source_name,
                    year=item.get("year"),
                    total_episodes=item.get("episodes"),
                )
                results.append(anime)

            return results
        except Exception as e:
            raise SourceUnavailableError(f"AnimePahe search failed: {e}")

    async def get_anime_info(self, url: str) -> AnimeInfo:
        """Get detailed anime information from URL.

        Args:
            url: Anime URL

        Returns:
            Anime information with episodes
        """
        try:
            await self.http.start()
            response_text = await self.http.get(url)

            # Extract anime ID from URL
            match = re.search(r"/anime/([a-z0-9-]+)", url)
            if not match:
                raise StreamNotFoundError("Cannot extract anime ID from URL")

            slug = match.group(1)
            anime_url = f"{self.api_url}/anime/{slug}"
            anime_data = json.loads(await self.http.get(anime_url))
            data = anime_data["data"]

            # Get episodes
            episodes_url = f"{self.api_url}/anime/{slug}/episodes?sort=asc"
            episodes_data = json.loads(await self.http.get(episodes_url))

            episodes = []
            for ep_data in episodes_data.get("data", []):
                episode = EpisodeInfo(
                    episode_number=int(ep_data["episode"]),
                    title=ep_data.get("title", f"Episode {ep_data['episode']}"),
                    url=url,  # Use base anime URL
                    duration_seconds=ep_data.get("duration"),
                    available_qualities=[720, 1080],  # AnimePahe typical qualities
                    available_audio=[AudioLanguage.JAPANESE, AudioLanguage.ENGLISH],
                )
                episodes.append(episode)

            return AnimeInfo(
                title=data["title"],
                url=url,
                source=self.source_name,
                episodes=sorted(episodes, key=lambda x: x.episode_number),
                total_episodes=len(episodes),
                year=data.get("year"),
                rating=data.get("score"),
                description=data.get("synopsis"),
            )
        except Exception as e:
            raise SourceUnavailableError(f"Failed to get anime info from AnimePahe: {e}")

    async def get_episode_stream(self, episode: EpisodeInfo, quality: int) -> str:
        """Get M3U8 stream URL for episode.

        Args:
            episode: Episode information
            quality: Desired quality (360/720/1080)

        Returns:
            M3U8 stream URL
        """
        try:
            await self.http.start()
            response_text = await self.http.get(episode.url)

            # This is a simplified version - actual implementation requires
            # FlareSolverr for Cloudflare bypass and complex JS parsing
            # Real implementation: extract Kwik URL, resolve to M3U8
            raise StreamNotFoundError(
                "Full stream extraction requires FlareSolverr integration"
            )
        except Exception as e:
            raise StreamNotFoundError(f"Cannot get stream for episode {episode.episode_number}: {e}")

    async def is_available(self) -> bool:
        """Check if source is currently accessible.

        Returns:
            True if source is available
        """
        try:
            await self.http.start()
            response = await self.http.get(self.base_url, allow_redirects=True)
            return True
        except Exception:
            return False
        finally:
            await self.http.close()
