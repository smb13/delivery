from __future__ import annotations

from typing import TypeVar

from libs.errs.error import Error
from libs.primitives import Comparable

T = TypeVar("T", bound=Comparable)


class GeneralErrors:
    @staticmethod
    def not_found(name: str, record_id: object) -> Error:
        GeneralErrors._validate_name(name)
        return Error.of(
            "record.not.found",
            f"Record not found. Name: {name}, id: {record_id}",
        )

    @staticmethod
    def value_is_invalid(name: str, value: object) -> Error:
        GeneralErrors._validate_name(name)
        return Error.of(
            "value.is.invalid",
            f"Value '{value}' is invalid for {name}",
        )

    @staticmethod
    def value_is_required(name: str) -> Error:
        GeneralErrors._validate_name(name)
        return Error.of("value.is.required", f"Value is required for {name}")

    @staticmethod
    def invalid_length(name: str) -> Error:
        GeneralErrors._validate_name(name)
        return Error.of("invalid.string.length", f"Invalid {name} length")

    @staticmethod
    def collection_is_too_small(min_size: int, current: int) -> Error:
        return Error.of(
            "collection.is.too.small",
            f"The collection must contain {min_size} items or more. "
            f"It contains {current} items.",
        )

    @staticmethod
    def collection_is_too_large(max_size: int, current: int) -> Error:
        return Error.of(
            "collection.is.too.large",
            f"The collection must contain {max_size} items or fewer. "
            f"It contains {current} items.",
        )

    @staticmethod
    def value_is_out_of_range(name: str, value: T, min_value: T, max_value: T) -> Error:
        GeneralErrors._validate_name(name)
        message = (
            f"Value {value} for {name} is out of range. "
            f"Min value is {min_value}, max value is {max_value}."
        )
        return Error.of("value.is.out.of.range", message)

    @staticmethod
    def value_must_be_greater_than(name: str, value: T, min_value: T) -> Error:
        GeneralErrors._validate_name(name)
        return Error.of(
            "value.must.be.greater.than",
            f"The value of {name} ({value}) must be greater than {min_value}.",
        )

    @staticmethod
    def value_must_be_greater_or_equal(name: str, value: T, min_value: T) -> Error:
        GeneralErrors._validate_name(name)
        return Error.of(
            "value.must.be.greater.or.equal",
            f"The value of {name} ({value}) must be greater than or equal to {min_value}.",
        )

    @staticmethod
    def value_must_be_less_than(name: str, value: T, max_value: T) -> Error:
        GeneralErrors._validate_name(name)
        return Error.of(
            "value.must.be.less.than",
            f"The value of {name} ({value}) must be less than {max_value}.",
        )

    @staticmethod
    def value_must_be_less_or_equal(name: str, value: T, max_value: T) -> Error:
        GeneralErrors._validate_name(name)
        return Error.of(
            "value.must.be.less.or.equal",
            f"The value of {name} ({value}) must be less than or equal to {max_value}.",
        )

    @staticmethod
    def _validate_name(name: str) -> None:
        if name is None or not name.strip():
            raise ValueError("Name must not be null or empty")
