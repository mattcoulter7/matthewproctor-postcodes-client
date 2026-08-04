"""Exceptions raised by the Matthew Proctor postcodes client."""


class MatthewProctorPostcodesError(Exception):
    """Base error for the package."""


class InvalidPostcodeError(MatthewProctorPostcodesError, ValueError):
    """Raised when a postcode is not one to four decimal digits."""


class UnsupportedCountryError(MatthewProctorPostcodesError, ValueError):
    """Raised when a country cannot be mapped to an available database."""


class CountryMismatchError(MatthewProctorPostcodesError, ValueError):
    """Raised when a lookup country does not match the configured client database."""


class DatasetUnavailableError(MatthewProctorPostcodesError):
    """Raised when a database is missing and cannot or must not be downloaded."""


class DatasetFormatError(MatthewProctorPostcodesError):
    """Raised when a downloaded or baked-in database cannot be parsed."""
