from __future__ import annotations

from collections.abc import Iterable

from libs.ddd.aggregate import Aggregate
from libs.ddd.domain_event_publisher import DomainEventPublisher
from microarch.delivery.config.application_event_publisher import (
    ApplicationEventPublisher,
)


class DefaultDomainEventPublisher(DomainEventPublisher):
    """Стандартная реализация публикации доменных событий.

    Извлекает накопленные события из агрегатов и передаёт их
    внутреннему application event publisher для обработки.
    """

    def __init__(self, publisher: ApplicationEventPublisher) -> None:
        self._publisher = publisher

    async def publish(self, aggregates: Iterable[Aggregate]) -> None:
        for aggregate in aggregates:
            for event in aggregate.get_domain_events():
                await self._publisher.publish_event(event)
            aggregate.clear_domain_events()
