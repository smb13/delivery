from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from microarch.delivery.core.domain.model.courier.courier import Courier


class ICourierRepository(ABC):
    """Порт для работы с агрегатом Courier.

    Описывает, что требуется домену от хранилища курьеров, не вдаваясь
    в детали реализации (Postgres, Mongo и т.п.).
    """

    @abstractmethod
    async def add(self, courier: Courier) -> None:
        """Добавить нового курьера."""
        ...

    @abstractmethod
    async def update(self, courier: Courier) -> None:
        """Обновить существующего курьера."""
        ...

    @abstractmethod
    async def get(self, courier_id: UUID) -> Courier | None:
        """Получить курьера по идентификатору."""
        ...

    @abstractmethod
    async def get_all(self) -> list[Courier]:
        """Получить всех курьеров."""
        ...
