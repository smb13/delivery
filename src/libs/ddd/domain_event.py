from __future__ import annotations

from abc import ABC
from datetime import UTC, datetime
from uuid import UUID, uuid4


class DomainEvent(ABC):
    def __init__(
        self,
        source: object = "default",
        event_id: UUID | None = None,
        occurred_on_utc: datetime | None = None,
    ) -> None:
        self._source = source
        self.event_id: UUID = event_id or uuid4()
        self.occurred_on_utc: datetime = occurred_on_utc or datetime.now(UTC)

    @property
    def source(self) -> object:
        return self._source
