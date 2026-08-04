"""Typed postcode row models."""

from .australia import AUSMatthewProctorPostcodeInfo
from .database_type import MatthewProctorDatabaseType
from .newzealand import NZLMatthewProctorPostcodeInfo

type MatthewProctorPostcodeInfo = AUSMatthewProctorPostcodeInfo | NZLMatthewProctorPostcodeInfo

__all__ = [
    "AUSMatthewProctorPostcodeInfo",
    "MatthewProctorDatabaseType",
    "MatthewProctorPostcodeInfo",
    "NZLMatthewProctorPostcodeInfo",
]
