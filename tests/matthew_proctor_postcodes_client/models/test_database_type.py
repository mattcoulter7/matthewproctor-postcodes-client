from enum import StrEnum

import pytest

from matthew_proctor_postcodes_client.models import MatthewProctorDatabaseType


def test_database_type_is_strenum() -> None:
    assert issubclass(MatthewProctorDatabaseType, StrEnum)


def test_database_type_values_are_alpha_three_codes() -> None:
    assert MatthewProctorDatabaseType.AUS == "AUS"
    assert MatthewProctorDatabaseType.NZL == "NZL"


def test_database_type_rejects_alpha_two_codes() -> None:
    with pytest.raises(ValueError):
        MatthewProctorDatabaseType("AU")
