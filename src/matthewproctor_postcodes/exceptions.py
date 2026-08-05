"""Exceptions raised by Matthew Proctor postcode lookups."""

from __future__ import annotations

from collections.abc import Sequence


class MatthewProctorPostcodesError(Exception):
    """Base error for the package."""


class InvalidPostcodeError(MatthewProctorPostcodesError, ValueError):
    """Raised when a postcode is not one to four decimal digits."""


class UnsupportedCountryError(MatthewProctorPostcodesError, ValueError):
    """Raised when a country cannot be mapped to an available database."""


class DatasetUnavailableError(MatthewProctorPostcodesError):
    """Raised when a database is missing and cannot or must not be downloaded."""


class DatasetDownloadError(ExceptionGroup, MatthewProctorPostcodesError):
    """Raised when every configured dataset source fails."""

    def derive(self, exceptions: Sequence[Exception]) -> DatasetDownloadError:
        """Preserve this exception type during ``except*`` splitting."""
        return type(self)(self.message, list(exceptions))


class DatasetFormatError(MatthewProctorPostcodesError):
    """Raised when a downloaded or baked-in database cannot be parsed."""
