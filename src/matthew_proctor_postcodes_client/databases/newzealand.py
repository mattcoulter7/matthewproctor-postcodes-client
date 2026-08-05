"""New Zealand postcode database."""

from __future__ import annotations

from matthew_proctor_postcodes_client.databases.base import MatthewProctorPostcodesDatabase
from matthew_proctor_postcodes_client.models import MatthewProctorDatabaseType
from matthew_proctor_postcodes_client.models.newzealand import NZLMatthewProctorPostcodeInfo


class NZLMatthewProctorPostcodesDatabase(MatthewProctorPostcodesDatabase[NZLMatthewProctorPostcodeInfo]):
    """Database for New Zealand postcodes."""

    database_type = MatthewProctorDatabaseType.NZL
    database_filename = "newzealand_postcodes.csv"
    database_urls = (
        "https://www.matthewproctor.com/Content/postcodes/newzealand_postcodes.csv",
        "https://raw.githubusercontent.com/matthewproctor/australianpostcodes/master/newzealand_postcodes.csv",
    )
