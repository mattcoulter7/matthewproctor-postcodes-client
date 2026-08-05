from matthewproctor_postcodes.exceptions import (
    DatasetDownloadError,
    DatasetFormatError,
    DatasetUnavailableError,
    InvalidPostcodeError,
    MatthewProctorPostcodesError,
    UnsupportedCountryError,
)


def test_package_exceptions_share_base_error() -> None:
    assert issubclass(InvalidPostcodeError, MatthewProctorPostcodesError)
    assert issubclass(UnsupportedCountryError, MatthewProctorPostcodesError)
    assert issubclass(DatasetUnavailableError, MatthewProctorPostcodesError)
    assert issubclass(DatasetDownloadError, MatthewProctorPostcodesError)
    assert issubclass(DatasetFormatError, MatthewProctorPostcodesError)


def test_dataset_download_error_derive_preserves_type() -> None:
    error = DatasetDownloadError("download failed", [OSError("first"), ValueError("second")])

    derived = error.derive([error.exceptions[0]])

    assert type(derived) is DatasetDownloadError
    assert derived.message == "download failed"
    assert derived.exceptions == (error.exceptions[0],)
