from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncEngine
from taskiq import InMemoryBroker, TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource

from microarch.delivery.config.container import Container
from microarch.delivery.core.application.commands.assign_order import (
    AssignOrderCommand,
    AssignOrderCommandHandler,
)
from microarch.delivery.core.domain.services.orders_distribution_service_impl import (
    OrdersDistributionServiceImpl,
)

broker = InMemoryBroker()
scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)],
)

_engine: AsyncEngine | None = None


def configure_taskiq(engine: AsyncEngine) -> None:
    """Устанавливает engine БД для фоновых задач."""
    global _engine  # noqa: PLW0603
    _engine = engine


@broker.task(schedule=[{"interval": 1}])
async def assign_order_task() -> None:
    """Периодически назначает один созданный заказ на подходящего курьера.

    Запускается каждую секунду через Taskiq scheduler.
    """
    if _engine is None:
        raise RuntimeError("Taskiq is not configured with a database engine")

    container = Container(_engine)
    uow = container.create_unit_of_work()

    command_result = AssignOrderCommand.create()
    if command_result.is_failure:
        return

    handler = AssignOrderCommandHandler(
        order_repository=uow.orders,
        courier_repository=uow.couriers,
        distribution_service=OrdersDistributionServiceImpl(),
        unit_of_work=uow,
    )
    await handler.handle(command_result.get_value())
