from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from taskiq import InMemoryBroker, TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource

from microarch.delivery.adapters.out.postgres.outbox.job import OutboxJob
from microarch.delivery.adapters.out.postgres.outbox.publisher import (
    create_outbox_domain_event_publisher,
)
from microarch.delivery.adapters.out.postgres.outbox.repository import OutboxRepository
from microarch.delivery.config.container import Container
from microarch.delivery.core.application.commands.assign_order import (
    AssignOrderCommand,
)
from microarch.delivery.core.ports.domain_event_publisher import IDomainEventPublisher

broker = InMemoryBroker()
scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)],
)

_engine: AsyncEngine | None = None
_order_events_producer: IDomainEventPublisher | None = None


def configure_taskiq(
    engine: AsyncEngine,
    order_events_producer: IDomainEventPublisher | None = None,
) -> None:
    """Устанавливает engine БД и продюсер событий для фоновых задач."""
    global _engine, _order_events_producer  # noqa: PLW0603
    _engine = engine
    _order_events_producer = order_events_producer


def _create_session_maker() -> async_sessionmaker[AsyncSession]:
    if _engine is None:
        raise RuntimeError("Taskiq is not configured with a database engine")
    return async_sessionmaker(
        _engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@broker.task(schedule=[{"interval": 1}])
async def assign_order_task() -> None:
    """Периодически назначает один созданный заказ на подходящего курьера.

    Запускается каждую секунду через Taskiq scheduler.
    """
    if _engine is None:
        raise RuntimeError("Taskiq is not configured with a database engine")

    container = Container(_engine)

    command_result = AssignOrderCommand.create()
    if command_result.is_failure:
        return

    async with container.create_unit_of_work() as uow:
        handler = container.create_assign_order_handler(
            uow,
            domain_event_publisher=create_outbox_domain_event_publisher(uow.session),
        )
        await handler.handle(command_result.get_value())


@broker.task(schedule=[{"interval": 1}])
async def publish_outbox_messages() -> None:
    """Периодически публикует неотправленные outbox-сообщения в Kafka.

    Запускается каждую секунду через Taskiq scheduler.
    """
    if _engine is None or _order_events_producer is None:
        return

    session_maker = _create_session_maker()
    job = OutboxJob(session_maker, _order_events_producer, OutboxRepository)
    await job.run()
