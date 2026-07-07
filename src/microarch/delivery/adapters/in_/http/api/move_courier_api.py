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
from microarch.delivery.adapters.in_.http.api.move_courier_api_base import BaseMoveCourierApi
from microarch.delivery.adapters.in_.http.dependencies import get_move_courier_handler, get_session
from microarch.delivery.adapters.in_.http.models.error import Error
from microarch.delivery.adapters.in_.http.models.extra_models import TokenModel  # noqa: F401
from microarch.delivery.adapters.in_.http.models.location import Location
from microarch.delivery.core.application.commands.move_courier import MoveCourierCommandHandler

router = APIRouter()

ns_pkg = microarch.delivery.adapters.in_.http
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.post(
    "/api/v1/couriers/{courierId}/move",
    responses={
        200: {"description": "Успешный ответ"},
        400: {"model": Error, "description": "Некорректные параметры запроса"},
        409: {"model": Error, "description": "Конфликт при перемещении курьера"},
        500: {"model": Error, "description": "Внутренняя ошибка сервиса"},
    },
    tags=["MoveCourier"],
    summary="Переместить курьера",
    response_model_by_alias=True,
)
async def move_courier(
    courierId: Annotated[UUID, Field(description="Идентификатор курьера")] = Path(
        ..., description="Идентификатор курьера"
    ),
    location: Annotated[Location, Field(description="Местоположение")] = Body(
        None, description="Местоположение"
    ),
    session: AsyncSession = Depends(get_session),
    handler: MoveCourierCommandHandler = Depends(get_move_courier_handler),
) -> None:
    """Позволяет переместить курьера"""
    if not BaseMoveCourierApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseMoveCourierApi.subclasses[0](handler).move_courier(
        courierId, location, session
    )
