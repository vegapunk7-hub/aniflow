"""FFmpeg-based video muxing and encoding."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any


class FFmpegError(Exception):
    """Raised when FFmpeg operation fails."""

    pass


class FFmpegMuxer:
    """Handle video muxing and encoding via FFmpeg."""

    def __init__(self, ffmpeg_path: str = "ffmpeg") -> None:
        """Initialize FFmpeg muxer.

        Args:
            ffmpeg_path: Path to ffmpeg executable
        """
        self.ffmpeg_path = ffmpeg_path

    async def mux_segments(
        self,
        segment_dir: Path,
        output_file: Path,
        duration: float | None = None,
    ) -> None:
        """Mux TS segments into MP4 file.

        Args:
            segment_dir: Directory containing TS segments
            output_file: Output MP4 file path
            duration: Total duration in seconds (for validation)
        """
        concat_file = segment_dir / "concat.txt"
        self._create_concat_file(segment_dir, concat_file)

        try:
            # Use concat demuxer for fast muxing (no re-encoding)
            cmd = [
                self.ffmpeg_path,
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_file),
                "-c", "copy",  # Copy codec (no re-encoding)
                "-movflags", "+faststart",  # Enable streaming
                str(output_file),
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                # Fallback to pipe mode if concat demuxer fails
                await self._mux_segments_pipe_mode(segment_dir, output_file)
        except Exception as e:
            raise FFmpegError(f"Muxing failed: {e}")

    async def mux_segments_with_encoding(
        self,
        segment_dir: Path,
        output_file: Path,
        video_codec: str = "h264",
        audio_codec: str = "aac",
        bitrate: str | None = None,
    ) -> None:
        """Mux segments with optional re-encoding.

        Args:
            segment_dir: Directory containing TS segments
            output_file: Output file path
            video_codec: Video codec (h264, h265, vp9)
            audio_codec: Audio codec (aac, opus)
            bitrate: Target bitrate (e.g., "5M", "10000k")
        """
        concat_file = segment_dir / "concat.txt"
        self._create_concat_file(segment_dir, concat_file)

        try:
            cmd = [
                self.ffmpeg_path,
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_file),
                "-c:v", video_codec,
                "-c:a", audio_codec,
                "-movflags", "+faststart",
            ]

            if bitrate:
                cmd.extend(["-b:v", bitrate])

            cmd.append(str(output_file))

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                raise FFmpegError(f"Encoding failed: {stderr.decode()}")
        except Exception as e:
            raise FFmpegError(f"Encoding with transcoding failed: {e}")

    async def get_video_info(self, video_file: Path) -> dict[str, Any]:
        """Get video information via FFprobe.

        Args:
            video_file: Path to video file

        Returns:
            Video metadata
        """
        try:
            cmd = [
                "ffprobe",
                "-v", "error",
                "-show_format",
                "-show_streams",
                "-of", "json",
                str(video_file),
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                return json.loads(stdout.decode())
            else:
                raise FFmpegError(f"FFprobe failed: {stderr.decode()}")
        except Exception as e:
            raise FFmpegError(f"Could not get video info: {e}")

    @staticmethod
    def _create_concat_file(segment_dir: Path, output_file: Path) -> None:
        """Create FFmpeg concat demuxer file.

        Args:
            segment_dir: Directory containing TS segments
            output_file: Output concat file path
        """
        segments = sorted(segment_dir.glob("*.ts"))
        if not segments:
            raise FFmpegError(f"No TS files found in {segment_dir}")

        with output_file.open("w") as f:
            for segment in segments:
                f.write(f"file '{segment.absolute()}'\n")

    async def _mux_segments_pipe_mode(
        self,
        segment_dir: Path,
        output_file: Path,
    ) -> None:
        """Fallback: mux segments using pipe mode.

        Args:
            segment_dir: Directory containing TS segments
            output_file: Output file path
        """
        try:
            cmd = [
                self.ffmpeg_path,
                "-i", "pipe:0",
                "-c", "copy",
                "-movflags", "+faststart",
                str(output_file),
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            # Pipe segments to FFmpeg stdin
            segments = sorted(segment_dir.glob("*.ts"))
            for segment_file in segments:
                data = segment_file.read_bytes()
                process.stdin.write(data)

            process.stdin.close()
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                raise FFmpegError(f"Pipe mode muxing failed: {stderr.decode()}")
        except Exception as e:
            raise FFmpegError(f"Fallback muxing failed: {e}")
