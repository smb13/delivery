from __future__ import annotations

from uuid import uuid4

import pytest

from microarch.delivery.adapters.out.postgres.outbox.mapper import OutboxMapper
from microarch.delivery.core.domain.model.location import Location
from microarch.delivery.core.domain.model.order.events import (
    OrderAssignedDomainEvent,
    OrderCompletedDomainEvent,
)
from microarch.delivery.core.domain.model.order.order import Order
from microarch.delivery.core.domain.model.volume import Volume


def test_mapper_serializes_and_deserializes_order_assigned_event() -> None:
    order_id = uuid4()
    event = OrderAssignedDomainEvent(order_id)
    order = Order.must_create(order_id, Location.must_create(5, 5), Volume.must_create(2))

    message = OutboxMapper.to_outbox_message(event, order)

    assert message.id == event.event_id
    assert message.aggregate_id == str(order_id)
    assert message.aggregate_type == "Order"
    assert "OrderAssignedDomainEvent" in message.event_type
    assert message.processed_on_utc is None

    restored = OutboxMapper.to_domain_event(message)

    assert isinstance(restored, OrderAssignedDomainEvent)
    assert restored.order_id == order_id
    assert restored.event_id == event.event_id
    assert restored.occurred_on_utc == event.occurred_on_utc


def test_mapper_serializes_and_deserializes_order_completed_event() -> None:
    order_id = uuid4()
    event = OrderCompletedDomainEvent(order_id)
    order = Order.must_create(order_id, Location.must_create(3, 3), Volume.must_create(1))

    message = OutboxMapper.to_outbox_message(event, order)
    restored = OutboxMapper.to_domain_event(message)

    assert isinstance(restored, OrderCompletedDomainEvent)
    assert restored.order_id == order_id
    assert restored.event_id == event.event_id
    assert restored.occurred_on_utc == event.occurred_on_utc


def test_mapper_raises_on_unknown_event_type() -> None:
    order = Order.must_create(uuid4(), Location.must_create(1, 1), Volume.must_create(1))
    event = OrderAssignedDomainEvent(order.id)
    message = OutboxMapper.to_outbox_message(event, order)
    message.event_type = "unknown.Event"

    with pytest.raises(ValueError, match="Invalid domain event type"):
        OutboxMapper.to_domain_event(message)


def test_mapper_raises_on_unsupported_event() -> None:
    class UnknownDomainEvent:
        def __init__(self) -> None:
            self.event_id = uuid4()
            self.occurred_on_utc = __import__("datetime").datetime.now(
                __import__("datetime").timezone.utc,
            )

    order = Order.must_create(uuid4(), Location.must_create(1, 1), Volume.must_create(1))

    with pytest.raises(ValueError, match="Unsupported domain event"):
        OutboxMapper.to_outbox_message(UnknownDomainEvent(), order)  # type: ignore[arg-type]
