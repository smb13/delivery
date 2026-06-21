from __future__ import annotations

from collections.abc import Collection
from typing import TypeVar
from uuid import UUID

from libs.errs.error import Error
from libs.errs.general_errors import GeneralErrors
from libs.primitives import Comparable

T = TypeVar("T", bound=Comparable)

_EMPTY_UUID = UUID(int=0)


class Guard:
    @staticmethod
    def combine(*errors: Error | None) -> Error | None:
        for error in errors:
            if error is not None:
                return error
        return None

    @staticmethod
    def against_null_or_empty(value: str | None, param_name: str) -> Error | None:
        if value is None or not value.strip():
            return GeneralErrors.value_is_required(param_name)
        return None

    @staticmethod
    def against_null_or_empty_collection(
        collection: Collection[object] | None,
        param_name: str,
    ) -> Error | None:
        if collection is None or len(collection) == 0:
            return GeneralErrors.value_is_required(param_name)
        return None

    @staticmethod
    def against_null_or_empty_uuid(uuid: UUID | None, param_name: str) -> Error | None:
        if uuid is None or uuid == _EMPTY_UUID:
            return GeneralErrors.value_is_required(param_name)
        return None

    @staticmethod
    def against_greater_than(value: T | None, max_value: T, param_name: str) -> Error | None:
        if value is None or value > max_value:
            return GeneralErrors.value_must_be_less_than(param_name, value, max_value)
        return None

    @staticmethod
    def against_greater_or_equal(value: T | None, max_value: T, param_name: str) -> Error | None:
        if value is None or value >= max_value:
            return GeneralErrors.value_must_be_less_or_equal(param_name, value, max_value)
        return None

    @staticmethod
    def against_less_than(value: T | None, min_value: T, param_name: str) -> Error | None:
        if value is None or value < min_value:
            return GeneralErrors.value_must_be_greater_than(param_name, value, min_value)
        return None

    @staticmethod
    def against_less_or_equal(value: T | None, min_value: T, param_name: str) -> Error | None:
        if value is None or value <= min_value:
            return GeneralErrors.value_must_be_greater_or_equal(param_name, value, min_value)
        return None

    @staticmethod
    def against_out_of_range(
        value: T | None,
        min_value: T,
        max_value: T,
        param_name: str,
    ) -> Error | None:
        if value is None or value < min_value or value > max_value:
            return GeneralErrors.value_is_out_of_range(param_name, value, min_value, max_value)
        return None
