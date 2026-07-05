from uuid import uuid4

import pytest

from microarch.delivery.core.domain.model.location import Location
from microarch.delivery.core.domain.model.order.order import Order
from microarch.delivery.core.domain.model.order.order_status import OrderStatus
from microarch.delivery.core.domain.model.volume import Volume
from microarch.delivery.core.ports.unit_of_work import IUnitOfWork

pytestmark = pytest.mark.asyncio


async def test_add_and_get_order(uow: IUnitOfWork) -> None:
    order_id = uuid4()
    order = Order.must_create(
        order_id,
        Location.must_create(5, 5),
        Volume.must_create(3),
    )

    await uow.orders.add(order)

    fetched = await uow.orders.get(order_id)
    assert fetched is not None
    assert fetched.id == order_id
    assert fetched.location == Location.must_create(5, 5)
    assert fetched.volume == Volume.must_create(3)
    assert fetched.status == OrderStatus.CREATED


async def test_get_order_returns_none_when_not_exists(uow: IUnitOfWork) -> None:
    fetched = await uow.orders.get(uuid4())

    assert fetched is None


async def test_update_order_status(uow: IUnitOfWork) -> None:
    order = Order.must_create(
        uuid4(),
        Location.must_create(1, 1),
        Volume.must_create(2),
    )
    await uow.orders.add(order)
    order.assign()

    await uow.orders.update(order)

    fetched = await uow.orders.get(order.id)
    assert fetched is not None
    assert fetched.status == OrderStatus.ASSIGNED


async def test_get_one_created_returns_created_order(uow: IUnitOfWork) -> None:
    created = Order.must_create(
        uuid4(),
        Location.must_create(2, 2),
        Volume.must_create(1),
    )
    assigned = Order.must_create(
        uuid4(),
        Location.must_create(3, 3),
        Volume.must_create(1),
    )
    assigned.assign()
    await uow.orders.add(created)
    await uow.orders.add(assigned)

    fetched = await uow.orders.get_one_created()

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.status == OrderStatus.CREATED


async def test_get_one_created_returns_none_when_no_created_orders(
    uow: IUnitOfWork,
) -> None:
    assigned = Order.must_create(
        uuid4(),
        Location.must_create(3, 3),
        Volume.must_create(1),
    )
    assigned.assign()
    await uow.orders.add(assigned)

    fetched = await uow.orders.get_one_created()

    assert fetched is None


async def test_get_all_assigned_returns_only_assigned_orders(uow: IUnitOfWork) -> None:
    created = Order.must_create(
        uuid4(),
        Location.must_create(1, 1),
        Volume.must_create(1),
    )
    assigned_1 = Order.must_create(
        uuid4(),
        Location.must_create(2, 2),
        Volume.must_create(1),
    )
    assigned_1.assign()
    assigned_2 = Order.must_create(
        uuid4(),
        Location.must_create(3, 3),
        Volume.must_create(1),
    )
    assigned_2.assign()
    completed = Order.must_create(
        uuid4(),
        Location.must_create(4, 4),
        Volume.must_create(1),
    )
    completed.assign()
    completed.complete()

    await uow.orders.add(created)
    await uow.orders.add(assigned_1)
    await uow.orders.add(assigned_2)
    await uow.orders.add(completed)

    fetched = await uow.orders.get_all_assigned()

    assert len(fetched) == 2
    assert {order.id for order in fetched} == {assigned_1.id, assigned_2.id}
