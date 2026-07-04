from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from libs.errs.error import Error
from libs.errs.guard import Guard
from libs.errs.result import Result
from microarch.delivery.core.domain.model.courier.courier import Courier
from microarch.delivery.core.domain.model.location import Location
from microarch.delivery.core.ports.courier_repository import ICourierRepository


@dataclass(frozen=True)
class CreateCourierCommand:
    """Команда создания курьера."""

    name: str

    @staticmethod
    def create(name: str) -> Result[CreateCourierCommand, Error]:
        err = Guard.combine(
            Guard.against_none_or_empty(name, "name"),
        )
        if err is not None:
            return Result.failure(err)

        return Result.success(CreateCourierCommand(name))


class CreateCourierCommandHandler:
    """Обработчик команды создания курьера."""

    def __init__(
        self,
        courier_repository: ICourierRepository,
        session: AsyncSession,
    ) -> None:
        self._courier_repository = courier_repository
        self._session = session

    async def handle(self, command: CreateCourierCommand) -> Result[UUID, Error]:
        courier_result = Courier.create(command.name, Location.must_create(1, 1))
        if courier_result.is_failure:
            return Result.failure(courier_result.get_error())

        courier = courier_result.get_value()
        await self._courier_repository.add(courier)
        await self._session.commit()

        return Result.success(courier.id)
