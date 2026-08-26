"""Kwik URL extractor with JS deobfuscation."""

from __future__ import annotations

import re
from typing import Any

from aniflow.http import HttpClient
from aniflow.models import AudioLanguage


class JsPackerUnpacker:
    """Unpack JavaScript packed with Dean Edwards' packer."""

    @staticmethod
    def unpack(packed_code: str) -> str:
        """Unpack p,a,c,k,e,d JavaScript code.

        Args:
            packed_code: Packed JavaScript

        Returns:
            Unpacked JavaScript
        """
        # Extract parameters
        pattern = r"eval\(function\(p,a,c,k,e,r\)\{.*?return p\.replace\(.*?\}"
        match = re.search(pattern, packed_code, re.DOTALL)
        if not match:
            return packed_code

        # Extract the function call parameters
        func_call_pattern = r"\}\('([^']*)',([\d]+),'([^']*)'.*?\)\)"
        func_match = re.search(func_call_pattern, packed_code, re.DOTALL)

        if not func_match:
            return packed_code

        try:
            code_str = func_match.group(1)
            radix = int(func_match.group(2))
            keys_str = func_match.group(3)

            # Parse keys
            keys = keys_str.split("|")

            # Replace tokens
            for i in range(len(keys) - 1, 0, -1):
                token = keys[i]
                if token:
                    # Convert index to base-radix representation
                    replacement = JsPackerUnpacker._int_to_base(i, radix)
                    code_str = code_str.replace(replacement, token)

            return code_str
        except Exception:
            return packed_code

    @staticmethod
    def _int_to_base(num: int, base: int) -> str:
        """Convert integer to base-N representation.

        Args:
            num: Number to convert
            base: Base for conversion

        Returns:
            Base-N representation
        """
        if num == 0:
            return "0"

        digits = "0123456789abcdefghijklmnopqrstuvwxyz"
        result = ""
        while num:
            result = digits[num % base] + result
            num //= base
        return result


class KwikExtractor:
    """Extract Kwik URLs and M3U8 manifests from AnimePahe."""

    def __init__(self) -> None:
        """Initialize Kwik extractor."""
        self.http = HttpClient(max_retries=5)
        self.kwik_base = "https://kwik.si"

    async def extract_from_animepahe_page(
        self,
        page_content: str,
        quality: int = 1080,
        audio_lang: AudioLanguage = AudioLanguage.JAPANESE,
    ) -> tuple[str, int, AudioLanguage]:
        """Extract M3U8 URL from AnimePahe episode page.

        Args:
            page_content: HTML content of AnimePahe episode page
            quality: Preferred quality (360/720/1080)
            audio_lang: Preferred audio language

        Returns:
            Tuple of (m3u8_url, actual_quality, actual_audio_lang)
        """
        # Parse resolution buttons
        resolutions = self._parse_resolution_buttons(page_content)
        if not resolutions:
            raise ValueError("No resolution options found on page")

        # Select best matching quality
        selected_quality = self._select_quality(resolutions, quality)
        selected_audio = self._select_audio(
            resolutions[selected_quality], audio_lang
        )

        # Get Kwik URL from selected button
        kwik_url = resolutions[selected_quality][selected_audio]
        if not kwik_url:
            raise ValueError(f"No Kwik URL found for {selected_quality}p/{selected_audio.value}")

        # Resolve Kwik URL to M3U8
        m3u8_url = await self._resolve_kwik_to_m3u8(kwik_url)
        return m3u8_url, selected_quality, selected_audio

    def _parse_resolution_buttons(self, page_content: str) -> dict[int, dict[AudioLanguage, str]]:
        """Parse resolution buttons from AnimePahe page.

        Args:
            page_content: Page HTML

        Returns:
            Dict of {quality: {audio_lang: kwik_url}}
        """
        resolutions: dict[int, dict[AudioLanguage, str]] = {}

        # Find resolution buttons
        button_pattern = r'<a[^>]*data-src="([^"]+)"[^>]*data-resolution="(\d+)[^>]*data-audio="([^"]+)"'
        matches = re.finditer(button_pattern, page_content)

        for match in matches:
            kwik_url = match.group(1)
            quality = int(match.group(2))
            audio = match.group(3)

            # Parse audio language
            if "dub" in audio.lower():
                audio_lang = AudioLanguage.ENGLISH
            else:
                audio_lang = AudioLanguage.JAPANESE

            if quality not in resolutions:
                resolutions[quality] = {}
            resolutions[quality][audio_lang] = kwik_url

        return resolutions

    @staticmethod
    def _select_quality(
        resolutions: dict[int, dict[AudioLanguage, str]],
        preferred_quality: int,
    ) -> int:
        """Select best matching quality.

        Strategy:
        1. Exact match if available
        2. Closest below preferred
        3. Highest available

        Args:
            resolutions: Available resolutions
            preferred_quality: Preferred quality

        Returns:
            Selected quality
        """
        available = sorted(resolutions.keys())

        # Exact match
        if preferred_quality in available:
            return preferred_quality

        # Closest below preferred
        below = [q for q in available if q < preferred_quality]
        if below:
            return max(below)

        # Highest available
        return max(available)

    @staticmethod
    def _select_audio(
        audio_options: dict[AudioLanguage, str],
        preferred_audio: AudioLanguage,
    ) -> AudioLanguage:
        """Select audio language.

        Strategy:
        1. Exact match
        2. Fallback to Japanese if DUB preferred but unavailable
        3. Fallback to English if JAP preferred but unavailable
        4. Any available

        Args:
            audio_options: Available audio languages
            preferred_audio: Preferred language

        Returns:
            Selected language
        """
        # Exact match
        if preferred_audio in audio_options:
            return preferred_audio

        # Fallback strategy
        if preferred_audio == AudioLanguage.ENGLISH and AudioLanguage.JAPANESE in audio_options:
            return AudioLanguage.JAPANESE
        elif preferred_audio == AudioLanguage.JAPANESE and AudioLanguage.ENGLISH in audio_options:
            return AudioLanguage.ENGLISH

        # Any available
        return next(iter(audio_options.keys()))

    async def _resolve_kwik_to_m3u8(self, kwik_url: str) -> str:
        """Resolve Kwik URL to M3U8 manifest.

        Args:
            kwik_url: Kwik player URL

        Returns:
            M3U8 manifest URL
        """
        await self.http.start()

        try:
            # Fetch Kwik page (no FlareSolverr needed for this hop)
            headers = {"Referer": "https://animepahe.com/"}
            content = await self.http.get(kwik_url, headers=headers)

            # Strategy 1: Direct regex match
            m3u8_match = re.search(r'["\']([^"\']*/master\.m3u8[^"\']*)["\'']', content)
            if m3u8_match:
                return m3u8_match.group(1)

            # Strategy 2: JS deobfuscation
            unpacked = JsPackerUnpacker.unpack(content)
            m3u8_match = re.search(r'["\']([^"\']*/master\.m3u8[^"\']*)["\'']', unpacked)
            if m3u8_match:
                return m3u8_match.group(1)

            # Strategy 3: Source tag extraction
            source_match = re.search(
                r'<source[^>]*src="([^"]*\.m3u8[^"]*)"',
                content,
                re.IGNORECASE,
            )
            if source_match:
                return source_match.group(1)

            raise ValueError("Could not extract M3U8 URL from Kwik page")
        finally:
            await self.http.close()
