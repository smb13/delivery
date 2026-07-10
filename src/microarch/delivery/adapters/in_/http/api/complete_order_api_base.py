
from typing import Annotated, Any, ClassVar, Dict, List, Tuple  # noqa: F401
from uuid import UUID

from pydantic import Field
from sqlalchemy.ext.asyncio import AsyncSession


class BaseCompleteOrderApi:
    subclasses: ClassVar[tuple] = ()

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
