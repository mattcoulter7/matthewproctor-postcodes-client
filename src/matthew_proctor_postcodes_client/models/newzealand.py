"""TypedDict model for ``newzealand_postcodes.csv`` rows."""

from __future__ import annotations

from typing import TypedDict

from .database_type import MatthewProctorDatabaseType


class NZLMatthewProctorPostcodeInfo(TypedDict, total=False):
    """One row from Matthew Proctor's New Zealand postcode CSV."""

    # Database-injected source discriminator.
    database: MatthewProctorDatabaseType

    # Postcode in four-digit numerical format, including leading zeroes.
    postcode: str
    # Locality name, typically a city, suburb, or postal distribution centre.
    locality: str
    # Region or state in which the postcode resides.
    region: str
    # Longitude from the source CSV.
    long: str | None
    # Latitude from the source CSV.
    lat: str | None
    # Territorial authority name.
    territory: str
    # Island containing the postcode.
    island: str
