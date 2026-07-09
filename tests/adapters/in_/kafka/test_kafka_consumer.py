from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from microarch.delivery.adapters.in_.kafka import (
    BasketConfirmedIntegrationEventHandler,
    KafkaConsumer,
    basket_events_pb2,
)

pytestmark = pytest.mark.asyncio


def _build_event_bytes(basket_id: str) -> bytes:
    event = basket_events_pb2.BasketConfirmedIntegrationEvent(
        basket_id=basket_id,
        address=basket_events_pb2.Address(
            country="RU",
            city="Moscow",
            street="Tverskaya",
            house="1",
            apartment="2",
        ),
        volume=3,
    )
    return event.SerializeToString()


async def test_consumer_uses_manual_ack_and_commits_on_success() -> None:
    handler = AsyncMock(spec=BasketConfirmedIntegrationEventHandler)
    handler.handle.return_value = True
    consumer = KafkaConsumer(
        bootstrap_servers="localhost:9092",
        group_id="test-group",
        topic="basket.events",
        handler=handler,
    )

    order_id = uuid4()
    raw_event = _build_event_bytes(basket_id=str(order_id))
    message = MagicMock()
    message.value = raw_event

    with patch(
        "microarch.delivery.adapters.in_.kafka.consumer.AIOKafkaConsumer",
    ) as mock_consumer_cls:
        mock_consumer = AsyncMock()
        mock_consumer_cls.return_value = mock_consumer
        mock_consumer.__aiter__.return_value = [message]

        await consumer.start()
        await asyncio.sleep(0.01)
        await consumer.stop()

    mock_consumer_cls.assert_called_once_with(
        "basket.events",
        bootstrap_servers="localhost:9092",
        group_id="test-group",
        auto_offset_reset="earliest",
        enable_auto_commit=False,
    )
    mock_consumer.start.assert_awaited_once()
    handler.handle.assert_awaited_once_with(raw_event)
    mock_consumer.commit.assert_awaited_once()


async def test_consumer_does_not_commit_on_handler_failure() -> None:
    handler = AsyncMock(spec=BasketConfirmedIntegrationEventHandler)
    handler.handle.return_value = False
    consumer = KafkaConsumer(
        bootstrap_servers="localhost:9092",
        group_id="test-group",
        topic="basket.events",
        handler=handler,
    )

    order_id = uuid4()
    raw_event = _build_event_bytes(basket_id=str(order_id))
    message = MagicMock()
    message.value = raw_event

    with patch(
        "microarch.delivery.adapters.in_.kafka.consumer.AIOKafkaConsumer",
    ) as mock_consumer_cls:
        mock_consumer = AsyncMock()
        mock_consumer_cls.return_value = mock_consumer
        mock_consumer.__aiter__.return_value = [message]

        await consumer.start()
        await asyncio.sleep(0.01)
        await consumer.stop()

    handler.handle.assert_awaited_once_with(raw_event)
    mock_consumer.commit.assert_not_awaited()


async def test_consumer_does_not_commit_on_handler_exception() -> None:
    handler = AsyncMock(spec=BasketConfirmedIntegrationEventHandler)
    handler.handle.side_effect = RuntimeError("boom")
    consumer = KafkaConsumer(
        bootstrap_servers="localhost:9092",
        group_id="test-group",
        topic="basket.events",
        handler=handler,
    )

    order_id = uuid4()
    raw_event = _build_event_bytes(basket_id=str(order_id))
    message = MagicMock()
    message.value = raw_event

    with patch(
        "microarch.delivery.adapters.in_.kafka.consumer.AIOKafkaConsumer",
    ) as mock_consumer_cls:
        mock_consumer = AsyncMock()
        mock_consumer_cls.return_value = mock_consumer
        mock_consumer.__aiter__.return_value = [message]

        await consumer.start()
        await asyncio.sleep(0.01)
        await consumer.stop()

    handler.handle.assert_awaited_once_with(raw_event)
    mock_consumer.commit.assert_not_awaited()
