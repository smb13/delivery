from __future__ import annotations

from collections.abc import Callable
from typing import Generic, TypeVar

from libs.errs.domain_invariant_exception import DomainInvariantException
from libs.errs.error import Error
from libs.errs.result import IllegalStateError, Result

E = TypeVar("E", bound=Error)


class UnitResult(Generic[E]):
    def __init__(self, is_success: bool, error: E | None) -> None:
        self._is_success = is_success
        self._error = error

    @staticmethod
    def success() -> UnitResult[E]:
        return UnitResult(True, None)

    @staticmethod
    def failure(error: E) -> UnitResult[E]:
        if error is None:
            raise ValueError("Error must not be none on failure")
        return UnitResult(False, error)

    @property
    def is_success(self) -> bool:
        return self._is_success

    @property
    def is_failure(self) -> bool:
        return not self._is_success

    def get_error(self) -> E:
        if self._is_success:
            raise IllegalStateError("Cannot get error from success")
        assert self._error is not None
        return self._error

    def on_success(self, handler: Callable[[], None]) -> UnitResult[E]:
        if self._is_success:
            handler()
        return self

    def on_failure(self, handler: Callable[[E], None]) -> UnitResult[E]:
        if self.is_failure:
            handler(self.get_error())
        return self

    def fold(
        self,
        on_success: Callable[[], object],
        on_failure: Callable[[E], object],
    ) -> object:
        if self._is_success:
            return on_success()
        return on_failure(self.get_error())

    def merge(self, other: UnitResult[E]) -> UnitResult[E]:
        if self.is_failure:
            return self
        if other.is_failure:
            return other
        return UnitResult.success()

    @staticmethod
    def from_result(result: Result[None, E]) -> UnitResult[E]:
        if result.is_success:
            return UnitResult.success()
        return UnitResult.failure(result.get_error())

    def to_result(self) -> Result[None, E]:
        if self.is_failure:
            return Result.failure(self.get_error())
        return Result.success_unit()

    def get_or_else_throw(
        self,
        exception_mapper: Callable[[E], Exception] | None = None,
    ) -> None:
        if self._is_success:
            return
        error = self.get_error()
        if exception_mapper is not None:
            raise exception_mapper(error)
        raise DomainInvariantException(error)

    def __repr__(self) -> str:
        if self._is_success:
            return "Success"
        return f"Failure({self._error})"
