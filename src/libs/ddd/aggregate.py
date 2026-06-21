from __future__ import annotations

from typing import TypeVar

from libs.ddd.base_entity import BaseEntity
from libs.ddd.domain_event import DomainEvent
from libs.primitives import Comparable

TId = TypeVar("TId", bound=Comparable)


class Aggregate(BaseEntity[TId]):
    def __init__(self, id: TId | None = None) -> None:
        super().__init__(id)
        self._domain_events: list[DomainEvent] = []

    def get_domain_events(self) -> list[DomainEvent]:
        return list(self._domain_events)

    def clear_domain_events(self) -> None:
        self._domain_events.clear()

    def raise_domain_event(self, domain_event: DomainEvent) -> None:
        self._domain_events.append(domain_event)
