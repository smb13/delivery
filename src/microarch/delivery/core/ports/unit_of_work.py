from __future__ import annotations

from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self

from microarch.delivery.core.ports.courier_repository import ICourierRepository
from microarch.delivery.core.ports.order_repository import IOrderRepository


class IUnitOfWork(ABC):
    """Порт для транзакционного сохранения нескольких агрегатов.

    Предоставляет доступ к репозиториям и управляет единой транзакцией,
    в рамках которой можно атомарно сохранить изменения.
    """

    @property
    @abstractmethod
    def orders(self) -> IOrderRepository:
        """Репозиторий заказов."""
        ...

    @property
    @abstractmethod
    def couriers(self) -> ICourierRepository:
        """Репозиторий курьеров."""
        ...

    @abstractmethod
    async def commit(self) -> None:
        """Зафиксировать транзакцию."""
        ...

    @abstractmethod
    async def rollback(self) -> None:
        """Откатить транзакцию."""
        ...

    @abstractmethod
    async def __aenter__(self) -> Self:
        ...

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        ...
