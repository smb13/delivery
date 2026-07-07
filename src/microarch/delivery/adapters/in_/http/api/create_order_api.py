
import importlib
import pkgutil
from typing import Annotated, Dict, List  # noqa: F401

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)
from pydantic import Field
from sqlalchemy.ext.asyncio import AsyncSession

import microarch.delivery.adapters.in_.http
from microarch.delivery.adapters.in_.http.api.create_order_api_base import BaseCreateOrderApi
from microarch.delivery.adapters.in_.http.dependencies import (
    get_create_order_handler,
    get_session,
)
from microarch.delivery.adapters.in_.http.models.create_order_response import CreateOrderResponse
from microarch.delivery.adapters.in_.http.models.error import Error
from microarch.delivery.adapters.in_.http.models.extra_models import TokenModel  # noqa: F401
from microarch.delivery.adapters.in_.http.models.new_order import NewOrder
from microarch.delivery.core.application.commands.create_order import CreateOrderCommandHandler

router = APIRouter()

ns_pkg = microarch.delivery.adapters.in_.http
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.post(
    "/api/v1/orders",
    responses={
        201: {"model": CreateOrderResponse, "description": "Заказ успешно создан"},
        400: {"model": Error, "description": "Некорректные параметры запроса"},
        409: {"model": Error, "description": "Конфликт при создании заказа"},
        500: {"model": Error, "description": "Внутренняя ошибка сервиса"},
    },
    tags=["CreateOrder"],
    summary="Создать заказ",
    response_model_by_alias=True,
)
async def create_order(
    new_order: Annotated[NewOrder, Field(description="Новый заказ")] = Body(
        None, description="Новый заказ"
    ),
    session: AsyncSession = Depends(get_session),
    handler: CreateOrderCommandHandler = Depends(get_create_order_handler),
) -> CreateOrderResponse:
    """Позволяет создать заказ с целью тестирования"""
    if not BaseCreateOrderApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseCreateOrderApi.subclasses[0](handler).create_order(new_order, session)
