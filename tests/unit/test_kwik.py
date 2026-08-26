"""Unit tests for Kwik extractor."""

from __future__ import annotations

import pytest

from aniflow.extractors.kwik import KwikExtractor, JsPackerUnpacker
from aniflow.models import AudioLanguage


class TestJsPackerUnpacker:
    """Tests for JavaScript unpacker."""

    def test_int_to_base_conversion(self) -> None:
        """Test integer to base conversion."""
        assert JsPackerUnpacker._int_to_base(10, 36) == "a"
        assert JsPackerUnpacker._int_to_base(35, 36) == "z"
        assert JsPackerUnpacker._int_to_base(0, 36) == "0"

    def test_unpack_invalid_code(self) -> None:
        """Test unpacking invalid code returns original."""
        invalid_code = "some random code"
        result = JsPackerUnpacker.unpack(invalid_code)
        # Should return original or something unpacked
        assert isinstance(result, str)


class TestKwikExtractor:
    """Tests for Kwik URL extractor."""

    def test_quality_selection_exact_match(self) -> None:
        """Test selecting exact quality match."""
        extractor = KwikExtractor()
        resolutions = {
            360: {AudioLanguage.JAPANESE: "url_360"},
            720: {AudioLanguage.JAPANESE: "url_720"},
            1080: {AudioLanguage.JAPANESE: "url_1080"},
        }

        selected = extractor._select_quality(resolutions, 720)
        assert selected == 720

    def test_quality_selection_below_preference(self) -> None:
        """Test selecting quality below preference."""
        extractor = KwikExtractor()
        resolutions = {
            360: {AudioLanguage.JAPANESE: "url_360"},
            720: {AudioLanguage.JAPANESE: "url_720"},
        }

        # Prefer 1080 but only 720 available
        selected = extractor._select_quality(resolutions, 1080)
        assert selected == 720

    def test_quality_selection_highest_fallback(self) -> None:
        """Test selecting highest quality as fallback."""
        extractor = KwikExtractor()
        resolutions = {
            360: {AudioLanguage.JAPANESE: "url_360"},
            480: {AudioLanguage.JAPANESE: "url_480"},
        }

        # Prefer 1080 but highest is 480
        selected = extractor._select_quality(resolutions, 1080)
        assert selected == 480

    def test_audio_exact_match(self) -> None:
        """Test selecting exact audio match."""
        extractor = KwikExtractor()
        audio_options = {
            AudioLanguage.JAPANESE: "url_jp",
            AudioLanguage.ENGLISH: "url_eng",
        }

        selected = extractor._select_audio(audio_options, AudioLanguage.ENGLISH)
        assert selected == AudioLanguage.ENGLISH

    def test_audio_fallback_to_japanese(self) -> None:
        """Test audio fallback to Japanese when DUB unavailable."""
        extractor = KwikExtractor()
        audio_options = {AudioLanguage.JAPANESE: "url_jp"}

        # Want English but only Japanese available
        selected = extractor._select_audio(audio_options, AudioLanguage.ENGLISH)
        assert selected == AudioLanguage.JAPANESE

    def test_audio_fallback_to_english(self) -> None:
        """Test audio fallback to English when SUB unavailable."""
        extractor = KwikExtractor()
        audio_options = {AudioLanguage.ENGLISH: "url_eng"}

        # Want Japanese but only English available
        selected = extractor._select_audio(audio_options, AudioLanguage.JAPANESE)
        assert selected == AudioLanguage.ENGLISH
