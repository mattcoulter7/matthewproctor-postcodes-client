"""Matthew Proctor postcode lookup API."""

from typing import Literal, cast, overload

from matthew_proctor_postcodes_client.databases import (
    AUSMatthewProctorPostcodesDatabase,
    MatthewProctorPostcodesDatabase,
    NZLMatthewProctorPostcodesDatabase,
)
from matthew_proctor_postcodes_client.exceptions import UnsupportedCountryError
from matthew_proctor_postcodes_client.models import (
    AUSMatthewProctorPostcodeInfo,
    MatthewProctorDatabaseType,
    MatthewProctorPostcodeInfo,
    NZLMatthewProctorPostcodeInfo,
)

_DATABASES = [
    AUSMatthewProctorPostcodesDatabase(),
    NZLMatthewProctorPostcodesDatabase(),
]

_DATABASES_INDEX = {
    database.database_type: database
    for database in _DATABASES
}

def lookup_postcode(
    postcode: str,
    country: str | MatthewProctorDatabaseType,
    *,
    request_timeout_seconds: float = 30.0,
    download_if_missing: bool = True,
) -> list[MatthewProctorPostcodeInfo]:
    """Look up postcode rows within a supported alpha-3 country."""
    try:
        database_type = MatthewProctorDatabaseType(country.strip().upper())
        database = _DATABASES_INDEX[database_type]
    except (ValueError, KeyError) as error:
        raise UnsupportedCountryError(f"Unsupported postcode country {country!r}.") from error

    return database.lookup(
        postcode,
        request_timeout_seconds=request_timeout_seconds,
        download_if_missing=download_if_missing,
    )
