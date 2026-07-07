from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from microarch.delivery.core.application.queries.get_all_couriers import (
    CourierDto,
    GetAllCouriersQuery,
    GetAllCouriersQueryHandler,
)
from microarch.delivery.core.application.queries.get_not_completed_orders import (
    GetNotCompletedOrdersQuery,
    GetNotCompletedOrdersQueryHandler,
    OrderDto,
)
from microarch.delivery.core.domain.model.courier.courier import Courier
from microarch.delivery.core.domain.model.location import Location
from microarch.delivery.core.domain.model.order.order import Order
from microarch.delivery.core.domain.model.volume import Volume
from microarch.delivery.core.ports.unit_of_work import IUnitOfWork

pytestmark = pytest.mark.asyncio


async def test_get_all_couriers_returns_all_couriers(
    uow: IUnitOfWork,
    query_session: AsyncSession,
) -> None:
    courier_1 = Courier.must_create("Ivan", Location.must_create(1, 1))
    courier_2 = Courier.must_create("Petr", Location.must_create(2, 2))

    await uow.couriers.add(courier_1)
    await uow.couriers.add(courier_2)
    await uow.commit()

    handler = GetAllCouriersQueryHandler(query_session)
    result = await handler.handle(GetAllCouriersQuery())

    assert result.is_success
    dtos = result.get_value()
    assert len(dtos) == 2
    assert {dto.id for dto in dtos} == {courier_1.id, courier_2.id}
    assert all(isinstance(dto, CourierDto) for dto in dtos)


async def test_get_all_couriers_returns_empty_list_when_no_couriers(
    query_session: AsyncSession,
) -> None:
    handler = GetAllCouriersQueryHandler(query_session)
    result = await handler.handle(GetAllCouriersQuery())

    assert result.is_success
    assert result.get_value() == []


async def test_get_not_completed_orders_returns_created_and_assigned(
    uow: IUnitOfWork,
    query_session: AsyncSession,
) -> None:
    created = Order.must_create(
        uuid4(),
        Location.must_create(1, 1),
        Volume.must_create(1),
    )
    assigned = Order.must_create(
        uuid4(),
        Location.must_create(2, 2),
        Volume.must_create(1),
    )
    assigned.assign()
    completed = Order.must_create(
        uuid4(),
        Location.must_create(3, 3),
        Volume.must_create(1),
    )
    completed.assign()
    completed.complete()

    await uow.orders.add(created)
    await uow.orders.add(assigned)
    await uow.orders.add(completed)
    await uow.commit()

    handler = GetNotCompletedOrdersQueryHandler(query_session)
    result = await handler.handle(GetNotCompletedOrdersQuery())

    assert result.is_success
    dtos = result.get_value()
    assert len(dtos) == 2
    assert {dto.id for dto in dtos} == {created.id, assigned.id}
    assert all(isinstance(dto, OrderDto) for dto in dtos)


async def test_get_not_completed_orders_returns_empty_list_when_all_completed(
    uow: IUnitOfWork,
    query_session: AsyncSession,
) -> None:
    completed = Order.must_create(
        uuid4(),
        Location.must_create(5, 5),
        Volume.must_create(1),
    )
    completed.assign()
    completed.complete()
    await uow.orders.add(completed)
    await uow.commit()

    handler = GetNotCompletedOrdersQueryHandler(query_session)
    result = await handler.handle(GetNotCompletedOrdersQuery())

    assert result.is_success
    assert result.get_value() == []
