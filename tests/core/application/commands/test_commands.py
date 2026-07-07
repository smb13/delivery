from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from libs.errs.error import Error
from libs.errs.result import Result
from microarch.delivery.core.application.commands.assign_order import (
    AssignOrderCommand,
    AssignOrderCommandHandler,
)
from microarch.delivery.core.application.commands.complete_order import (
    CompleteOrderCommand,
    CompleteOrderCommandHandler,
)
from microarch.delivery.core.application.commands.create_courier import (
    CreateCourierCommand,
    CreateCourierCommandHandler,
)
from microarch.delivery.core.application.commands.create_order import (
    CreateOrderCommand,
    CreateOrderCommandHandler,
)
from microarch.delivery.core.application.commands.move_courier import (
    MoveCourierCommand,
    MoveCourierCommandHandler,
)
from microarch.delivery.core.domain.model.address import Address
from microarch.delivery.core.domain.model.courier.assignment import AssignmentStatus
from microarch.delivery.core.domain.model.courier.courier import Courier
from microarch.delivery.core.domain.model.location import Location
from microarch.delivery.core.domain.model.order.order import Order
from microarch.delivery.core.domain.model.order.order_status import OrderStatus
from microarch.delivery.core.domain.model.volume import Volume
from microarch.delivery.core.domain.services.orders_distribution_service import (
    OrdersDistributionService,
)
from microarch.delivery.core.ports.courier_repository import ICourierRepository
from microarch.delivery.core.ports.order_repository import IOrderRepository
from microarch.delivery.core.ports.unit_of_work import IUnitOfWork

pytestmark = pytest.mark.asyncio


def _unit_of_work_mock() -> AsyncMock:
    uow = AsyncMock(spec=IUnitOfWork)
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=False)
    uow.orders = AsyncMock(spec=IOrderRepository)
    uow.couriers = AsyncMock(spec=ICourierRepository)
    return uow


async def test_create_order_handler_persists_order() -> None:
    order_repo = AsyncMock(spec=IOrderRepository)
    session = AsyncMock(spec=AsyncSession)
    handler = CreateOrderCommandHandler(order_repo, session)

    order_id = uuid4()
    command = CreateOrderCommand(
        order_id=order_id,
        address=Address.must_create("RU", "Moscow", "Tverskaya", "1", "2"),
        volume=3,
    )

    with patch(
        "microarch.delivery.core.application.commands.create_order.random.randint",
        return_value=5,
    ):
        result = await handler.handle(command)

    assert result.is_success
    assert result.get_value() == order_id

    order_repo.add.assert_awaited_once()
    added_order = order_repo.add.await_args[0][0]
    assert added_order.id == order_id
    assert added_order.volume == Volume.must_create(3)
    assert added_order.location == Location.must_create(5, 5)
    assert added_order.status == OrderStatus.CREATED

    session.commit.assert_awaited_once()


async def test_create_order_handler_returns_failure_when_volume_is_invalid() -> None:
    order_repo = AsyncMock(spec=IOrderRepository)
    session = AsyncMock(spec=AsyncSession)
    handler = CreateOrderCommandHandler(order_repo, session)

    command = CreateOrderCommand(
        order_id=uuid4(),
        address=Address.must_create("RU", "Moscow", "Tverskaya", "1", "2"),
        volume=0,
    )

    result = await handler.handle(command)

    assert result.is_failure
    assert result.get_error().code == "value.must.be.greater.or.equal"
    order_repo.add.assert_not_awaited()
    session.commit.assert_not_awaited()


async def test_create_courier_handler_persists_courier() -> None:
    courier_repo = AsyncMock(spec=ICourierRepository)
    session = AsyncMock(spec=AsyncSession)
    handler = CreateCourierCommandHandler(courier_repo, session)

    command = CreateCourierCommand.create("Ivan").get_value()

    result = await handler.handle(command)

    assert result.is_success
    courier_repo.add.assert_awaited_once()
    added_courier = courier_repo.add.await_args[0][0]
    assert added_courier.name == "Ivan"
    assert added_courier.location == Location.must_create(1, 1)
    session.commit.assert_awaited_once()


async def test_create_courier_handler_returns_failure_when_name_is_empty() -> None:
    courier_repo = AsyncMock(spec=ICourierRepository)
    session = AsyncMock(spec=AsyncSession)
    handler = CreateCourierCommandHandler(courier_repo, session)

    result = await handler.handle(CreateCourierCommand(""))

    assert result.is_failure
    assert result.get_error().code == "value.is.required"
    courier_repo.add.assert_not_awaited()
    session.commit.assert_not_awaited()


async def test_move_courier_handler_moves_and_persists_courier() -> None:
    courier_repo = AsyncMock(spec=ICourierRepository)
    session = AsyncMock(spec=AsyncSession)
    handler = MoveCourierCommandHandler(courier_repo, session)

    courier = Courier.must_create("Ivan", Location.must_create(1, 1))
    courier_repo.get.return_value = courier

    command = MoveCourierCommand.create(courier.id, 2, 2).get_value()

    result = await handler.handle(command)

    assert result.is_success
    assert courier.location == Location.must_create(2, 2)
    courier_repo.update.assert_awaited_once_with(courier)
    session.commit.assert_awaited_once()


async def test_move_courier_handler_returns_failure_when_courier_not_found() -> None:
    courier_repo = AsyncMock(spec=ICourierRepository)
    session = AsyncMock(spec=AsyncSession)
    handler = MoveCourierCommandHandler(courier_repo, session)

    courier_repo.get.return_value = None
    command = MoveCourierCommand.create(uuid4(), 2, 2).get_value()

    result = await handler.handle(command)

    assert result.is_failure
    assert result.get_error().code == "record.not.found"
    courier_repo.update.assert_not_awaited()
    session.commit.assert_not_awaited()


async def test_assign_order_handler_assigns_and_persists_changes() -> None:
    order_repo = AsyncMock(spec=IOrderRepository)
    courier_repo = AsyncMock(spec=ICourierRepository)
    distribution_service = MagicMock(spec=OrdersDistributionService)
    uow = _unit_of_work_mock()

    order = Order.must_create(
        uuid4(),
        Location.must_create(5, 5),
        Volume.must_create(2),
    )
    courier = Courier.must_create("Ivan", Location.must_create(5, 5))
    distribution_service.dispatch.return_value = Result.success(courier)

    order_repo.get_one_created.return_value = order
    courier_repo.get_all.return_value = [courier]

    handler = AssignOrderCommandHandler(
        order_repo,
        courier_repo,
        distribution_service,
        uow,
    )

    result = await handler.handle(AssignOrderCommand())

    assert result.is_success
    order_repo.get_one_created.assert_awaited_once()
    courier_repo.get_all.assert_awaited_once()
    distribution_service.dispatch.assert_called_once_with(order, [courier])

    uow.orders.update.assert_awaited_once_with(order)
    uow.couriers.update.assert_awaited_once_with(courier)


async def test_assign_order_handler_returns_failure_when_no_created_order() -> None:
    order_repo = AsyncMock(spec=IOrderRepository)
    courier_repo = AsyncMock(spec=ICourierRepository)
    distribution_service = MagicMock(spec=OrdersDistributionService)
    uow = _unit_of_work_mock()

    order_repo.get_one_created.return_value = None

    handler = AssignOrderCommandHandler(
        order_repo,
        courier_repo,
        distribution_service,
        uow,
    )

    result = await handler.handle(AssignOrderCommand())

    assert result.is_failure
    assert result.get_error().code == "record.not.found"
    courier_repo.get_all.assert_not_awaited()
    distribution_service.dispatch.assert_not_called()
    uow.orders.update.assert_not_awaited()


async def test_assign_order_handler_returns_distribution_error() -> None:
    order_repo = AsyncMock(spec=IOrderRepository)
    courier_repo = AsyncMock(spec=ICourierRepository)
    distribution_service = MagicMock(spec=OrdersDistributionService)
    uow = _unit_of_work_mock()

    order = Order.must_create(
        uuid4(),
        Location.must_create(5, 5),
        Volume.must_create(2),
    )
    order_repo.get_one_created.return_value = order
    courier_repo.get_all.return_value = []
    distribution_service.dispatch.return_value = Result.failure(
        Error.of("no.available.courier", "No available courier can take the order"),
    )

    handler = AssignOrderCommandHandler(
        order_repo,
        courier_repo,
        distribution_service,
        uow,
    )

    result = await handler.handle(AssignOrderCommand())

    assert result.is_failure
    uow.orders.update.assert_not_awaited()
    uow.couriers.update.assert_not_awaited()


async def test_complete_order_handler_completes_assignment_and_order() -> None:
    order_repo = AsyncMock(spec=IOrderRepository)
    courier_repo = AsyncMock(spec=ICourierRepository)
    uow = _unit_of_work_mock()

    order = Order.must_create(
        uuid4(),
        Location.must_create(5, 5),
        Volume.must_create(2),
    )
    order.assign()

    courier = Courier.must_create("Ivan", Location.must_create(5, 5))
    courier.take_order(order.id, order.volume, order.location)

    order_repo.get.return_value = order
    courier_repo.get.return_value = courier

    handler = CompleteOrderCommandHandler(order_repo, courier_repo, uow)
    command = CompleteOrderCommand.create(courier.id, order.id).get_value()

    result = await handler.handle(command)

    assert result.is_success
    assert order.status == OrderStatus.COMPLETED
    assert courier.assignments[0].status == AssignmentStatus.COMPLETED

    courier_repo.get.assert_awaited_once_with(courier.id)
    order_repo.get.assert_awaited_once_with(order.id)
    uow.couriers.update.assert_awaited_once_with(courier)
    uow.orders.update.assert_awaited_once_with(order)


async def test_complete_order_handler_returns_failure_when_courier_not_found() -> None:
    order_repo = AsyncMock(spec=IOrderRepository)
    courier_repo = AsyncMock(spec=ICourierRepository)
    uow = _unit_of_work_mock()

    courier_repo.get.return_value = None

    handler = CompleteOrderCommandHandler(order_repo, courier_repo, uow)
    command = CompleteOrderCommand.create(uuid4(), uuid4()).get_value()

    result = await handler.handle(command)

    assert result.is_failure
    assert result.get_error().code == "record.not.found"
    order_repo.get.assert_not_awaited()
    uow.couriers.update.assert_not_awaited()


async def test_complete_order_handler_returns_failure_when_order_not_assigned() -> None:
    order_repo = AsyncMock(spec=IOrderRepository)
    courier_repo = AsyncMock(spec=ICourierRepository)
    uow = _unit_of_work_mock()

    order = Order.must_create(
        uuid4(),
        Location.must_create(5, 5),
        Volume.must_create(2),
    )
    courier = Courier.must_create("Ivan", Location.must_create(5, 5))
    courier.take_order(order.id, order.volume, order.location)

    order_repo.get.return_value = order
    courier_repo.get.return_value = courier

    handler = CompleteOrderCommandHandler(order_repo, courier_repo, uow)
    command = CompleteOrderCommand.create(courier.id, order.id).get_value()

    result = await handler.handle(command)

    assert result.is_failure
    assert result.get_error().code == "order.is.not.assigned"
    uow.couriers.update.assert_not_awaited()
    uow.orders.update.assert_not_awaited()
