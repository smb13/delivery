from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from microarch.delivery.adapters.in_.http.api.get_couriers_api_base import (
    BaseGetCouriersApi,
)
from microarch.delivery.adapters.in_.http.dependencies import bad_request, conflict
from microarch.delivery.adapters.in_.http.models.courier import Courier as CourierModel
from microarch.delivery.adapters.in_.http.models.location import Location as LocationModel
from microarch.delivery.core.application.queries.get_all_couriers import (
    GetAllCouriersQuery,
    GetAllCouriersQueryHandler,
)


class GetCouriersController(BaseGetCouriersApi):
    """Контроллер получения всех курьеров."""

    async def get_couriers(self, session: AsyncSession) -> list[CourierModel]:
        query_result = GetAllCouriersQuery.create()
        if query_result.is_failure:
            return bad_request(query_result.get_error())

        handler = GetAllCouriersQueryHandler(session=session)
        result = await handler.handle(query_result.get_value())
        if result.is_failure:
            return conflict(result.get_error())

        return [
            CourierModel(
                id=dto.id,
                name=dto.name,
                location=LocationModel(x=dto.location.x, y=dto.location.y),
            )
            for dto in result.get_value()
        ]
