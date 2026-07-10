from __future__ import annotations

from uuid import UUID

from libs.ddd.aggregate import Aggregate
from libs.errs.error import Error
from libs.errs.guard import Guard
from libs.errs.result import Result
from libs.errs.unit_result import UnitResult
from microarch.delivery.core.domain.model.location import Location
from microarch.delivery.core.domain.model.order.events import (
    OrderAssignedDomainEvent,
    OrderCompletedDomainEvent,
)
from microarch.delivery.core.domain.model.order.order_status import OrderStatus
from microarch.delivery.core.domain.model.volume import Volume


class Order(Aggregate[UUID]):
    """Заказ на доставку."""

    def __init__(
        self,
        id: UUID,
        location: Location,
        volume: Volume,
        status: OrderStatus,
    ) -> None:
        super().__init__(id)
        self._location = location
        self._volume = volume
        self._status = status

    @property
    def location(self) -> Location:
        return self._location

    @property
    def volume(self) -> Volume:
        return self._volume

    @property
    def status(self) -> OrderStatus:
        return self._status

    @staticmethod
    def create(
        id: UUID,
        location: Location,
        volume: Volume,
    ) -> Result[Order, Error]:
        err = Guard.combine(
            Guard.against_none_or_empty_uuid(id, "id"),
            Guard.against_none(location, "location"),
            Guard.against_none(volume, "volume"),
        )
        if err is not None:
            return Result.failure(err)

        return Result.success(Order(id, location, volume, OrderStatus.CREATED))

    @staticmethod
    def must_create(
        id: UUID,
        location: Location,
        volume: Volume,
    ) -> Order:
        return Order.create(id, location, volume).get_value_or_throw()

    def assign(self) -> UnitResult[Error]:
        if self._status != OrderStatus.CREATED:
            return UnitResult.failure(OrderErrors.order_is_not_created())

        self._status = OrderStatus.ASSIGNED
        self.raise_domain_event(OrderAssignedDomainEvent(self.id))
        return UnitResult.success()

    def complete(self) -> UnitResult[Error]:
        if self._status != OrderStatus.ASSIGNED:
            return UnitResult.failure(OrderErrors.order_is_not_assigned())

        self._status = OrderStatus.COMPLETED
        self.raise_domain_event(OrderCompletedDomainEvent(self.id))
        return UnitResult.success()


class OrderErrors:
    @staticmethod
    def order_is_not_created() -> Error:
        return Error.of(
            "order.is.not.created",
            "Order can be assigned only when it is in Created status",
        )

    @staticmethod
    def order_is_not_assigned() -> Error:
        return Error.of(
            "order.is.not.assigned",
            "Order can be completed only when it is in Assigned status",
        )
