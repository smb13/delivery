from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from microarch.delivery.core.domain.model.order.order import Order


class IOrderRepository(ABC):
    """Порт для работы с агрегатом Order.

    Описывает, что требуется домену от хранилища заказов, не вдаваясь
    в детали реализации (Postgres, Mongo и т.п.).
    """

    @abstractmethod
    async def add(self, order: Order) -> None:
        """Добавить новый заказ."""
        ...

    @abstractmethod
    async def update(self, order: Order) -> None:
        """Обновить существующий заказ."""
        ...

    @abstractmethod
    async def get(self, order_id: UUID) -> Order | None:
        """Получить заказ по идентификатору."""
        ...

    @abstractmethod
    async def get_one_created(self) -> Order | None:
        """Получить один любой новый заказ (в статусе Created)."""
        ...

    @abstractmethod
    async def get_all_assigned(self) -> list[Order]:
        """Получить все назначенные заказы (в статусе Assigned)."""
        ...
