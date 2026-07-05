from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from libs.errs.error import Error
from libs.errs.general_errors import GeneralErrors
from libs.errs.guard import Guard
from libs.errs.result import Result
from libs.errs.unit_result import UnitResult
from microarch.delivery.core.ports.courier_repository import ICourierRepository
from microarch.delivery.core.ports.order_repository import IOrderRepository
from microarch.delivery.core.ports.unit_of_work import IUnitOfWork


@dataclass(frozen=True)
class CompleteOrderCommand:
    """Команда завершения заказа."""

    courier_id: UUID
    order_id: UUID

    @staticmethod
    def create(
        courier_id: UUID,
        order_id: UUID,
    ) -> Result[CompleteOrderCommand, Error]:
        err = Guard.combine(
            Guard.against_none_or_empty_uuid(courier_id, "courier_id"),
            Guard.against_none_or_empty_uuid(order_id, "order_id"),
        )
        if err is not None:
            return Result.failure(err)

        return Result.success(CompleteOrderCommand(courier_id, order_id))


class CompleteOrderCommandHandler:
    """Обработчик команды завершения заказа."""

    def __init__(
        self,
        order_repository: IOrderRepository,
        courier_repository: ICourierRepository,
        unit_of_work: IUnitOfWork,
    ) -> None:
        self._order_repository = order_repository
        self._courier_repository = courier_repository
        self._unit_of_work = unit_of_work

    async def handle(self, command: CompleteOrderCommand) -> UnitResult[Error]:
        courier = await self._courier_repository.get(command.courier_id)
        if courier is None:
            return UnitResult.failure(
                GeneralErrors.not_found("Courier", command.courier_id),
            )

        order = await self._order_repository.get(command.order_id)
        if order is None:
            return UnitResult.failure(
                GeneralErrors.not_found("Order", command.order_id),
            )

        complete_assignment_result = courier.complete_assignment(order.id)
        if complete_assignment_result.is_failure:
            return UnitResult.failure(complete_assignment_result.get_error())

        complete_order_result = order.complete()
        if complete_order_result.is_failure:
            return UnitResult.failure(complete_order_result.get_error())

        async with self._unit_of_work as uow:
            await uow.couriers.update(courier)
            await uow.orders.update(order)

        return UnitResult.success()
