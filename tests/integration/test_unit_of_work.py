from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

from microarch.delivery.config.container import Container
from microarch.delivery.core.domain.model.location import Location
from microarch.delivery.core.domain.model.order.order import Order
from microarch.delivery.core.domain.model.order.order_status import OrderStatus
from microarch.delivery.core.domain.model.volume import Volume

pytestmark = pytest.mark.asyncio


async def test_commit_persists_changes(engine: AsyncEngine) -> None:
    container = Container(engine)
    order = Order.must_create(
        uuid4(),
        Location.must_create(5, 5),
        Volume.must_create(2),
    )

    async with container.create_unit_of_work() as uow:
        await uow.orders.add(order)

    async with container.create_unit_of_work() as uow:
        fetched = await uow.orders.get(order.id)
        assert fetched is not None
        assert fetched.status == OrderStatus.CREATED


async def test_rollback_does_not_persist_changes(engine: AsyncEngine) -> None:
    container = Container(engine)
    order = Order.must_create(
        uuid4(),
        Location.must_create(5, 5),
        Volume.must_create(2),
    )

    with pytest.raises(RuntimeError):
        async with container.create_unit_of_work() as uow:
            await uow.orders.add(order)
            raise RuntimeError("boom")

    async with container.create_unit_of_work() as uow:
        fetched = await uow.orders.get(order.id)
        assert fetched is None


async def test_multiple_aggregates_saved_in_one_transaction(engine: AsyncEngine) -> None:
    from microarch.delivery.core.domain.model.courier.courier import Courier

    container = Container(engine)
    order = Order.must_create(
        uuid4(),
        Location.must_create(3, 3),
        Volume.must_create(2),
    )
    courier = Courier.must_create("Ivan", Location.must_create(1, 1))
    order.assign()
    courier.take_order(order.id, order.volume, order.location)

    async with container.create_unit_of_work() as uow:
        await uow.orders.add(order)
        await uow.couriers.add(courier)

    async with container.create_unit_of_work() as uow:
        fetched_order = await uow.orders.get(order.id)
        fetched_courier = await uow.couriers.get(courier.id)
        assert fetched_order is not None
        assert fetched_order.status == OrderStatus.ASSIGNED
        assert fetched_courier is not None
        assert len(fetched_courier.assignments) == 1
