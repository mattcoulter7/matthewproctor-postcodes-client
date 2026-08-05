"""TypedDict model for ``australian_postcodes.csv`` rows."""

from __future__ import annotations

from typing import TypedDict

from .database_type import MatthewProctorDatabaseType


class AUSMatthewProctorPostcodeInfo(TypedDict, total=False):
    """One row from Matthew Proctor's Australian postcode CSV."""

    # Database-injected source discriminator.
    database: MatthewProctorDatabaseType

    # Primary key from source database.
    id: str | None
    # Postcode in four-digit numerical format, including leading zeroes.
    postcode: str
    # Locality name, typically a city, suburb, or postal distribution centre.
    locality: str
    # Australian state or territory abbreviation.
    state: str
    # Longitude from the source CSV.
    long: str | None
    # Latitude from the source CSV.
    lat: str | None
    # Australia Post distribution centre servicing this postcode.
    dc: str | None
    # Locality type, such as Delivery Area, Post Office Boxes, or LVR.
    type: str | None
    # Source data status note.
    status: str | None
    # Statistical Area 3 code.
    sa3: str | None
    # Statistical Area 3 name.
    sa3name: str | None
    # Statistical Area 4 code.
    sa4: str | None
    # Statistical Area 4 name.
    sa4name: str | None
    # Designated regional area.
    region: str | None
    # Precise latitude from Google Maps data in the source dataset.
    Lat_precise: str | None
    # Precise longitude from Google Maps data in the source dataset.
    Long_precise: str | None
    # Statistical Area 1 2021 code.
    SA1_CODE_2021: str | None
    # Statistical Area 1 2021 name.
    SA1_NAME_2021: str | None
    # Statistical Area 2 2021 code.
    SA2_CODE_2021: str | None
    # Statistical Area 2 2021 name.
    SA2_NAME_2021: str | None
    # Statistical Area 3 2021 code.
    SA3_CODE_2021: str | None
    # Statistical Area 3 2021 name.
    SA3_NAME_2021: str | None
    # Statistical Area 4 2021 code.
    SA4_CODE_2021: str | None
    # Statistical Area 4 2021 name.
    SA4_NAME_2021: str | None
    # Remoteness Area 2011 value.
    RA_2011: str | None
    # Remoteness Area 2016 value.
    RA_2016: str | None
    # Remoteness Area 2021 value.
    RA_2021: str | None
    # Remoteness Area 2021 name.
    RA_2021_NAME: str | None
    # Modified Monash Model 2015 value.
    MMM_2015: str | None
    # Modified Monash Model 2019 value.
    MMM_2019: str | None
    # Commonwealth Electoral Division.
    ced: str | None
    # Altitude or elevation in metres.
    altitude: str | None
    # Australia Post charge zone.
    chargezone: str | None
    # Primary Health Network code.
    phn_code: str | None
    # Primary Health Network name.
    phn_name: str | None
    # Local Government Area region.
    lgaregion: str | None
    # Local Government Area code.
    lgacode: str | None
    # Federal government electorate.
    electorate: str | None
    # Federal government demographic rating.
    electoraterating: str | None
    # State electoral division code.
    sed_code: str | None
    # State electoral division name.
    sed_name: str | None
