from __future__ import annotations

from collections.abc import Callable

from libs.ddd.domain_event import DomainEvent


class ApplicationEventPublisher:
    def __init__(self) -> None:
        self._handlers: list[Callable[[DomainEvent], None]] = []

    def subscribe(self, handler: Callable[[DomainEvent], None]) -> None:
        self._handlers.append(handler)

    def publish_event(self, event: DomainEvent) -> None:
        for handler in self._handlers:
            handler(event)
