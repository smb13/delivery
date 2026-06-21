from __future__ import annotations

from collections.abc import Callable
from typing import Generic, TypeVar

from libs.errs.domain_invariant_exception import DomainInvariantException
from libs.errs.error import Error

T = TypeVar("T")
E = TypeVar("E", bound=Error)
R = TypeVar("R")
E2 = TypeVar("E2", bound=Error)


class Result(Generic[T, E]):
    def __init__(self, value: T | None, error: E | None, is_success: bool) -> None:
        self._value = value
        self._error = error
        self._is_success = is_success

    @staticmethod
    def success(value: T) -> Result[T, E]:
        if value is None:
            raise ValueError("value must not be None")
        return Result(value, None, True)

    @staticmethod
    def success_unit() -> Result[None, E]:
        return Result(None, None, True)

    @staticmethod
    def failure(error: E) -> Result[T, E]:
        if error is None:
            raise ValueError("error must not be None")
        return Result(None, error, False)

    @property
    def is_success(self) -> bool:
        return self._is_success

    @property
    def is_failure(self) -> bool:
        return not self._is_success

    def get_value(self) -> T:
        if not self._is_success:
            raise IllegalStateError("Cannot get value from failure")
        if self._value is None:
            raise IllegalStateError("value is None")
        return self._value

    def get_error(self) -> E:
        if self._is_success:
            raise IllegalStateError("Cannot get error from success")
        if self._error is None:
            raise IllegalStateError("error is None")
        return self._error

    def map(self, mapper: Callable[[T], R]) -> Result[R, E]:
        if self._is_success:
            return Result.success(mapper(self.get_value()))
        return Result.failure(self.get_error())

    def flat_map(self, mapper: Callable[[T], Result[R, E]]) -> Result[R, E]:
        if self._is_success:
            return mapper(self.get_value())
        return Result.failure(self.get_error())

    def on_success(self, handler: Callable[[T], None]) -> Result[T, E]:
        if self._is_success:
            handler(self.get_value())
        return self

    def on_failure(self, handler: Callable[[E], None]) -> Result[T, E]:
        if self.is_failure:
            handler(self.get_error())
        return self

    def fold(
        self,
        on_success: Callable[[T], R],
        on_failure: Callable[[E], R],
    ) -> R:
        if self._is_success:
            return on_success(self.get_value())
        return on_failure(self.get_error())

    def map_error(self, mapper: Callable[[E], E2]) -> Result[T, E2]:
        if self._is_success:
            return Result.success(self.get_value())
        return Result.failure(mapper(self.get_error()))

    def get_value_or_throw(self) -> T:
        if self._is_success:
            return self.get_value()
        raise DomainInvariantException(self.get_error())

    def __repr__(self) -> str:
        if self._is_success:
            return f"Success({self._value})"
        return f"Failure({self._error})"


class IllegalStateError(Exception):
    pass
