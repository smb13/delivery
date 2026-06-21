"""Shared primitive types used across the project."""

from __future__ import annotations

from typing import Any, Protocol


class Comparable(Protocol):
    """Protocol for types that support ordering."""

    def __lt__(self, other: Any, /) -> bool: ...
