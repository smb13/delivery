from __future__ import annotations

from abc import ABC, abstractmethod

from libs.ddd.domain_event import DomainEvent


class IDomainEventPublisher(ABC):
    """Порт для публикации доменных событий во внешнюю инфраструктуру.

    Адаптеры реализуют этот интерфейс для конкретного транспорта (Kafka, RabbitMQ и т.п.),
    оставляя домен и application-слой независимыми от инфраструктуры.
    """

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """Опубликовать доменное событие.

        Args:
            event: Доменное событие для публикации.
        """
        ...
