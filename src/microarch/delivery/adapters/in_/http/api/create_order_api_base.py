# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from microarch.delivery.adapters.in_.http.models.create_order_response import CreateOrderResponse
from microarch.delivery.adapters.in_.http.models.error import Error
from microarch.delivery.adapters.in_.http.models.new_order import NewOrder


class BaseCreateOrderApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseCreateOrderApi.subclasses = BaseCreateOrderApi.subclasses + (cls,)
    async def create_order(
        self,
        new_order: Annotated[NewOrder, Field(description="Новый заказ")],
        session: AsyncSession,
    ) -> CreateOrderResponse:
        """Позволяет создать заказ с целью тестирования"""
        ...
