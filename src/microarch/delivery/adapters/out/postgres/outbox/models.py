from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from microarch.delivery.adapters.out.postgres.models import Base


class OutboxMessage(Base):
    """Техническая ORM-модель таблицы outbox.

    Хранит доменные события для надёжной доставки во внешний транспорт.
    Пока processed_on_utc равно NULL, сообщение считается неотправленным.
    """

    __tablename__ = "outbox"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    event_type: Mapped[str] = mapped_column(String(255), nullable=False)
    aggregate_id: Mapped[str] = mapped_column(String(255), nullable=False)
    aggregate_type: Mapped[str] = mapped_column(String(255), nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    occurred_on_utc: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    processed_on_utc: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    def mark_as_processed(self) -> None:
        """Помечает сообщение как успешно отправленное."""
        self.processed_on_utc = datetime.now(UTC)
