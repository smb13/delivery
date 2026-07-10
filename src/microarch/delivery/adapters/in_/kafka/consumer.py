from __future__ import annotations

import asyncio
import logging

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError

from microarch.delivery.adapters.in_.kafka.basket_confirmed_event_handler import (
    BasketConfirmedIntegrationEventHandler,
)
from microarch.delivery.core.ports.integration_event_consumer import (
    IIntegrationEventConsumer,
)

logger = logging.getLogger(__name__)


class KafkaConsumer(IIntegrationEventConsumer):
    """Kafka-потребитель интеграционных событий корзины."""

    def __init__(
        self,
        bootstrap_servers: str,
        group_id: str,
        topic: str,
        handler: BasketConfirmedIntegrationEventHandler,
    ) -> None:
        self._bootstrap_servers = bootstrap_servers
        self._group_id = group_id
        self._topic = topic
        self._handler = handler
        self._consumer: AIOKafkaConsumer | None = None
        self._task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        self._consumer = AIOKafkaConsumer(
            self._topic,
            bootstrap_servers=self._bootstrap_servers,
            group_id=self._group_id,
            auto_offset_reset="earliest",
            enable_auto_commit=False,
        )
        try:
            await self._consumer.start()
        except KafkaConnectionError:
            logger.exception(
                "Failed to connect to Kafka at %s",
                self._bootstrap_servers,
            )
            return

        self._task = asyncio.create_task(self._consume())
        logger.info(
            "Kafka consumer started for topic %s at %s",
            self._topic,
            self._bootstrap_servers,
        )

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        if self._consumer is not None:
            await self._consumer.stop()

        logger.info("Kafka consumer stopped")

    async def _consume(self) -> None:
        if self._consumer is None:
            return

        try:
            async for message in self._consumer:
                try:
                    success = await self._handler.handle(message.value)
                    if success:
                        await self._consumer.commit()
                except Exception:
                    logger.exception(
                        "Failed to handle Kafka message from topic %s",
                        self._topic,
                    )
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Kafka consumer loop failed")
