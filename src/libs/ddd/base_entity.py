from __future__ import annotations

from abc import ABC
from typing import Generic, TypeVar

from libs.primitives import Comparable

TId = TypeVar("TId", bound=Comparable)


class BaseEntity(ABC, Generic[TId]):
    id: TId | None

    def __init__(self, id: TId | None = None) -> None:
        self.id = id

    def is_transient(self) -> bool:
        default = self.default_value()
        return self.id is None or self.id == default

    def default_value(self) -> TId | None:
        return None

    def __eq__(self, other: object) -> bool:
        if other is None:
            return False
        if self is other:
            return True
        if not isinstance(other, BaseEntity):
            return False
        if type(self) is not type(other):
            return False
        if self.is_transient() or other.is_transient():
            return False
        return self.id == other.id

    # Entities are mutable (id changes on persistence), therefore they must not
    # be used as dict keys or stored in sets.
    __hash__ = None

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, BaseEntity):
            return NotImplemented
        if type(self) is not type(other):
            return NotImplemented
        if self.id is None or other.id is None:
            return NotImplemented
        return self.id < other.id
