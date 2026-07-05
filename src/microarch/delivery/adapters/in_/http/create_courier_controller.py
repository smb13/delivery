from __future__ import annotations

from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from microarch.delivery.adapters.in_.http.api.create_courier_api_base import (
    BaseCreateCourierApi,
)
from microarch.delivery.adapters.in_.http.dependencies import bad_request, conflict
from microarch.delivery.adapters.in_.http.models.create_courier_response import (
    CreateCourierResponse,
)
from microarch.delivery.adapters.in_.http.models.new_courier import NewCourier
from microarch.delivery.adapters.out.postgres.courier_repository import CourierRepository
from microarch.delivery.core.application.commands.create_courier import (
    CreateCourierCommand,
    CreateCourierCommandHandler,
)


class CreateCourierController(BaseCreateCourierApi):
    """Контроллер создания курьера."""

    async def create_courier(
        self,
        new_courier: NewCourier,
        session: AsyncSession,
    ) -> CreateCourierResponse:
        command_result = CreateCourierCommand.create(new_courier.name)
        if command_result.is_failure:
            return bad_request(command_result.get_error())

        handler = CreateCourierCommandHandler(
            courier_repository=CourierRepository(session),
            session=session,
        )
        result = await handler.handle(command_result.get_value())
        if result.is_failure:
            return conflict(result.get_error())

        response_model = CreateCourierResponse(courier_id=result.get_value())
        return JSONResponse(
            status_code=201,
            content=response_model.model_dump(mode="json", by_alias=True),
        )
