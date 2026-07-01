from uuid import UUID, uuid4

import pytest

from libs.errs.domain_invariant_exception import DomainInvariantException
from microarch.delivery.core.domain.model.courier.assignment import (
    Assignment,
    AssignmentStatus,
)
from microarch.delivery.core.domain.model.location import Location
from microarch.delivery.core.domain.model.volume import Volume


def test_create_returns_assignment_with_assigned_status() -> None:
    order_id = uuid4()
    volume = Volume.must_create(3)
    location = Location.must_create(5, 5)

    result = Assignment.create(order_id, volume, location)

    assert result.is_success
    assignment = result.get_value()
    assert isinstance(assignment.id, UUID)
    assert assignment.order_id == order_id
    assert assignment.volume == volume
    assert assignment.location == location
    assert assignment.status == AssignmentStatus.ASSIGNED


def test_create_returns_failure_when_order_id_is_missing() -> None:
    volume = Volume.must_create(3)
    location = Location.must_create(5, 5)

    result = Assignment.create(UUID(int=0), volume, location)

    assert result.is_failure
    assert result.get_error().code == "value.is.required"


def test_create_returns_failure_when_volume_is_missing() -> None:
    order_id = uuid4()
    location = Location.must_create(5, 5)

    result = Assignment.create(order_id, None, location)  # type: ignore[arg-type]

    assert result.is_failure
    assert result.get_error().code == "value.is.required"


def test_create_returns_failure_when_location_is_missing() -> None:
    order_id = uuid4()
    volume = Volume.must_create(3)

    result = Assignment.create(order_id, volume, None)  # type: ignore[arg-type]

    assert result.is_failure
    assert result.get_error().code == "value.is.required"


def test_must_create_throws_on_invalid_arguments() -> None:
    with pytest.raises(DomainInvariantException):
        Assignment.must_create(UUID(int=0), Volume.must_create(3), Location.must_create(5, 5))


def test_complete_succeeds_when_courier_is_at_order_location() -> None:
    assignment = Assignment.must_create(uuid4(), Volume.must_create(2), Location.must_create(4, 4))
    courier_location = Location.must_create(4, 4)

    result = assignment.complete(courier_location)

    assert result.is_success
    assert assignment.status == AssignmentStatus.COMPLETED


def test_complete_succeeds_when_courier_is_one_cell_away() -> None:
    assignment = Assignment.must_create(uuid4(), Volume.must_create(2), Location.must_create(4, 4))
    courier_location = Location.must_create(4, 5)

    result = assignment.complete(courier_location)

    assert result.is_success
    assert assignment.status == AssignmentStatus.COMPLETED


def test_complete_fails_when_courier_is_too_far() -> None:
    assignment = Assignment.must_create(uuid4(), Volume.must_create(2), Location.must_create(4, 4))
    courier_location = Location.must_create(1, 1)

    result = assignment.complete(courier_location)

    assert result.is_failure
    assert result.get_error().code == "assignment.courier.is.too.far"
    assert assignment.status == AssignmentStatus.ASSIGNED


def test_complete_fails_when_assignment_is_already_completed() -> None:
    assignment = Assignment.must_create(uuid4(), Volume.must_create(2), Location.must_create(4, 4))
    courier_location = Location.must_create(4, 4)

    assignment.complete(courier_location)
    result = assignment.complete(courier_location)

    assert result.is_failure
    assert result.get_error().code == "assignment.already.completed"


def test_assignments_are_equal_by_id() -> None:
    order_id = uuid4()
    volume = Volume.must_create(2)
    location = Location.must_create(3, 3)

    assignment_a = Assignment.must_create(order_id, volume, location)
    assignment_b = Assignment(
        assignment_a.id, order_id, volume, location, AssignmentStatus.ASSIGNED
    )

    assert assignment_a == assignment_b
