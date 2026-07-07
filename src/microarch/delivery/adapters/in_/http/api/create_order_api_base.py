
from typing import Annotated, ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field

from microarch.delivery.adapters.in_.http.models.create_order_response import CreateOrderResponse
from microarch.delivery.adapters.in_.http.models.new_order import NewOrder


class BaseCreateOrderApi:
    subclasses: ClassVar[tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseCreateOrderApi.subclasses = BaseCreateOrderApi.subclasses + (cls,)
    async def create_order(
        self,
        new_order: Annotated[NewOrder, Field(description="Новый заказ")],
    ) -> CreateOrderResponse:
        """Позволяет создать заказ с целью тестирования"""
        ...
