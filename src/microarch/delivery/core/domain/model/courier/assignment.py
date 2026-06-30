from __future__ import annotations

from enum import Enum, auto
from uuid import UUID, uuid4

from libs.ddd.base_entity import BaseEntity
from libs.errs.error import Error
from libs.errs.guard import Guard
from libs.errs.result import Result
from libs.errs.unit_result import UnitResult
from microarch.delivery.core.domain.model.location import Location
from microarch.delivery.core.domain.model.volume import Volume


class AssignmentStatus(Enum):
    ASSIGNED = auto()
    COMPLETED = auto()


class Assignment(BaseEntity[UUID]):
    """Назначение заказа на курьера.

    Хранит частичную информацию о заказе и отражает задачу на доставку,
    которая закреплена за курьером.
    """

    def __init__(
        self,
        id: UUID,
        order_id: UUID,
        volume: Volume,
        location: Location,
        status: AssignmentStatus,
    ) -> None:
        super().__init__(id)
        self._order_id = order_id
        self._volume = volume
        self._location = location
        self._status = status

    @property
    def order_id(self) -> UUID:
        return self._order_id

    @property
    def volume(self) -> Volume:
        return self._volume

    @property
    def location(self) -> Location:
        return self._location

    @property
    def status(self) -> AssignmentStatus:
        return self._status

    @staticmethod
    def create(
        order_id: UUID,
        volume: Volume,
        location: Location,
    ) -> Result[Assignment, Error]:
        err = Guard.combine(
            Guard.against_none_or_empty_uuid(order_id, "order_id"),
            Guard.against_none(volume, "volume"),
            Guard.against_none(location, "location"),
        )
        if err is not None:
            return Result.failure(err)

        assignment = Assignment(
            id=uuid4(),
            order_id=order_id,
            volume=volume,
            location=location,
            status=AssignmentStatus.ASSIGNED,
        )
        return Result.success(assignment)

    @staticmethod
    def must_create(
        order_id: UUID,
        volume: Volume,
        location: Location,
    ) -> Assignment:
        return Assignment.create(order_id, volume, location).get_value_or_throw()

    def complete(self, courier_location: Location) -> UnitResult[Error]:
        if self._status == AssignmentStatus.COMPLETED:
            return UnitResult.failure(AssignmentErrors.already_completed())

        if courier_location.distance_to(self._location) != 0:
            return UnitResult.failure(AssignmentErrors.courier_is_too_far())

        self._status = AssignmentStatus.COMPLETED
        return UnitResult.success()


class AssignmentErrors:
    @staticmethod
    def already_completed() -> Error:
        return Error.of(
            "assignment.already.completed",
            "Assignment is already completed",
        )

    @staticmethod
    def courier_is_too_far() -> Error:
        return Error.of(
            "assignment.courier.is.too.far",
            "Courier must be at the order location to complete the assignment",
        )
