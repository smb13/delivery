import pytest

from libs.errs.domain_invariant_exception import DomainInvariantException
from microarch.delivery.core.domain.model.volume import Volume


def test_create_returns_success_for_positive_value() -> None:
    result = Volume.create(5)
    assert result.is_success
    assert result.get_value().value == 5


def test_create_returns_failure_when_value_is_zero() -> None:
    result = Volume.create(0)
    assert result.is_failure
    assert result.get_error().code == "value.must.be.greater.or.equal"


def test_create_returns_failure_when_value_is_negative() -> None:
    result = Volume.create(-3)
    assert result.is_failure
    assert result.get_error().code == "value.must.be.greater.or.equal"


def test_must_create_throws_on_invalid_value() -> None:
    with pytest.raises(DomainInvariantException):
        Volume.must_create(0)


def test_volumes_are_equal_when_values_are_equal() -> None:
    assert Volume.must_create(7) == Volume.must_create(7)


def test_volumes_are_not_equal_when_values_differ() -> None:
    assert Volume.must_create(7) != Volume.must_create(8)


def test_volume_is_immutable() -> None:
    volume = Volume.must_create(4)
    with pytest.raises(AttributeError):
        volume.value = 10
