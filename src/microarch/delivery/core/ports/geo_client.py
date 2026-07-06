from __future__ import annotations

from abc import ABC, abstractmethod

from libs.errs.error import Error
from libs.errs.result import Result
from microarch.delivery.core.domain.model.address import Address
from microarch.delivery.core.domain.model.location import Location


class IGeoClient(ABC):
    """Порт для синхронного получения геолокации по адресу из сервиса Geo."""

    @abstractmethod
    async def get_location(self, address: Address) -> Result[Location, Error]:
        """Вернуть Location для переданного Address."""
        ...
