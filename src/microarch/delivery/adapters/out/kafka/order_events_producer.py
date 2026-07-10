from __future__ import annotations

import logging

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaConnectionError, KafkaError

from libs.ddd.domain_event import DomainEvent
from microarch.delivery.adapters.out.kafka import order_events_pb2
from microarch.delivery.core.domain.model.order.events import (
    OrderAssignedDomainEvent,
    OrderCompletedDomainEvent,
)
from microarch.delivery.core.ports.domain_event_publisher import IDomainEventPublisher

logger = logging.getLogger(__name__)


class OrderEventsKafkaProducer(IDomainEventPublisher):
    """Kafka-адаптер для публикации доменных событий заказа."""

    def __init__(self, producer: AIOKafkaProducer, topic: str) -> None:
        self._producer = producer
        self._topic = topic

    async def publish(self, event: DomainEvent) -> None:
        """Отправить доменное событие заказа в Kafka.

        Args:
            event: Доменное событие заказа.
        """
        payload = self._serialize(event)
        key = self._extract_key(event)
        encoded_key = key.encode() if key else None
        try:
            await self._producer.send_and_wait(
                self._topic,
                value=payload,
                key=encoded_key,
            )
        except KafkaConnectionError:
            logger.exception("Failed to connect to Kafka")
            raise
        except KafkaError:
            logger.exception("Failed to publish order event to Kafka")
            raise

    def _serialize(self, event: DomainEvent) -> bytes:
        match event:
            case OrderAssignedDomainEvent():
                return order_events_pb2.OrderAssignedIntegrationEvent(
                    order_id=str(event.order_id),
                ).SerializeToString()
            case OrderCompletedDomainEvent():
                return order_events_pb2.OrderCompletedIntegrationEvent(
                    order_id=str(event.order_id),
                ).SerializeToString()
            case _:
                raise ValueError(f"Unsupported domain event: {type(event)}")

    def _extract_key(self, event: DomainEvent) -> str | None:
        match event:
            case OrderAssignedDomainEvent() | OrderCompletedDomainEvent():
                return str(event.order_id)
            case _:
                return None
