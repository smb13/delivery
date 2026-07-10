from __future__ import annotations

import logging
from collections.abc import Callable

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from microarch.delivery.adapters.out.postgres.outbox.mapper import OutboxMapper
from microarch.delivery.adapters.out.postgres.outbox.models import OutboxMessage
from microarch.delivery.adapters.out.postgres.outbox.repository import OutboxRepository
from microarch.delivery.core.ports.domain_event_publisher import IDomainEventPublisher

logger = logging.getLogger(__name__)


class OutboxJob:
    """Фоновая задача для публикации неотправленных outbox-сообщений.

    Опрашивает таблицу outbox, отправляет сообщения через внешний публикатор
    и помечает их как обработанные. При ошибке отправки сообщение остаётся
    неотмеченным и будет повторно обработано при следующем запуске.
    """

    def __init__(
        self,
        session_maker: async_sessionmaker[AsyncSession],
        producer: IDomainEventPublisher,
        repository_factory: Callable[[AsyncSession], OutboxRepository],
    ) -> None:
        self._session_maker = session_maker
        self._producer = producer
        self._repository_factory = repository_factory

    async def run(self) -> None:
        """Выполнить один цикл отправки неотправленных сообщений."""
        async with self._session_maker() as session:
            repository = self._repository_factory(session)
            messages = await repository.get_unprocessed()

            for message in messages:
                await self._process_message(message, repository)

            await session.commit()

    async def _process_message(
        self,
        message: OutboxMessage,
        repository: OutboxRepository,
    ) -> None:
        try:
            event = OutboxMapper.to_domain_event(message)
            await self._producer.publish(event)
            await repository.mark_as_processed(message)
        except Exception:
            logger.exception("Failed to publish outbox message %s", message.id)
