from __future__ import annotations

from uuid import UUID

from libs.ddd.domain_event import DomainEvent
from microarch.delivery.adapters.out.kafka import order_events_pb2
from microarch.delivery.core.domain.model.order.events import (
    OrderAssignedDomainEvent,
    OrderCompletedDomainEvent,
)
from microarch.delivery.core.ports.integration_event_producer import (
    IIntegrationEventProducer,
)


class OrderDomainEventHandler:
    """Обработчик доменных событий заказа.

    Преобразует доменные события агрегата Order в интеграционные события
    и публикует их через порт IIntegrationEventProducer,
    оставаясь независимым от конкретного транспорта.
    """

    def __init__(self, producer: IIntegrationEventProducer) -> None:
        self._producer = producer

    async def handle(self, event: DomainEvent) -> None:
        """Обработать доменное событие заказа."""
        match event:
            case OrderAssignedDomainEvent():
                await self._publish_assigned(event.order_id)
            case OrderCompletedDomainEvent():
                await self._publish_completed(event.order_id)

    async def _publish_assigned(self, order_id: UUID) -> None:
        integration_event = order_events_pb2.OrderAssignedIntegrationEvent(
            order_id=str(order_id),
        )
        await self._producer.produce(
            payload=integration_event.SerializeToString(),
            key=str(order_id),
        )

    async def _publish_completed(self, order_id: UUID) -> None:
        integration_event = order_events_pb2.OrderCompletedIntegrationEvent(
            order_id=str(order_id),
        )
        await self._producer.produce(
            payload=integration_event.SerializeToString(),
            key=str(order_id),
        )
