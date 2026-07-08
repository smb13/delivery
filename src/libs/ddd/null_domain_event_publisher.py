from __future__ import annotations

from collections.abc import Iterable

from libs.ddd.aggregate import Aggregate
from libs.ddd.domain_event_publisher import DomainEventPublisher


class NullDomainEventPublisher(DomainEventPublisher):
    """No-op реализация публикации доменных событий.

    Используется в сценариях, где публикация событий не требуется
    или инфраструктура брокера недоступна.
    """

    async def publish(self, aggregates: Iterable[Aggregate]) -> None:
        pass
