"""Australian postcode database."""

from __future__ import annotations

from matthew_proctor_postcodes_client.databases.base import MatthewProctorPostcodesDatabase
from matthew_proctor_postcodes_client.models import MatthewProctorDatabaseType
from matthew_proctor_postcodes_client.models.australia import AUSMatthewProctorPostcodeInfo


class AUSMatthewProctorPostcodesDatabase(MatthewProctorPostcodesDatabase[AUSMatthewProctorPostcodeInfo]):
    """Database for Australian postcodes."""

    database_type = MatthewProctorDatabaseType.AUS
    database_filename = "australian_postcodes.csv"
    database_urls = (
        "https://www.matthewproctor.com/Content/postcodes/australian_postcodes.csv",
        "https://raw.githubusercontent.com/matthewproctor/australianpostcodes/master/australian_postcodes.csv",
    )
