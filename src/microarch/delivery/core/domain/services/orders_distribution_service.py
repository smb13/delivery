from abc import ABC, abstractmethod

from libs.errs.error import Error
from libs.errs.result import Result
from microarch.delivery.core.domain.model.courier.courier import Courier
from microarch.delivery.core.domain.model.order.order import Order


class OrdersDistributionService(ABC):
    """Доменный сервис распределения заказов на курьеров."""

    @abstractmethod
    def dispatch(
        self,
        order: Order,
        couriers: list[Courier],
    ) -> Result[Courier, Error]:
        """Назначить заказ на самого подходящего курьера.

        Args:
            order: Заказ в статусе Created.
            couriers: Список курьеров, участвующих в распределении.

        Returns:
            Result с победившим курьером или бизнес-ошибкой.
        """
        ...
