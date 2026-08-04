"""Typed async access to Matthew Proctor postcode datasets."""

from .clients import (
    AUSMatthewProctorPostcodesClient,
    MatthewProctorPostcodesClient,
    NZLMatthewProctorPostcodesClient,
    default_data_dir,
)
from .constants import DATA_DIR_ENV_VAR, DEFAULT_DATA_DIR
from .exceptions import (
    CountryMismatchError,
    DatasetFormatError,
    DatasetUnavailableError,
    InvalidPostcodeError,
    MatthewProctorPostcodesError,
    UnsupportedCountryError,
)
from .models import (
    AUSMatthewProctorPostcodeInfo,
    MatthewProctorDatabaseType,
    MatthewProctorPostcodeInfo,
    NZLMatthewProctorPostcodeInfo,
)
from .utils import normalize_postcode

__all__ = [
    "AUSMatthewProctorPostcodeInfo",
    "AUSMatthewProctorPostcodesClient",
    "CountryMismatchError",
    "DATA_DIR_ENV_VAR",
    "DEFAULT_DATA_DIR",
    "DatasetFormatError",
    "DatasetUnavailableError",
    "InvalidPostcodeError",
    "MatthewProctorDatabaseType",
    "MatthewProctorPostcodeInfo",
    "MatthewProctorPostcodesClient",
    "MatthewProctorPostcodesError",
    "NZLMatthewProctorPostcodeInfo",
    "NZLMatthewProctorPostcodesClient",
    "UnsupportedCountryError",
    "default_data_dir",
    "normalize_postcode",
]
