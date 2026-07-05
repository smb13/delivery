from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from libs.errs.error import Error


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Возвращает асинхронную сессию БД из контекста приложения."""
    session_factory = request.app.state.session_factory
    async with session_factory() as session:
        yield session


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
