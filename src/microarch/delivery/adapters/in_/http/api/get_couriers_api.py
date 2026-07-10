
import importlib
import pkgutil
from typing import Dict, List  # noqa: F401

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
from sqlalchemy.ext.asyncio import AsyncSession

import microarch.delivery.adapters.in_.http
from microarch.delivery.adapters.in_.http.api.get_couriers_api_base import BaseGetCouriersApi
from microarch.delivery.adapters.in_.http.dependencies import get_session
from microarch.delivery.adapters.in_.http.models.courier import Courier
from microarch.delivery.adapters.in_.http.models.error import Error
from microarch.delivery.adapters.in_.http.models.extra_models import TokenModel  # noqa: F401

router = APIRouter()

ns_pkg = microarch.delivery.adapters.in_.http
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/api/v1/couriers",
    responses={
        200: {"model": list[Courier], "description": "Успешный ответ"},
        400: {"model": Error, "description": "Некорректные параметры запроса"},
        500: {"model": Error, "description": "Внутренняя ошибка сервиса"},
    },
    tags=["GetCouriers"],
    summary="Получить всех курьеров",
    response_model_by_alias=True,
)
async def get_couriers(
    session: AsyncSession = Depends(get_session),
) -> list[Courier]:
    """Позволяет получить всех курьеров"""
    if not BaseGetCouriersApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseGetCouriersApi.subclasses[0]().get_couriers(session)
