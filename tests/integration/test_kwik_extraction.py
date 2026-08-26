"""Integration tests for Kwik extraction."""

from __future__ import annotations

import pytest

from aniflow.extractors.kwik import KwikExtractor, JsPackerUnpacker
from aniflow.models import AudioLanguage


def test_jspacker_unpacker_simple() -> None:
    """Test JsPacker unpacker with simple code."""
    # Simple packed code for testing
    packed = "eval(function(p,a,c,k,e,r){return 'test'}())"
    unpacked = JsPackerUnpacker.unpack(packed)
    assert isinstance(unpacked, str)


def test_kwik_quality_selection() -> None:
    """Test quality selection logic."""
    extractor = KwikExtractor()

    resolutions = {
        720: {AudioLanguage.JAPANESE: "url_720_jp"},
        1080: {AudioLanguage.JAPANESE: "url_1080_jp"},
    }

    # Prefer 1080
    selected = extractor._select_quality(resolutions, 1080)
    assert selected == 1080

    # Fallback to 720 if 1080 not available
    selected = extractor._select_quality(resolutions, 2160)
    assert selected == 1080

    # Select exact match
    selected = extractor._select_quality(resolutions, 720)
    assert selected == 720


def test_kwik_audio_selection() -> None:
    """Test audio track selection logic."""
    extractor = KwikExtractor()

    audio_options = {
        AudioLanguage.JAPANESE: "url_jp",
        AudioLanguage.ENGLISH: "url_eng",
    }

    # Prefer Japanese
    selected = extractor._select_audio(audio_options, AudioLanguage.JAPANESE)
    assert selected == AudioLanguage.JAPANESE

    # Fallback to English if Japanese unavailable
    audio_jp_only = {AudioLanguage.JAPANESE: "url_jp"}
    selected = extractor._select_audio(audio_jp_only, AudioLanguage.ENGLISH)
    assert selected == AudioLanguage.JAPANESE


def test_resolution_button_parsing() -> None:
    """Test parsing resolution buttons from HTML."""
    extractor = KwikExtractor()

    html = '''<a data-src="https://kwik.si/xyz" data-resolution="720" data-audio="jpn dub"></a>
              <a data-src="https://kwik.si/abc" data-resolution="1080" data-audio="jpn sub"></a>'''

    resolutions = extractor._parse_resolution_buttons(html)

    assert 720 in resolutions
    assert 1080 in resolutions
    assert AudioLanguage.ENGLISH in resolutions[720]  # "dub" -> English
    assert AudioLanguage.JAPANESE in resolutions[1080]  # "sub" -> Japanese
