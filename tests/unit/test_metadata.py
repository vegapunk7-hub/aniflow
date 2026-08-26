"""Tests for metadata extraction."""

from __future__ import annotations

import pytest

from aniflow.extractors.metadata import MetadataExtractor


class TestDurationParsing:
    """Tests for duration parsing."""

    def test_parse_duration_mmss(self) -> None:
        """Test parsing mm:ss format."""
        result = MetadataExtractor.parse_duration("24:30")
        assert result == 24 * 60 + 30

    def test_parse_duration_hhmmss(self) -> None:
        """Test parsing hh:mm:ss format."""
        result = MetadataExtractor.parse_duration("1:24:30")
        assert result == 3600 + 24 * 60 + 30

    def test_parse_duration_seconds(self) -> None:
        """Test parsing seconds format."""
        result = MetadataExtractor.parse_duration("1440")
        assert result == 1440

    def test_parse_duration_none(self) -> None:
        """Test parsing None returns None."""
        result = MetadataExtractor.parse_duration(None)
        assert result is None


class TestFillerDetection:
    """Tests for filler episode detection."""

    def test_detect_filler_keyword(self) -> None:
        """Test detecting filler episode by keyword."""
        assert MetadataExtractor.is_filler_episode("Filler Episode", 1)
        assert MetadataExtractor.is_filler_episode("Recap Special", 1)
        assert MetadataExtractor.is_filler_episode("OVA Episode", 1)

    def test_detect_normal_episode(self) -> None:
        """Test normal episode not detected as filler."""
        assert not MetadataExtractor.is_filler_episode("Episode 1: Beginning", 1)
        assert not MetadataExtractor.is_filler_episode("The Final Battle", 12)


class TestQualityExtraction:
    """Tests for quality extraction."""

    def test_extract_qualities(self) -> None:
        """Test extracting quality options."""
        result = MetadataExtractor.extract_quality_options("360p, 720p, 1080p")
        assert set(result) == {360, 720, 1080}
        assert result == [1080, 720, 360]  # Sorted descending

    def test_extract_qualities_no_p_suffix(self) -> None:
        """Test extracting qualities without 'p' suffix."""
        result = MetadataExtractor.extract_quality_options("360, 720, 1080")
        assert set(result) == {360, 720, 1080}

    def test_extract_qualities_empty(self) -> None:
        """Test extracting from empty string."""
        result = MetadataExtractor.extract_quality_options("")
        assert result == []


class TestAudioExtraction:
    """Tests for audio track extraction."""

    def test_extract_audio_tracks(self) -> None:
        """Test extracting audio tracks."""
        result = MetadataExtractor.extract_audio_tracks("Japanese, English, Spanish")
        assert result == ["japanese", "english", "spanish"]

    def test_extract_audio_single(self) -> None:
        """Test extracting single audio track."""
        result = MetadataExtractor.extract_audio_tracks("Japanese")
        assert result == ["japanese"]

    def test_extract_audio_empty(self) -> None:
        """Test extracting from empty string."""
        result = MetadataExtractor.extract_audio_tracks("")
        assert result == []
