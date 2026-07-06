from uuid import uuid4

import pytest

from microarch.delivery.core.domain.model.courier.assignment import AssignmentStatus
from microarch.delivery.core.domain.model.courier.courier import Courier
from microarch.delivery.core.domain.model.location import Location
from microarch.delivery.core.domain.model.volume import Volume
from microarch.delivery.core.ports.unit_of_work import IUnitOfWork

pytestmark = pytest.mark.asyncio


async def test_add_and_get_courier(uow: IUnitOfWork) -> None:
    courier = Courier.must_create("Ivan", Location.must_create(5, 5))

    await uow.couriers.add(courier)

    fetched = await uow.couriers.get(courier.id)
    assert fetched is not None
    assert fetched.id == courier.id
    assert fetched.name == "Ivan"
    assert fetched.location == Location.must_create(5, 5)
    assert fetched.max_volume == Volume.must_create(20)
    assert fetched.assignments == []


async def test_get_courier_returns_none_when_not_exists(uow: IUnitOfWork) -> None:
    fetched = await uow.couriers.get(uuid4())

    assert fetched is None


async def test_add_courier_with_assignments(uow: IUnitOfWork) -> None:
    courier = Courier.must_create("Petr", Location.must_create(1, 1))
    order_id = uuid4()
    courier.take_order(order_id, Volume.must_create(5), Location.must_create(2, 2))

    await uow.couriers.add(courier)

    fetched = await uow.couriers.get(courier.id)
    assert fetched is not None
    assert len(fetched.assignments) == 1
    assignment = fetched.assignments[0]
    assert assignment.order_id == order_id
    assert assignment.volume == Volume.must_create(5)
    assert assignment.location == Location.must_create(2, 2)
    assert assignment.status == AssignmentStatus.ASSIGNED


async def test_update_courier_location_and_assignments(uow: IUnitOfWork) -> None:
    courier = Courier.must_create("Sidr", Location.must_create(1, 1))
    order_id = uuid4()
    courier.take_order(order_id, Volume.must_create(5), Location.must_create(2, 2))
    await uow.couriers.add(courier)

    courier.move(Location.must_create(2, 2))
    courier.complete_assignment(order_id)

    await uow.couriers.update(courier)

    fetched = await uow.couriers.get(courier.id)
    assert fetched is not None
    assert fetched.location == Location.must_create(2, 2)
    assert len(fetched.assignments) == 1
    assert fetched.assignments[0].status == AssignmentStatus.COMPLETED


async def test_get_all_couriers(uow: IUnitOfWork) -> None:
    courier_1 = Courier.must_create("Ivan", Location.must_create(1, 1))
    courier_2 = Courier.must_create("Petr", Location.must_create(2, 2))
    await uow.couriers.add(courier_1)
    await uow.couriers.add(courier_2)

    fetched = await uow.couriers.get_all()

    assert len(fetched) == 2
    assert {courier.id for courier in fetched} == {courier_1.id, courier_2.id}
