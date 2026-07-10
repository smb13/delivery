from __future__ import annotations

from collections.abc import Awaitable, Iterable
from typing import Protocol

from libs.ddd.aggregate import Aggregate


class DomainEventPublisher(Protocol):
    def publish(self, aggregates: Iterable[Aggregate]) -> Awaitable[None]: ...
