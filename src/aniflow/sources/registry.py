"""Registry for anime sources."""

from __future__ import annotations

from typing import Any

from aniflow.sources.base import BaseSource


class SourceRegistry:
    """Registry for managing anime source plugins."""

    def __init__(self) -> None:
        """Initialize source registry."""
        self._sources: dict[str, type[BaseSource]] = {}

    def register(self, source_class: type[BaseSource]) -> None:
        """Register a source plugin."""
        source_name = source_class.source_name
        self._sources[source_name] = source_class

    def get_source(self, name: str) -> BaseSource | None:
        """Get a source instance by name."""
        source_class = self._sources.get(name)
        if source_class:
            return source_class()
        return None

    def list_sources(self) -> list[str]:
        """List all registered sources."""
        return list(self._sources.keys())


# Global registry instance
_registry = SourceRegistry()


def get_registry() -> SourceRegistry:
    """Get the global source registry."""
    return _registry
