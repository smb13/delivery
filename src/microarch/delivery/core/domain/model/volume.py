from __future__ import annotations

from libs.ddd.value_object import ValueObject
from libs.errs.error import Error
from libs.errs.guard import Guard
from libs.errs.result import Result


class Volume(ValueObject):
    """Объем заказа.

      * Значение должно быть положительным.
      * Объект неизменяем после создания.
      * Два Volume равны, если равны их значения.
    """

    __slots__ = ("_value",)

    def __init__(self, value: int) -> None:
        self._value = value

    @property
    def value(self) -> int:
        return self._value

    @staticmethod
    def create(value: int) -> Result[Volume, Error]:
        err = Guard.against_less_or_equal(value, 0, "volume")
        if err is not None:
            return Result.failure(err)

        return Result.success(Volume(value))

    @staticmethod
    def must_create(value: int) -> Volume:
        return Volume.create(value).get_value_or_throw()

    def equality_components(self):
        return [self._value]
