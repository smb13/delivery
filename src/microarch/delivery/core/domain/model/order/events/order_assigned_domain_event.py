from __future__ import annotations

from uuid import UUID

from libs.ddd.domain_event import DomainEvent


class OrderAssignedDomainEvent(DomainEvent):
    """Доменное событие назначения заказа на курьера."""

    def __init__(self, order_id: UUID) -> None:
        super().__init__()
        self._order_id = order_id

    @property
    def order_id(self) -> UUID:
        return self._order_id
