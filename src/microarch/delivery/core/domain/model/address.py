from __future__ import annotations

from libs.ddd.value_object import ValueObject
from libs.errs.error import Error
from libs.errs.guard import Guard
from libs.errs.result import Result


class Address(ValueObject):
    """Адрес доставки заказа.

      * Все компоненты адреса обязательны для заполнения.
      * Объект неизменяем после создания.
      * Два Address равны, если равны их компоненты.
    """

    __slots__ = ("_country", "_city", "_street", "_house", "_apartment")

    def __init__(
        self,
        country: str,
        city: str,
        street: str,
        house: str,
        apartment: str,
    ) -> None:
        self._country = country
        self._city = city
        self._street = street
        self._house = house
        self._apartment = apartment

    @property
    def country(self) -> str:
        return self._country

    @property
    def city(self) -> str:
        return self._city

    @property
    def street(self) -> str:
        return self._street

    @property
    def house(self) -> str:
        return self._house

    @property
    def apartment(self) -> str:
        return self._apartment

    @staticmethod
    def create(
        country: str,
        city: str,
        street: str,
        house: str,
        apartment: str,
    ) -> Result[Address, Error]:
        err = Guard.combine(
            Guard.against_none_or_empty(country, "country"),
            Guard.against_none_or_empty(city, "city"),
            Guard.against_none_or_empty(street, "street"),
            Guard.against_none_or_empty(house, "house"),
            Guard.against_none_or_empty(apartment, "apartment"),
        )
        if err is not None:
            return Result.failure(err)

        return Result.success(
            Address(country, city, street, house, apartment),
        )

    @staticmethod
    def must_create(
        country: str,
        city: str,
        street: str,
        house: str,
        apartment: str,
    ) -> Address:
        return Address.create(country, city, street, house, apartment).get_value_or_throw()

    def equality_components(self):
        return [
            self._country,
            self._city,
            self._street,
            self._house,
            self._apartment,
        ]
