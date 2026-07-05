# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from sqlalchemy.ext.asyncio import AsyncSession

from microarch.delivery.adapters.in_.http.models.courier import Courier
from microarch.delivery.adapters.in_.http.models.error import Error


class BaseGetCouriersApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseGetCouriersApi.subclasses = BaseGetCouriersApi.subclasses + (cls,)
    async def get_couriers(
        self,
        session: AsyncSession,
    ) -> List[Courier]:
        """Позволяет получить всех курьеров"""
        ...
