from __future__ import annotations

from typing import Protocol, TypeVar

from libs.ddd.domain_event import DomainEvent
from libs.primitives import Comparable

TId = TypeVar("TId", bound=Comparable)


class AggregateRoot(Protocol[TId]):
    @property
    def id(self) -> TId | None: ...

    def get_domain_events(self) -> list[DomainEvent]: ...

    def clear_domain_events(self) -> None: ...
