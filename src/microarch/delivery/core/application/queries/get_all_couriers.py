from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from libs.errs.error import Error
from libs.errs.result import Result
from microarch.delivery.adapters.out.postgres.models import CourierModel
from microarch.delivery.core.domain.model.location import Location


@dataclass(frozen=True)
class CourierDto:
    """DTO курьера для оперативного отображения на карте."""

    id: UUID
    name: str
    location: Location


class GetAllCouriersQuery:
    """Query получения всех курьеров."""

    @staticmethod
    def create() -> Result[GetAllCouriersQuery, Error]:
        return Result.success(GetAllCouriersQuery())


class GetAllCouriersQueryHandler:
    """Обработчик Query получения всех курьеров."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def handle(
        self,
        query: GetAllCouriersQuery,
    ) -> Result[list[CourierDto], Error]:
        result = await self._session.execute(
            select(
                CourierModel.id,
                CourierModel.name,
                CourierModel.location_x,
                CourierModel.location_y,
            ).order_by(CourierModel.id),
        )

        rows = result.all()
        dtos = [
            CourierDto(
                id=row.id,
                name=row.name,
                location=Location.must_create(row.location_x, row.location_y),
            )
            for row in rows
        ]

        return Result.success(dtos)
