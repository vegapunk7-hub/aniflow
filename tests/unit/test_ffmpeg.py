"""Tests for FFmpeg muxer."""

from __future__ import annotations

import pytest

from aniflow.downloader.ffmpeg import FFmpegMuxer


def test_create_concat_file(tmp_path) -> None:
    """Test creating FFmpeg concat file."""
    segment_dir = tmp_path / "segments"
    segment_dir.mkdir()

    # Create segment files
    for i in range(3):
        (segment_dir / f"{i:06d}.ts").write_bytes(b"test")

    concat_file = segment_dir / "concat.txt"
    FFmpegMuxer._create_concat_file(segment_dir, concat_file)

    assert concat_file.exists()
    content = concat_file.read_text()
    assert "000000.ts" in content
    assert "000001.ts" in content
    assert "000002.ts" in content


def test_create_concat_file_no_segments(tmp_path) -> None:
    """Test creating concat file with no segments."""
    segment_dir = tmp_path / "empty"
    segment_dir.mkdir()

    concat_file = segment_dir / "concat.txt"

    from aniflow.downloader.ffmpeg import FFmpegError
    with pytest.raises(FFmpegError):
        FFmpegMuxer._create_concat_file(segment_dir, concat_file)
