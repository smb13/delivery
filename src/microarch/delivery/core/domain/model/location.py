from libs.ddd.value_object import ValueObject
from libs.errs.error import Error
from libs.errs.guard import Guard
from libs.errs.result import Result


class Location(ValueObject):
    """Координата на поле: X (горизонталь) и Y (вертикаль).

      * X и Y находятся в диапазоне от 1 до 10 включительно.
      * Объект неизменяем после создания.
      * Два Location равны, если равны их X и Y.
    """

    _MIN_VALUE = 1
    _MAX_VALUE = 10

    __slots__ = ("_x", "_y")

    def __init__(self, x: int, y: int) -> None:
        self._x = x
        self._y = y

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    @staticmethod
    def create(x: int, y: int) -> Result[Location, Error]:
        err = Guard.combine(
            Guard.against_out_of_range(x, Location._MIN_VALUE, Location._MAX_VALUE, "x"),
            Guard.against_out_of_range(y, Location._MIN_VALUE, Location._MAX_VALUE, "y"),
        )
        if err is not None:
            return Result.failure(err)

        return Result.success(Location(x, y))

    @staticmethod
    def must_create(x: int, y: int) -> Location:
        return Location.create(x, y).get_value_or_throw()

    def distance_to(self, other: Location) -> int:
        return abs(self._x - other._x) + abs(self._y - other._y)

    def equality_components(self):
        return [self._x, self._y]
