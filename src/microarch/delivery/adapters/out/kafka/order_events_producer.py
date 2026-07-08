from __future__ import annotations

import logging

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaConnectionError, KafkaError

from microarch.delivery.core.ports.integration_event_producer import (
    IIntegrationEventProducer,
)

logger = logging.getLogger(__name__)


class OrderEventsKafkaProducer(IIntegrationEventProducer):
    """Kafka-адаптер для публикации интеграционных событий заказа."""

    def __init__(self, producer: AIOKafkaProducer, topic: str) -> None:
        self._producer = producer
        self._topic = topic

    async def produce(self, payload: bytes, key: str | None = None) -> None:
        """Отправить сериализованное событие в Kafka.

        Args:
            payload: Сериализованное в bytes интеграционное событие.
            key: Опциональный ключ сообщения (например, идентификатор заказа).
        """
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
