"""Tests for configuration manager."""

from __future__ import annotations

import pytest
from pathlib import Path

from aniflow.config_manager import ConfigManager


def test_config_defaults() -> None:
    """Test config loads with defaults."""
    manager = ConfigManager(config_file=Path("/nonexistent/path.toml"))
    assert manager.config.default_quality == 1080
    assert manager.config.max_parallel_episodes == 2
    assert manager.config.hls_workers == 24


def test_config_get(tmp_path: Path) -> None:
    """Test getting config values."""
    manager = ConfigManager(config_file=tmp_path / "test.toml")
    assert manager.get("default_quality") == 1080
    assert manager.get("max_parallel_episodes") == 2


def test_config_set_quality(tmp_path: Path) -> None:
    """Test setting quality config."""
    manager = ConfigManager(config_file=tmp_path / "test.toml")
    manager.set("default_quality", 720)
    assert manager.config.default_quality == 720


def test_config_set_quality_validation(tmp_path: Path) -> None:
    """Test quality validation."""
    manager = ConfigManager(config_file=tmp_path / "test.toml")
    with pytest.raises(ValueError):
        manager.set("default_quality", 2160)  # Invalid quality


def test_config_set_parallel_clamping(tmp_path: Path) -> None:
    """Test parallel episodes clamping."""
    manager = ConfigManager(config_file=tmp_path / "test.toml")
    manager.set("max_parallel_episodes", 100)  # Should clamp to 8
    assert manager.config.max_parallel_episodes == 8


def test_config_save_load(tmp_path: Path) -> None:
    """Test saving and loading config."""
    config_file = tmp_path / "aniflow.toml"
    manager1 = ConfigManager(config_file=config_file)
    manager1.set("default_quality", 720)
    manager1.save()

    # Load and verify
    manager2 = ConfigManager(config_file=config_file)
    assert manager2.config.default_quality == 720


def test_config_reset(tmp_path: Path) -> None:
    """Test resetting config."""
    manager = ConfigManager(config_file=tmp_path / "test.toml")
    manager.set("default_quality", 720)
    assert manager.config.default_quality == 720

    manager.reset()
    assert manager.config.default_quality == 1080  # Back to default
