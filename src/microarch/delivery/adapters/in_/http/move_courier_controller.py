from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from microarch.delivery.adapters.in_.http.api.move_courier_api_base import (
    BaseMoveCourierApi,
)
from microarch.delivery.adapters.in_.http.dependencies import bad_request, conflict
from microarch.delivery.adapters.in_.http.models.location import Location as LocationModel
from microarch.delivery.adapters.out.postgres.courier_repository import CourierRepository
from microarch.delivery.core.application.commands.move_courier import (
    MoveCourierCommand,
    MoveCourierCommandHandler,
)
from microarch.delivery.core.domain.model.location import Location as DomainLocation


class MoveCourierController(BaseMoveCourierApi):
    """Контроллер перемещения курьера."""

    async def move_courier(
        self,
        courierId: UUID,
        location: LocationModel,
        session: AsyncSession,
    ) -> None:
        domain_location = DomainLocation.must_create(location.x, location.y)
        command_result = MoveCourierCommand.create(courierId, domain_location)
        if command_result.is_failure:
            return bad_request(command_result.get_error())

        handler = MoveCourierCommandHandler(
            courier_repository=CourierRepository(session),
            session=session,
        )
        result = await handler.handle(command_result.get_value())
        if result.is_failure:
            return conflict(result.get_error())

        return None
