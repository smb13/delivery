from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from microarch.delivery.adapters.in_.http.api.move_courier_api_base import (
    BaseMoveCourierApi,
)
from microarch.delivery.adapters.in_.http.dependencies import bad_request, conflict
from microarch.delivery.adapters.in_.http.models.location import Location as LocationModel
from microarch.delivery.core.application.commands.move_courier import (
    MoveCourierCommand,
    MoveCourierCommandHandler,
)


class MoveCourierController(BaseMoveCourierApi):
    """Контроллер перемещения курьера."""

    def __init__(self, handler: MoveCourierCommandHandler) -> None:
        self._handler = handler

    async def move_courier(
        self,
        courierId: UUID,
        location: LocationModel,
        session: AsyncSession,
    ) -> None:
        command_result = MoveCourierCommand.create(courierId, location.x, location.y)
        if command_result.is_failure:
            return bad_request(command_result.get_error())

        result = await self._handler.handle(command_result.get_value())
        if result.is_failure:
            return conflict(result.get_error())

        return None
