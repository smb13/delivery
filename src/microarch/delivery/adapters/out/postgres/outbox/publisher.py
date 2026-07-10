from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy.ext.asyncio import AsyncSession

from libs.ddd.aggregate import Aggregate
from libs.ddd.domain_event_publisher import DomainEventPublisher
from microarch.delivery.adapters.out.postgres.outbox.repository import OutboxRepository


class OutboxDomainEventPublisher(DomainEventPublisher):
    """Реализация DomainEventPublisher, сохраняющая события в таблицу outbox.

    Запись происходит в рамках текущей транзакции сессии, поэтому
    агрегат и событие фиксируются атомарно.
    """

    def __init__(self, repository: OutboxRepository) -> None:
        self._repository = repository

    async def publish(self, aggregates: Iterable[Aggregate]) -> None:
        """Сохранить доменные события агрегатов в outbox."""
        for aggregate in aggregates:
            for event in aggregate.get_domain_events():
                await self._repository.add(event, aggregate)
            aggregate.clear_domain_events()


def create_outbox_domain_event_publisher(
    session: AsyncSession,
) -> DomainEventPublisher:
    """Фабрика для создания outbox-публикатора на основе сессии БД."""
    return OutboxDomainEventPublisher(OutboxRepository(session))
