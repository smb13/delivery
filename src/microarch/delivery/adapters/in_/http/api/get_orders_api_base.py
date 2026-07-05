# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from sqlalchemy.ext.asyncio import AsyncSession

from microarch.delivery.adapters.in_.http.models.error import Error
from microarch.delivery.adapters.in_.http.models.order import Order


class BaseGetOrdersApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseGetOrdersApi.subclasses = BaseGetOrdersApi.subclasses + (cls,)
    async def get_orders(
        self,
        session: AsyncSession,
    ) -> List[Order]:
        """Позволяет получить все незавершенные заказы"""
        ...
