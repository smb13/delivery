from __future__ import annotations

import importlib
import json
from uuid import UUID

from libs.ddd.aggregate import Aggregate
from libs.ddd.domain_event import DomainEvent
from microarch.delivery.adapters.out.postgres.outbox.models import OutboxMessage
from microarch.delivery.core.domain.model.order.events import (
    OrderAssignedDomainEvent,
    OrderCompletedDomainEvent,
)


class OutboxMapper:
    """Маппер для сериализации/десериализации доменных событий в OutboxMessage."""

    _SUPPORTED_EVENT_TYPES: tuple[type[DomainEvent], ...] = (
        OrderAssignedDomainEvent,
        OrderCompletedDomainEvent,
    )

    @staticmethod
    def to_outbox_message(event: DomainEvent, aggregate: Aggregate) -> OutboxMessage:
        """Преобразовать доменное событие в запись outbox."""
        return OutboxMessage(
            id=event.event_id,
            event_type=f"{event.__class__.__module__}.{event.__class__.__qualname__}",
            aggregate_id=str(aggregate.id),
            aggregate_type=aggregate.__class__.__name__,
            payload=OutboxMapper._serialize_payload(event),
            occurred_on_utc=event.occurred_on_utc,
            processed_on_utc=None,
        )

    @staticmethod
    def to_domain_event(outbox_message: OutboxMessage) -> DomainEvent:
        """Восстановить доменное событие из записи outbox."""
        payload = json.loads(outbox_message.payload)
        event_id = outbox_message.id
        occurred_on_utc = outbox_message.occurred_on_utc

        event_class = OutboxMapper._import_event_class(outbox_message.event_type)

        if event_class in OutboxMapper._SUPPORTED_EVENT_TYPES:
            return event_class(
                order_id=UUID(payload["order_id"]),
                event_id=event_id,
                occurred_on_utc=occurred_on_utc,
            )

        raise ValueError(f"Unsupported domain event type: {outbox_message.event_type}")

    @staticmethod
    def _serialize_payload(event: DomainEvent) -> str:
        if isinstance(event, OutboxMapper._SUPPORTED_EVENT_TYPES):
            return json.dumps({"order_id": str(event.order_id)})

        raise ValueError(f"Unsupported domain event: {type(event)}")

    @staticmethod
    def _import_event_class(event_type: str) -> type[DomainEvent]:
        try:
            module_path, class_name = event_type.rsplit(".", 1)
            module = importlib.import_module(module_path)
            event_class = getattr(module, class_name)
        except (ValueError, ModuleNotFoundError, AttributeError) as e:
            raise ValueError(f"Invalid domain event type: {event_type}") from e

        if not isinstance(event_class, type) or not issubclass(event_class, DomainEvent):
            raise ValueError(f"Invalid domain event type: {event_type}")
        return event_class
