import pytest

from matthew_proctor_postcodes_client.exceptions import InvalidPostcodeError
from matthew_proctor_postcodes_client.utils import normalize_postcode


def test_normalize_postcode_preserves_leading_zero_postcode() -> None:
    assert normalize_postcode("110") == "0110"


def test_normalize_postcode_rejects_invalid_values() -> None:
    with pytest.raises(InvalidPostcodeError):
        normalize_postcode("3000-")


def test_normalize_postcode_rejects_bool() -> None:
    with pytest.raises(InvalidPostcodeError):
        normalize_postcode(True)
