from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from microarch.delivery.adapters.out.postgres.mappers import CourierMapper
from microarch.delivery.adapters.out.postgres.models import CourierModel
from microarch.delivery.core.domain.model.courier.courier import Courier
from microarch.delivery.core.ports.courier_repository import ICourierRepository


class CourierRepository(ICourierRepository):
    """Postgres-адаптер репозитория курьеров."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, courier: Courier) -> None:
        model = CourierMapper.to_model(courier)
        self._session.add(model)

    async def update(self, courier: Courier) -> None:
        model = CourierMapper.to_model(courier)
        await self._session.merge(model)

    async def get(self, courier_id: UUID) -> Courier | None:
        model = await self._session.get(CourierModel, courier_id)
        if model is None:
            return None
        return CourierMapper.to_domain(model)

    async def get_all(self) -> list[Courier]:
        result = await self._session.execute(
            select(CourierModel).order_by(CourierModel.id),
        )
        return [CourierMapper.to_domain(model) for model in result.scalars().all()]
