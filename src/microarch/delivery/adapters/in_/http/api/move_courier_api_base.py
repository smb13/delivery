# coding: utf-8

from typing import Any, ClassVar, Dict, List, Tuple  # noqa: F401
from uuid import UUID

from pydantic import Field
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from microarch.delivery.adapters.in_.http.models.error import Error
from microarch.delivery.adapters.in_.http.models.location import Location


class BaseMoveCourierApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseMoveCourierApi.subclasses = BaseMoveCourierApi.subclasses + (cls,)
    async def move_courier(
        self,
        courierId: Annotated[UUID, Field(description="Идентификатор курьера")],
        location: Annotated[Location, Field(description="Местоположение")],
        session: AsyncSession,
    ) -> None:
        """Позволяет переместить курьера"""
        ...
