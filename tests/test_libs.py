"""Tests for DDD and error-handling primitives."""

from decimal import Decimal
from uuid import UUID, uuid4

from libs.ddd.aggregate import Aggregate
from libs.ddd.domain_event import DomainEvent
from libs.ddd.value_object import ValueObject
from libs.errs.error import Error
from libs.errs.general_errors import GeneralErrors
from libs.errs.guard import Guard
from libs.errs.result import Result
from libs.errs.unit_result import UnitResult


class Money(ValueObject):
    def __init__(self, amount: Decimal) -> None:
        self.amount = amount

    def equality_components(self):
        return [self.amount]


class SampleEvent(DomainEvent):
    pass


class Order(Aggregate[UUID]):
    def confirm(self) -> None:
        self.raise_domain_event(SampleEvent(self))


def test_value_object_equality_and_ordering() -> None:
    assert Money(Decimal("10.00")) == Money(Decimal("10.00"))
    assert Money(Decimal("5.00")) < Money(Decimal("10.00"))


def test_aggregate_raises_domain_events() -> None:
    order_id = uuid4()
    order = Order(order_id)
    order.confirm()
    events = order.get_domain_events()
    assert len(events) == 1
    assert isinstance(events[0], SampleEvent)


def test_result_success_and_failure() -> None:
    ok = Result.success(42)
    assert ok.is_success
    assert ok.get_value() == 42

    err = Result.failure(GeneralErrors.value_is_required("name"))
    assert err.is_failure
    assert err.get_error().code == "value.is.required"


def test_unit_result_merge() -> None:
    first = UnitResult.success()
    second = UnitResult.failure(GeneralErrors.invalid_length("items"))
    assert first.merge(second).is_failure


def test_guard_against_none_or_empty() -> None:
    assert Guard.against_none_or_empty(None, "name") is not None
    assert Guard.against_none_or_empty("value", "name") is None


def test_error_serialization_roundtrip() -> None:
    original = Error.of("code.test", "message")
    restored = Error.deserialize(original.serialize())
    assert restored == original


def test_error_deserialize_preserves_separator_in_message() -> None:
    original = Error.of("code.test", "prefix||suffix")
    restored = Error.deserialize(original.serialize())
    assert restored == original


def test_guard_against_less_than_returns_greater_than_error() -> None:
    error = Guard.against_less_than(5, 10, "amount")
    assert error is not None
    assert error.code == "value.must.be.greater.than"


def test_value_object_compare_with_none_component() -> None:
    class MaybeMoney(ValueObject):
        def __init__(self, amount: Decimal | None) -> None:
            self.amount = amount

        def equality_components(self):
            return [self.amount]

    assert MaybeMoney(None) < MaybeMoney(Decimal("1.00"))
    assert MaybeMoney(Decimal("1.00")) > MaybeMoney(None)


def test_base_entity_is_unhashable() -> None:
    order = Order(uuid4())
    assert order.__hash__ is None
