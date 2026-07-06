# coding: utf-8

from typing import Any, ClassVar, Dict, List, Tuple  # noqa: F401
from uuid import UUID

from pydantic import Field
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from microarch.delivery.adapters.in_.http.models.error import Error


class BaseCompleteOrderApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseCompleteOrderApi.subclasses = BaseCompleteOrderApi.subclasses + (cls,)
    async def complete_order(
        self,
        courierId: Annotated[UUID, Field(description="Идентификатор курьера")],
        orderId: Annotated[UUID, Field(description="Идентификатор заказа")],
        session: AsyncSession,
    ) -> None:
        """Позволяет завершить заказ"""
        ...
