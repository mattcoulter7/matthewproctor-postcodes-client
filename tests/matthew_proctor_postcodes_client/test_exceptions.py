from matthew_proctor_postcodes_client import (
    CountryMismatchError,
    DatasetFormatError,
    DatasetUnavailableError,
    InvalidPostcodeError,
    MatthewProctorPostcodesError,
    UnsupportedCountryError,
)


def test_package_exceptions_share_base_error() -> None:
    assert issubclass(InvalidPostcodeError, MatthewProctorPostcodesError)
    assert issubclass(UnsupportedCountryError, MatthewProctorPostcodesError)
    assert issubclass(CountryMismatchError, MatthewProctorPostcodesError)
    assert issubclass(DatasetUnavailableError, MatthewProctorPostcodesError)
    assert issubclass(DatasetFormatError, MatthewProctorPostcodesError)
