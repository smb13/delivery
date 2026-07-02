from uuid import UUID, uuid4

import pytest

from libs.errs.domain_invariant_exception import DomainInvariantException
from microarch.delivery.core.domain.model.courier.assignment import AssignmentStatus
from microarch.delivery.core.domain.model.courier.courier import Courier
from microarch.delivery.core.domain.model.location import Location
from microarch.delivery.core.domain.model.volume import Volume


def test_create_returns_courier_with_max_volume() -> None:
    name = "Ivan"
    location = Location.must_create(5, 5)

    result = Courier.create(name, location)

    assert result.is_success
    courier = result.get_value()
    assert isinstance(courier.id, UUID)
    assert courier.name == name
    assert courier.location == location
    assert courier.max_volume == Volume.must_create(20)
    assert courier.assignments == []


def test_create_returns_failure_when_name_is_missing() -> None:
    location = Location.must_create(5, 5)

    result = Courier.create(None, location)  # type: ignore[arg-type]

    assert result.is_failure
    assert result.get_error().code == "value.is.required"


def test_create_returns_failure_when_name_is_empty() -> None:
    location = Location.must_create(5, 5)

    result = Courier.create("   ", location)

    assert result.is_failure
    assert result.get_error().code == "value.is.required"


def test_create_returns_failure_when_location_is_missing() -> None:
    result = Courier.create("Ivan", None)  # type: ignore[arg-type]

    assert result.is_failure
    assert result.get_error().code == "value.is.required"


def test_must_create_throws_on_invalid_arguments() -> None:
    with pytest.raises(DomainInvariantException):
        Courier.must_create("", Location.must_create(5, 5))


def test_can_take_returns_true_when_volume_fits() -> None:
    courier = Courier.must_create("Ivan", Location.must_create(1, 1))

    assert courier.can_take(Volume.must_create(20)) is True


def test_can_take_returns_false_when_volume_exceeds_capacity() -> None:
    courier = Courier.must_create("Ivan", Location.must_create(1, 1))

    assert courier.can_take(Volume.must_create(21)) is False


def test_can_take_counts_only_active_assignments() -> None:
    courier = Courier.must_create("Ivan", Location.must_create(1, 1))
    order_id = uuid4()
    courier.take_order(order_id, Volume.must_create(15), Location.must_create(2, 2))
    courier.move(Location.must_create(2, 2))
    courier.complete_assignment(order_id)

    assert courier.can_take(Volume.must_create(15)) is True


def test_take_order_adds_assignment() -> None:
    courier = Courier.must_create("Ivan", Location.must_create(1, 1))
    order_id = uuid4()
    volume = Volume.must_create(5)
    location = Location.must_create(2, 2)

    result = courier.take_order(order_id, volume, location)

    assert result.is_success
    assert len(courier.assignments) == 1
    assignment = courier.assignments[0]
    assert assignment.order_id == order_id
    assert assignment.volume == volume
    assert assignment.location == location
    assert assignment.status == AssignmentStatus.ASSIGNED


def test_take_order_fails_when_volume_exceeds_capacity() -> None:
    courier = Courier.must_create("Ivan", Location.must_create(1, 1))

    result = courier.take_order(uuid4(), Volume.must_create(21), Location.must_create(2, 2))

    assert result.is_failure
    assert result.get_error().code == "courier.capacity.exceeded"
    assert courier.assignments == []


def test_take_order_fails_when_order_id_is_missing() -> None:
    courier = Courier.must_create("Ivan", Location.must_create(1, 1))

    result = courier.take_order(UUID(int=0), Volume.must_create(5), Location.must_create(2, 2))

    assert result.is_failure
    assert result.get_error().code == "value.is.required"


def test_complete_assignment_succeeds_at_order_location() -> None:
    courier = Courier.must_create("Ivan", Location.must_create(1, 1))
    order_id = uuid4()
    courier.take_order(order_id, Volume.must_create(5), Location.must_create(2, 2))
    courier.move(Location.must_create(2, 2))

    result = courier.complete_assignment(order_id)

    assert result.is_success
    assert courier.assignments[0].status == AssignmentStatus.COMPLETED


def test_complete_assignment_succeeds_one_cell_away() -> None:
    courier = Courier.must_create("Ivan", Location.must_create(1, 1))
    order_id = uuid4()
    courier.take_order(order_id, Volume.must_create(5), Location.must_create(2, 2))
    courier.move(Location.must_create(2, 3))

    result = courier.complete_assignment(order_id)

    assert result.is_success
    assert courier.assignments[0].status == AssignmentStatus.COMPLETED


def test_complete_assignment_fails_when_too_far() -> None:
    courier = Courier.must_create("Ivan", Location.must_create(1, 1))
    order_id = uuid4()
    courier.take_order(order_id, Volume.must_create(5), Location.must_create(2, 2))

    result = courier.complete_assignment(order_id)

    assert result.is_failure
    assert result.get_error().code == "courier.is.too.far"
    assert courier.assignments[0].status == AssignmentStatus.ASSIGNED


def test_complete_assignment_fails_when_order_not_found() -> None:
    courier = Courier.must_create("Ivan", Location.must_create(1, 1))

    result = courier.complete_assignment(uuid4())

    assert result.is_failure
    assert result.get_error().code == "record.not.found"


def test_complete_assignment_fails_when_already_completed() -> None:
    courier = Courier.must_create("Ivan", Location.must_create(1, 1))
    order_id = uuid4()
    courier.take_order(order_id, Volume.must_create(5), Location.must_create(2, 2))
    courier.move(Location.must_create(2, 2))
    courier.complete_assignment(order_id)

    result = courier.complete_assignment(order_id)

    assert result.is_failure
    assert result.get_error().code == "assignment.already.completed"


def test_move_changes_location() -> None:
    courier = Courier.must_create("Ivan", Location.must_create(1, 1))
    new_location = Location.must_create(5, 5)

    result = courier.move(new_location)

    assert result.is_success
    assert courier.location == new_location


def test_move_fails_when_location_is_missing() -> None:
    courier = Courier.must_create("Ivan", Location.must_create(1, 1))

    result = courier.move(None)  # type: ignore[arg-type]

    assert result.is_failure
    assert result.get_error().code == "value.is.required"


def test_couriers_are_equal_by_id() -> None:
    courier_a = Courier.must_create("Ivan", Location.must_create(1, 1))
    courier_b = Courier(
        courier_a.id,
        "Petr",
        Location.must_create(10, 10),
        Volume.must_create(20),
        [],
    )

    assert courier_a == courier_b
