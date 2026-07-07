from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from libs.errs.error import Error
from libs.errs.general_errors import GeneralErrors
from libs.errs.guard import Guard
from libs.errs.result import Result
from libs.errs.unit_result import UnitResult
from microarch.delivery.core.domain.model.location import Location
from microarch.delivery.core.ports.courier_repository import ICourierRepository


@dataclass(frozen=True)
class MoveCourierCommand:
    """Команда перемещения курьера."""

    courier_id: UUID
    location: Location

    @staticmethod
    def create(
        courier_id: UUID,
        x: int,
        y: int,
    ) -> Result[MoveCourierCommand, Error]:
        err = Guard.combine(
            Guard.against_none_or_empty_uuid(courier_id, "courier_id"),
            Guard.against_none(x, "x"),
            Guard.against_none(y, "y"),
        )
        if err is not None:
            return Result.failure(err)

        location_result = Location.create(x, y)
        if location_result.is_failure:
            return Result.failure(location_result.get_error())

        return Result.success(MoveCourierCommand(courier_id, location_result.get_value()))


class MoveCourierCommandHandler:
    """Обработчик команды перемещения курьера."""

    def __init__(
        self,
        courier_repository: ICourierRepository,
        session: AsyncSession,
    ) -> None:
        self._courier_repository = courier_repository
        self._session = session

    async def handle(self, command: MoveCourierCommand) -> UnitResult[Error]:
        courier = await self._courier_repository.get(command.courier_id)
        if courier is None:
            return UnitResult.failure(
                GeneralErrors.not_found("Courier", command.courier_id),
            )

        move_result = courier.move(command.location)
        if move_result.is_failure:
            return UnitResult.failure(move_result.get_error())

        await self._courier_repository.update(courier)
        await self._session.commit()

        return UnitResult.success()
