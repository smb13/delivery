from __future__ import annotations

from dataclasses import dataclass

from libs.errs.error import Error
from libs.errs.general_errors import GeneralErrors
from libs.errs.result import Result
from libs.errs.unit_result import UnitResult
from microarch.delivery.core.domain.services.orders_distribution_service import (
    OrdersDistributionService,
)
from microarch.delivery.core.ports.courier_repository import ICourierRepository
from microarch.delivery.core.ports.order_repository import IOrderRepository
from microarch.delivery.core.ports.unit_of_work import IUnitOfWork


@dataclass(frozen=True)
class AssignOrderCommand:
    """Команда назначения заказа на курьера."""

    @staticmethod
    def create() -> Result[AssignOrderCommand, Error]:
        return Result.success(AssignOrderCommand())


class AssignOrderCommandHandler:
    """Обработчик команды назначения заказа на курьера."""

    def __init__(
        self,
        order_repository: IOrderRepository,
        courier_repository: ICourierRepository,
        distribution_service: OrdersDistributionService,
        unit_of_work: IUnitOfWork,
    ) -> None:
        self._order_repository = order_repository
        self._courier_repository = courier_repository
        self._distribution_service = distribution_service
        self._unit_of_work = unit_of_work

    async def handle(self, command: AssignOrderCommand) -> UnitResult[Error]:
        async with self._unit_of_work as uow:
            order = await self._order_repository.get_one_created()
            if order is None:
                return UnitResult.failure(
                    GeneralErrors.not_found("Order", "created"),
                )

            couriers = await self._courier_repository.get_all()

            dispatch_result = self._distribution_service.dispatch(order, couriers)
            if dispatch_result.is_failure:
                return UnitResult.failure(dispatch_result.get_error())

            courier = dispatch_result.get_value()

            await uow.orders.update(order)
            await uow.couriers.update(courier)

        return UnitResult.success()
