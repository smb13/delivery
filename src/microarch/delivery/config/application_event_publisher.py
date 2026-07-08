from __future__ import annotations

from collections.abc import Awaitable, Callable

from libs.ddd.domain_event import DomainEvent


class ApplicationEventPublisher:
    """Внутренний in-memory брокер доменных событий приложения."""

    def __init__(self) -> None:
        self._handlers: list[Callable[[DomainEvent], Awaitable[None]]] = []

    def subscribe(self, handler: Callable[[DomainEvent], Awaitable[None]]) -> None:
        self._handlers.append(handler)

    async def publish_event(self, event: DomainEvent) -> None:
        for handler in self._handlers:
            await handler(event)
