from __future__ import annotations

from datetime import datetime
from uuid import UUID

from libs.ddd.domain_event import DomainEvent


class OrderCompletedDomainEvent(DomainEvent):
    """Доменное событие завершения заказа."""

    def __init__(
        self,
        order_id: UUID,
        event_id: UUID | None = None,
        occurred_on_utc: datetime | None = None,
    ) -> None:
        super().__init__(event_id=event_id, occurred_on_utc=occurred_on_utc)
        self._order_id = order_id

    @property
    def order_id(self) -> UUID:
        return self._order_id
