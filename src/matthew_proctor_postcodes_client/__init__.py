"""Matthew Proctor postcode lookup API."""

from __future__ import annotations

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
from .lookup import lookup_postcode


__all__ = [
    "AUSMatthewProctorPostcodeInfo",
    "MatthewProctorPostcodeInfo",
    "NZLMatthewProctorPostcodeInfo",
    "lookup_postcode",
]
