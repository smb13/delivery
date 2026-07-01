from __future__ import annotations

from uuid import UUID, uuid4

from libs.ddd.aggregate import Aggregate
from libs.errs.error import Error
from libs.errs.general_errors import GeneralErrors
from libs.errs.guard import Guard
from libs.errs.result import Result
from libs.errs.unit_result import UnitResult
from microarch.delivery.core.domain.model.courier.assignment import (
    Assignment,
    AssignmentStatus,
)
from microarch.delivery.core.domain.model.location import Location
from microarch.delivery.core.domain.model.volume import Volume

_MAX_COURIER_VOLUME = 20


class Courier(Aggregate[UUID]):
    """Курьер, выполняющий доставку заказов."""

    def __init__(
        self,
        id: UUID,
        name: str,
        location: Location,
        max_volume: Volume,
        assignments: list[Assignment],
    ) -> None:
        super().__init__(id)
        self._name = name
        self._location = location
        self._max_volume = max_volume
        self._assignments = assignments

    @property
    def name(self) -> str:
        return self._name

    @property
    def location(self) -> Location:
        return self._location

    @property
    def max_volume(self) -> Volume:
        return self._max_volume

    @property
    def assignments(self) -> list[Assignment]:
        return list(self._assignments)

    @staticmethod
    def create(
        name: str,
        location: Location,
    ) -> Result[Courier, Error]:
        err = Guard.combine(
            Guard.against_none_or_empty(name, "name"),
            Guard.against_none(location, "location"),
        )
        if err is not None:
            return Result.failure(err)

        courier = Courier(
            id=uuid4(),
            name=name,
            location=location,
            max_volume=Volume.must_create(_MAX_COURIER_VOLUME),
            assignments=[],
        )
        return Result.success(courier)

    @staticmethod
    def must_create(
        name: str,
        location: Location,
    ) -> Courier:
        return Courier.create(name, location).get_value_or_throw()

    def can_take(self, order_volume: Volume) -> bool:
        active_volume = sum(
            assignment.volume.value
            for assignment in self._assignments
            if assignment.status != AssignmentStatus.COMPLETED
        )
        return active_volume + order_volume.value <= self._max_volume.value

    def take_order(
        self,
        order_id: UUID,
        volume: Volume,
        location: Location,
    ) -> UnitResult[Error]:
        err = Guard.combine(
            Guard.against_none_or_empty_uuid(order_id, "order_id"),
            Guard.against_none(volume, "volume"),
            Guard.against_none(location, "location"),
        )
        if err is not None:
            return UnitResult.failure(err)

        if not self.can_take(volume):
            return UnitResult.failure(CourierErrors.courier_capacity_exceeded())

        assignment = Assignment.must_create(order_id, volume, location)
        self._assignments.append(assignment)
        return UnitResult.success()

    def complete_assignment(
        self,
        order_id: UUID,
        courier_location: Location,
    ) -> UnitResult[Error]:
        err = Guard.combine(
            Guard.against_none_or_empty_uuid(order_id, "order_id"),
            Guard.against_none(courier_location, "courier_location"),
        )
        if err is not None:
            return UnitResult.failure(err)

        assignment = next(
            (a for a in self._assignments if a.order_id == order_id),
            None,
        )
        if assignment is None:
            return UnitResult.failure(
                GeneralErrors.not_found("Assignment", order_id),
            )

        if courier_location.distance_to(assignment.location) > 1:
            return UnitResult.failure(CourierErrors.courier_is_too_far())

        return assignment.complete(courier_location)

    def move(self, location: Location) -> UnitResult[Error]:
        err = Guard.against_none(location, "location")
        if err is not None:
            return UnitResult.failure(err)

        self._location = location
        return UnitResult.success()


class CourierErrors:
    @staticmethod
    def courier_capacity_exceeded() -> Error:
        return Error.of(
            "courier.capacity.exceeded",
            "Courier cannot take the order: total volume would exceed the maximum capacity",
        )

    @staticmethod
    def courier_is_too_far() -> Error:
        return Error.of(
            "courier.is.too.far",
            "Courier must be at most one cell away from the order location to complete it",
        )
