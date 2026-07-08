from __future__ import annotations

from abc import ABC, abstractmethod


class IIntegrationEventConsumer(ABC):
    """Порт для входящего потребителя интеграционных событий."""

    @abstractmethod
    async def start(self) -> None:
        """Запустить потребителя."""
        ...

    @abstractmethod
    async def stop(self) -> None:
        """Остановить потребителя."""
        ...
