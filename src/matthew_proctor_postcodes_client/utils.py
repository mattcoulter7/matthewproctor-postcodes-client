"""Small utility helpers for postcode clients."""

from __future__ import annotations

from .exceptions import InvalidPostcodeError


def normalize_postcode(value: object) -> str:
    """Normalize an Australian or New Zealand postcode to four decimal digits."""
    if isinstance(value, bool):
        raise InvalidPostcodeError("A postcode must be one to four decimal digits.")

    text = str(value).strip()
    if not text.isdecimal() or not 1 <= len(text) <= 4:
        raise InvalidPostcodeError(f"Invalid postcode {value!r}; expected one to four decimal digits.")
    return text.zfill(4)
