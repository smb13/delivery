# coding: utf-8

import importlib
import pkgutil
from typing import Any, Dict, List  # noqa: F401
from uuid import UUID

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
from typing_extensions import Annotated

import microarch.delivery.adapters.in_.http
from libs.ddd.domain_event_publisher import DomainEventPublisher
from microarch.delivery.adapters.in_.http.api.complete_order_api_base import BaseCompleteOrderApi
from microarch.delivery.adapters.in_.http.dependencies import (
    get_domain_event_publisher,
    get_session,
)
from microarch.delivery.adapters.in_.http.models.error import Error
from microarch.delivery.adapters.in_.http.models.extra_models import TokenModel  # noqa: F401

router = APIRouter()

ns_pkg = microarch.delivery.adapters.in_.http
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.post(
    "/api/v1/couriers/{courierId}/orders/{orderId}/complete",
    responses={
        200: {"description": "Успешный ответ"},
        400: {"model": Error, "description": "Некорректные параметры запроса"},
        409: {"model": Error, "description": "Конфликт при завершении заказа"},
        500: {"model": Error, "description": "Внутренняя ошибка сервиса"},
    },
    tags=["CompleteOrder"],
    summary="Завершить заказ",
    response_model_by_alias=True,
)
async def complete_order(
    courierId: Annotated[
        UUID,
        Field(description="Идентификатор курьера"),
    ] = Path(..., description="Идентификатор курьера"),
    orderId: Annotated[
        UUID,
        Field(description="Идентификатор заказа"),
    ] = Path(..., description="Идентификатор заказа"),
    session: AsyncSession = Depends(get_session),
    domain_event_publisher: DomainEventPublisher = Depends(
        get_domain_event_publisher,
    ),
) -> None:
    """Позволяет завершить заказ"""
    if not BaseCompleteOrderApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    controller = BaseCompleteOrderApi.subclasses[0](domain_event_publisher)
    return await controller.complete_order(courierId, orderId, session)
