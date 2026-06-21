from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any


class ValueObject(ABC):
    @abstractmethod
    def equality_components(self) -> Iterable[Any]:
        ...

    @staticmethod
    def _safe_compare(a: Any, b: Any) -> int:
        if a is b:
            return 0
        if a is None:
            return -1
        if b is None:
            return 1
        if a == b:
            return 0
        try:
            return -1 if a < b else 1
        except TypeError as exc:
            raise TypeError(f"Fields must be comparable: {a!r} and {b!r}") from exc

    @staticmethod
    def _to_list(iterable: Iterable[Any]) -> list[Any]:
        return list(iterable)

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True
        if other is None or type(self) is not type(other):
            return False
        this_components = self._to_list(self.equality_components())
        that_components = self._to_list(other.equality_components())
        if len(this_components) != len(that_components):
            return False
        return all(a == b for a, b in zip(this_components, that_components, strict=True))

    def __hash__(self) -> int:
        return hash(tuple(self._to_list(self.equality_components())))

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, ValueObject) or type(self) is not type(other):
            return NotImplemented
        this_components = self._to_list(self.equality_components())
        other_components = self._to_list(other.equality_components())
        for this_value, other_value in zip(this_components, other_components, strict=False):
            result = self._safe_compare(this_value, other_value)
            if result != 0:
                return result < 0
        return len(this_components) < len(other_components)

    def __repr__(self) -> str:
        components = self._to_list(self.equality_components())
        body = ", ".join(repr(component) for component in components)
        return f"{type(self).__name__}[{body}]"
