
from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from sqlalchemy.ext.asyncio import AsyncSession

from microarch.delivery.adapters.in_.http.models.courier import Courier


class BaseGetCouriersApi:
    subclasses: ClassVar[tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseGetCouriersApi.subclasses = BaseGetCouriersApi.subclasses + (cls,)
    async def get_couriers(
        self,
        session: AsyncSession,
    ) -> list[Courier]:
        """Позволяет получить всех курьеров"""
        ...
