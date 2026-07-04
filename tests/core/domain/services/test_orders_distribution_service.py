from uuid import uuid4

from microarch.delivery.core.domain.model.courier.assignment import AssignmentStatus
from microarch.delivery.core.domain.model.courier.courier import Courier
from microarch.delivery.core.domain.model.location import Location
from microarch.delivery.core.domain.model.order.order import Order
from microarch.delivery.core.domain.model.order.order_status import OrderStatus
from microarch.delivery.core.domain.model.volume import Volume
from microarch.delivery.core.domain.services.orders_distribution_service_impl import (
    OrdersDistributionServiceImpl,
)


def test_dispatch_assigns_closest_courier() -> None:
    service = OrdersDistributionServiceImpl()
    far_courier = Courier.must_create("Far", Location.must_create(1, 1))
    close_courier = Courier.must_create("Close", Location.must_create(5, 5))
    order = Order.must_create(uuid4(), Location.must_create(5, 6), Volume.must_create(3))

    result = service.dispatch(order, [far_courier, close_courier])

    assert result.is_success
    assert result.get_value() == close_courier
    assert order.status == OrderStatus.ASSIGNED
    assert len(close_courier.assignments) == 1
    assert close_courier.assignments[0].order_id == order.id
    assert close_courier.assignments[0].status == AssignmentStatus.ASSIGNED


def test_dispatch_skips_overloaded_couriers() -> None:
    service = OrdersDistributionServiceImpl()
    overloaded_courier = Courier.must_create("Overloaded", Location.must_create(5, 5))
    overloaded_courier.take_order(uuid4(), Volume.must_create(20), Location.must_create(5, 5))
    available_courier = Courier.must_create("Available", Location.must_create(1, 1))
    order = Order.must_create(uuid4(), Location.must_create(1, 1), Volume.must_create(1))

    result = service.dispatch(order, [overloaded_courier, available_courier])

    assert result.is_success
    assert result.get_value() == available_courier


def test_dispatch_returns_error_when_all_couriers_are_overloaded() -> None:
    service = OrdersDistributionServiceImpl()
    overloaded_courier = Courier.must_create("Overloaded", Location.must_create(5, 5))
    overloaded_courier.take_order(uuid4(), Volume.must_create(20), Location.must_create(5, 5))
    order = Order.must_create(uuid4(), Location.must_create(1, 1), Volume.must_create(1))

    result = service.dispatch(order, [overloaded_courier])

    assert result.is_failure
    assert result.get_error().code == "no.available.courier"


def test_dispatch_returns_error_when_courier_list_is_empty() -> None:
    service = OrdersDistributionServiceImpl()
    order = Order.must_create(uuid4(), Location.must_create(5, 5), Volume.must_create(3))

    result = service.dispatch(order, [])

    assert result.is_failure
    assert result.get_error().code == "value.is.required"


def test_dispatch_returns_error_when_order_is_not_created() -> None:
    service = OrdersDistributionServiceImpl()
    courier = Courier.must_create("Courier", Location.must_create(5, 5))
    order = Order.must_create(uuid4(), Location.must_create(5, 5), Volume.must_create(3))
    order.assign()

    result = service.dispatch(order, [courier])

    assert result.is_failure
    assert result.get_error().code == "order.is.not.created"
    assert courier.assignments == []


def test_dispatch_returns_error_when_order_is_completed() -> None:
    service = OrdersDistributionServiceImpl()
    courier = Courier.must_create("Courier", Location.must_create(5, 5))
    order = Order.must_create(uuid4(), Location.must_create(5, 5), Volume.must_create(3))
    order.assign()
    order.complete()

    result = service.dispatch(order, [courier])

    assert result.is_failure
    assert result.get_error().code == "order.is.not.created"
    assert courier.assignments == []


def test_dispatch_picks_first_courier_when_distances_are_equal() -> None:
    service = OrdersDistributionServiceImpl()
    first = Courier.must_create("First", Location.must_create(1, 1))
    second = Courier.must_create("Second", Location.must_create(1, 1))
    order = Order.must_create(uuid4(), Location.must_create(2, 2), Volume.must_create(1))

    result = service.dispatch(order, [first, second])

    assert result.is_success
    assert result.get_value() == first
