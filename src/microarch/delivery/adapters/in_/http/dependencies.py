from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from libs.errs.error import Error
from microarch.delivery.adapters.out.postgres.courier_repository import CourierRepository
from microarch.delivery.adapters.out.postgres.order_repository import OrderRepository
from microarch.delivery.core.application.commands.create_order import (
    CreateOrderCommandHandler,
)
from microarch.delivery.core.application.commands.move_courier import (
    MoveCourierCommandHandler,
)


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Возвращает асинхронную сессию БД из контекста приложения."""
    session_factory = request.app.state.session_factory
    async with session_factory() as session:
        yield session


def get_create_order_handler(
    session: AsyncSession = Depends(get_session),
) -> CreateOrderCommandHandler:
    """Возвращает готовый обработчик команды создания заказа."""
    return CreateOrderCommandHandler(
        order_repository=OrderRepository(session),
        session=session,
    )


def get_move_courier_handler(
    session: AsyncSession = Depends(get_session),
) -> MoveCourierCommandHandler:
    """Возвращает готовый обработчик команды перемещения курьера."""
    return MoveCourierCommandHandler(
        courier_repository=CourierRepository(session),
        session=session,
    )


def error_response(error: Error, status_code: int) -> dict[str, object]:
    """Формирует тело ошибки в формате, описанном в OpenAPI."""
    return {
        "code": status_code,
        "message": error.message,
    }


def bad_request(error: Error) -> JSONResponse:
    """Возвращает ответ 400 Bad Request с телом ошибки."""
    return JSONResponse(
        status_code=400,
        content=error_response(error, 400),
    )


def conflict(error: Error) -> JSONResponse:
    """Возвращает ответ 409 Conflict с телом ошибкой."""
    return JSONResponse(
        status_code=409,
        content=error_response(error, 409),
    )
