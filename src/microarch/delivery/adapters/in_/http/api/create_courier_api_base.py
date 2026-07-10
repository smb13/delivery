
from typing import Annotated, ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field
from sqlalchemy.ext.asyncio import AsyncSession

from microarch.delivery.adapters.in_.http.models.create_courier_response import (
    CreateCourierResponse,
)
from microarch.delivery.adapters.in_.http.models.new_courier import NewCourier


class BaseCreateCourierApi:
    subclasses: ClassVar[tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseCreateCourierApi.subclasses = BaseCreateCourierApi.subclasses + (cls,)
    async def create_courier(
        self,
        new_courier: Annotated[NewCourier, Field(description="Курьер")],
        session: AsyncSession,
    ) -> CreateCourierResponse:
        """Позволяет добавить курьера"""
        ...
