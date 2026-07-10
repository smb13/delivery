
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
from microarch.delivery.adapters.in_.http.api.create_courier_api_base import BaseCreateCourierApi
from microarch.delivery.adapters.in_.http.dependencies import get_session
from microarch.delivery.adapters.in_.http.models.create_courier_response import (
    CreateCourierResponse,
)
from microarch.delivery.adapters.in_.http.models.error import Error
from microarch.delivery.adapters.in_.http.models.extra_models import TokenModel  # noqa: F401
from microarch.delivery.adapters.in_.http.models.new_courier import NewCourier

router = APIRouter()

ns_pkg = microarch.delivery.adapters.in_.http
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.post(
    "/api/v1/couriers",
    responses={
        201: {"model": CreateCourierResponse, "description": "Курьер успешно создан"},
        400: {"model": Error, "description": "Некорректные параметры запроса"},
        409: {"model": Error, "description": "Конфликт при создании курьера"},
        500: {"model": Error, "description": "Внутренняя ошибка сервиса"},
    },
    tags=["CreateCourier"],
    summary="Добавить курьера",
    response_model_by_alias=True,
)
async def create_courier(
    new_courier: Annotated[NewCourier, Field(description="Курьер")] = Body(None, description="Курьер"),
    session: AsyncSession = Depends(get_session),
) -> CreateCourierResponse:
    """Позволяет добавить курьера"""
    if not BaseCreateCourierApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseCreateCourierApi.subclasses[0]().create_courier(new_courier, session)
