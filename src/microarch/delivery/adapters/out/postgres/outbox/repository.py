from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from libs.ddd.aggregate import Aggregate
from libs.ddd.domain_event import DomainEvent
from microarch.delivery.adapters.out.postgres.outbox.mapper import OutboxMapper
from microarch.delivery.adapters.out.postgres.outbox.models import OutboxMessage


class OutboxRepository:
    """Репозиторий для чтения и записи outbox-сообщений."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, event: DomainEvent, aggregate: Aggregate) -> None:
        """Сохранить доменное событие агрегата в outbox."""
        message = OutboxMapper.to_outbox_message(event, aggregate)
        self._session.add(message)

    async def get_unprocessed(self) -> list[OutboxMessage]:
        """Получить все неотправленные сообщения."""
        result = await self._session.execute(
            select(OutboxMessage).where(OutboxMessage.processed_on_utc.is_(None)),
        )
        return list(result.scalars().all())

    async def mark_as_processed(self, message: OutboxMessage) -> None:
        """Пометить сообщение как успешно отправленное."""
        message.mark_as_processed()
        await self._session.merge(message)
