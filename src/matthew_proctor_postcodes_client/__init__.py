"""Matthew Proctor postcode lookup API."""

from __future__ import annotations

from matthew_proctor_postcodes_client.models import (
    AUSMatthewProctorPostcodeInfo,
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
