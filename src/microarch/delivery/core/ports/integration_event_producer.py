from __future__ import annotations

from abc import ABC, abstractmethod


class IIntegrationEventProducer(ABC):
    """Порт для публикации интеграционных событий во внешнюю очередь.

    Адаптеры реализуют этот интерфейс для конкретного транспорта (Kafka, RabbitMQ и т.п.),
    оставляя домен и application-слой независимыми от инфраструктуры.
    """

    @abstractmethod
    async def produce(self, payload: bytes, key: str | None = None) -> None:
        """Опубликовать сериализованное интеграционное событие.

        Args:
            payload: Сериализованное в bytes интеграционное событие.
            key: Опциональный ключ сообщения (например, идентификатор агрегата).
        """
        ...
