import pytest

from libs.errs.domain_invariant_exception import DomainInvariantException
from microarch.delivery.core.domain.model.location import Location


def test_create_returns_success_for_valid_coordinates() -> None:
    result = Location.create(1, 10)
    assert result.is_success
    location = result.get_value()
    assert location.x == 1
    assert location.y == 10


def test_create_returns_failure_when_x_is_out_of_range() -> None:
    result = Location.create(0, 5)
    assert result.is_failure
    assert result.get_error().code == "value.is.out.of.range"


def test_create_returns_failure_when_y_is_out_of_range() -> None:
    result = Location.create(5, 11)
    assert result.is_failure
    assert result.get_error().code == "value.is.out.of.range"


def test_must_create_throws_on_invalid_coordinates() -> None:
    with pytest.raises(DomainInvariantException):
        Location.must_create(15, 5)


def test_locations_are_equal_when_coordinates_are_equal() -> None:
    assert Location.must_create(3, 4) == Location.must_create(3, 4)


def test_locations_are_not_equal_when_coordinates_differ() -> None:
    assert Location.must_create(3, 4) != Location.must_create(4, 3)


def test_location_is_immutable() -> None:
    location = Location.must_create(2, 2)
    with pytest.raises(AttributeError):
        location.x = 5


def test_distance_to_is_manhattan_distance() -> None:
    a = Location.must_create(1, 1)
    b = Location.must_create(4, 5)
    assert a.distance_to(b) == 7
    assert b.distance_to(a) == 7
