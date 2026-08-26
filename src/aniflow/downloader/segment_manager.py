"""HLS segment downloader with AES-128 decryption and atomic writes."""

from __future__ import annotations

import asyncio
import hashlib
from pathlib import Path
from typing import Any

from Cryptodome.Cipher import AES

from aniflow.http import HttpClient
from aniflow.models import DownloadStatus


class SegmentDownloadError(Exception):
    """Raised when segment download fails."""

    pass


class SegmentManager:
    """Manages HLS segment downloads with crash recovery."""

    def __init__(self, cache_dir: Path | None = None) -> None:
        """Initialize segment manager.

        Args:
            cache_dir: Cache directory for segments
        """
        self.cache_dir = cache_dir or Path("./pahe_cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.http = HttpClient(max_retries=5)

    async def download_segment(
        self,
        url: str,
        output_path: Path,
        encryption_key: bytes | None = None,
        encryption_iv: bytes | None = None,
        headers: dict[str, str] | None = None,
    ) -> int:
        """Download a single HLS segment with atomic write.

        Args:
            url: Segment URL
            output_path: Output file path
            encryption_key: AES-128 key (if encrypted)
            encryption_iv: AES-128 IV (if encrypted)
            headers: Additional HTTP headers

        Returns:
            Bytes downloaded
        """
        await self.http.start()

        try:
            # Download to temporary file
            temp_path = output_path.with_suffix(".tmp")
            segment_data = await self.http.get_bytes(url, headers=headers)

            # Decrypt if needed
            if encryption_key and encryption_iv:
                cipher = AES.new(encryption_key, AES.MODE_CBC, encryption_iv)
                segment_data = cipher.decrypt(segment_data)
                # Remove PKCS7 padding
                padding_length = segment_data[-1]
                segment_data = segment_data[:-padding_length]

            # Write to temporary file
            temp_path.write_bytes(segment_data)

            # Atomic rename
            temp_path.rename(output_path)

            return len(segment_data)
        except Exception as e:
            raise SegmentDownloadError(f"Failed to download segment {url}: {e}")

    async def download_segments_concurrent(
        self,
        segments: list[tuple[int, str]],  # (index, url)
        output_dir: Path,
        encryption_key: bytes | None = None,
        encryption_iv: bytes | None = None,
        max_workers: int = 24,
        headers: dict[str, str] | None = None,
    ) -> dict[int, int]:
        """Download multiple segments concurrently.

        Args:
            segments: List of (index, url) tuples
            output_dir: Output directory
            encryption_key: AES-128 key
            encryption_iv: AES-128 IV
            max_workers: Maximum concurrent downloads
            headers: Additional headers

        Returns:
            Dict of {segment_index: bytes_downloaded}
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        semaphore = asyncio.Semaphore(max_workers)
        results = {}

        async def download_with_semaphore(index: int, url: str) -> tuple[int, int]:
            async with semaphore:
                output_path = output_dir / f"{index:06d}.ts"

                # Skip if already downloaded
                if output_path.exists():
                    return index, output_path.stat().st_size

                bytes_downloaded = await self.download_segment(
                    url,
                    output_path,
                    encryption_key,
                    encryption_iv,
                    headers,
                )
                return index, bytes_downloaded

        tasks = [download_with_semaphore(idx, url) for idx, url in segments]
        download_results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in download_results:
            if isinstance(result, Exception):
                # Continue on individual segment failure
                continue
            else:
                index, bytes_count = result
                results[index] = bytes_count

        return results

    def get_downloaded_segments(self, output_dir: Path) -> set[int]:
        """Get list of already downloaded segment indices.

        Args:
            output_dir: Output directory

        Returns:
            Set of downloaded segment indices
        """
        if not output_dir.exists():
            return set()

        downloaded = set()
        for ts_file in output_dir.glob("*.ts"):
            try:
                index = int(ts_file.stem)
                downloaded.add(index)
            except ValueError:
                continue

        return downloaded

    @staticmethod
    def parse_encryption_key(key_string: str) -> bytes:
        """Parse encryption key from hex or URI.

        Args:
            key_string: Encryption key string

        Returns:
            Bytes key
        """
        if key_string.startswith("0x"):
            return bytes.fromhex(key_string[2:])
        elif key_string.startswith("http"):
            # Should be fetched from URL
            raise NotImplementedError("URL-based key fetching not yet implemented")
        else:
            return bytes.fromhex(key_string)

    @staticmethod
    def hash_segment(data: bytes) -> str:
        """Calculate SHA256 hash of segment data.

        Args:
            data: Segment data

        Returns:
            Hex hash string
        """
        return hashlib.sha256(data).hexdigest()
