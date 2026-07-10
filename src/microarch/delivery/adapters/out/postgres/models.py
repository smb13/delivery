from __future__ import annotations

from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# Импорт OutboxMessage гарантирует регистрацию модели в Base.metadata.
from microarch.delivery.adapters.out.postgres.outbox.models import OutboxMessage  # noqa: E402, F401


class OrderModel(Base):
    """ORM-модель агрегата Order."""

    __tablename__ = "orders"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    location_x: Mapped[int]
    location_y: Mapped[int]
    volume: Mapped[int]
    status: Mapped[str] = mapped_column(String(32))


class CourierModel(Base):
    """ORM-модель агрегата Courier."""

    __tablename__ = "couriers"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    location_x: Mapped[int]
    location_y: Mapped[int]
    max_volume: Mapped[int]

    assignments: Mapped[list[AssignmentModel]] = relationship(
        back_populates="courier",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class AssignmentModel(Base):
    """ORM-модель сущности Assignment, входящей в состав Courier."""

    __tablename__ = "assignments"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    courier_id: Mapped[UUID] = mapped_column(ForeignKey("couriers.id"))
    order_id: Mapped[UUID]
    volume: Mapped[int]
    location_x: Mapped[int]
    location_y: Mapped[int]
    status: Mapped[str] = mapped_column(String(32))

    courier: Mapped[CourierModel] = relationship(back_populates="assignments")
