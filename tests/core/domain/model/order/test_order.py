from uuid import UUID, uuid4

import pytest

from libs.errs.domain_invariant_exception import DomainInvariantException
from microarch.delivery.core.domain.model.location import Location
from microarch.delivery.core.domain.model.order.events import (
    OrderAssignedDomainEvent,
    OrderCompletedDomainEvent,
)
from microarch.delivery.core.domain.model.order.order import Order
from microarch.delivery.core.domain.model.order.order_status import OrderStatus
from microarch.delivery.core.domain.model.volume import Volume


def test_create_returns_order_with_created_status() -> None:
    order_id = uuid4()
    location = Location.must_create(5, 5)
    volume = Volume.must_create(3)

    result = Order.create(order_id, location, volume)

    assert result.is_success
    order = result.get_value()
    assert order.id == order_id
    assert order.location == location
    assert order.volume == volume
    assert order.status == OrderStatus.CREATED


def test_create_returns_failure_when_id_is_missing() -> None:
    location = Location.must_create(5, 5)
    volume = Volume.must_create(3)

    result = Order.create(UUID(int=0), location, volume)

    assert result.is_failure
    assert result.get_error().code == "value.is.required"


def test_create_returns_failure_when_location_is_missing() -> None:
    order_id = uuid4()
    volume = Volume.must_create(3)

    result = Order.create(order_id, None, volume)  # type: ignore[arg-type]

    assert result.is_failure
    assert result.get_error().code == "value.is.required"


def test_create_returns_failure_when_volume_is_missing() -> None:
    order_id = uuid4()
    location = Location.must_create(5, 5)

    result = Order.create(order_id, location, None)  # type: ignore[arg-type]

    assert result.is_failure
    assert result.get_error().code == "value.is.required"


def test_must_create_throws_on_invalid_arguments() -> None:
    with pytest.raises(DomainInvariantException):
        Order.must_create(UUID(int=0), Location.must_create(5, 5), Volume.must_create(3))


def test_assign_succeeds_when_order_is_created() -> None:
    order = Order.must_create(uuid4(), Location.must_create(5, 5), Volume.must_create(3))

    result = order.assign()

    assert result.is_success
    assert order.status == OrderStatus.ASSIGNED


def test_assign_raises_domain_event() -> None:
    order = Order.must_create(uuid4(), Location.must_create(5, 5), Volume.must_create(3))

    order.assign()

    events = order.get_domain_events()
    assert len(events) == 1
    assert isinstance(events[0], OrderAssignedDomainEvent)
    assert events[0].order_id == order.id


def test_assign_fails_when_order_is_already_assigned() -> None:
    order = Order.must_create(uuid4(), Location.must_create(5, 5), Volume.must_create(3))
    order.assign()

    result = order.assign()

    assert result.is_failure
    assert result.get_error().code == "order.is.not.created"


def test_assign_fails_when_order_is_completed() -> None:
    order = Order.must_create(uuid4(), Location.must_create(5, 5), Volume.must_create(3))
    order.assign()
    order.complete()

    result = order.assign()

    assert result.is_failure
    assert result.get_error().code == "order.is.not.created"


def test_complete_succeeds_when_order_is_assigned() -> None:
    order = Order.must_create(uuid4(), Location.must_create(5, 5), Volume.must_create(3))
    order.assign()

    result = order.complete()

    assert result.is_success
    assert order.status == OrderStatus.COMPLETED


def test_complete_raises_domain_event() -> None:
    order = Order.must_create(uuid4(), Location.must_create(5, 5), Volume.must_create(3))
    order.assign()
    order.clear_domain_events()

    order.complete()

    events = order.get_domain_events()
    assert len(events) == 1
    assert isinstance(events[0], OrderCompletedDomainEvent)
    assert events[0].order_id == order.id


def test_complete_fails_when_order_is_created() -> None:
    order = Order.must_create(uuid4(), Location.must_create(5, 5), Volume.must_create(3))

    result = order.complete()

    assert result.is_failure
    assert result.get_error().code == "order.is.not.assigned"


def test_complete_fails_when_order_is_already_completed() -> None:
    order = Order.must_create(uuid4(), Location.must_create(5, 5), Volume.must_create(3))
    order.assign()
    order.complete()

    result = order.complete()

    assert result.is_failure
    assert result.get_error().code == "order.is.not.assigned"


def test_orders_are_equal_by_id() -> None:
    order_id = uuid4()
    order_a = Order.must_create(order_id, Location.must_create(5, 5), Volume.must_create(3))
    order_b = Order.must_create(order_id, Location.must_create(6, 6), Volume.must_create(4))

    assert order_a == order_b
