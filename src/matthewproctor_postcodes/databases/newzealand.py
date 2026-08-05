"""New Zealand postcode database."""

from __future__ import annotations

from matthewproctor_postcodes.databases.base import MatthewProctorPostcodesDatabase
from matthewproctor_postcodes.models import MatthewProctorDatabaseType
from matthewproctor_postcodes.models.newzealand import NZLMatthewProctorPostcodeInfo


class NZLMatthewProctorPostcodesDatabase(MatthewProctorPostcodesDatabase[NZLMatthewProctorPostcodeInfo]):
    """Database for New Zealand postcodes."""

    database_type = MatthewProctorDatabaseType.NZL
    database_filename = "newzealand_postcodes.csv"
    database_urls = (
        "https://www.matthewproctor.com/Content/postcodes/newzealand_postcodes.csv",
        "https://raw.githubusercontent.com/matthewproctor/australianpostcodes/master/newzealand_postcodes.csv",
    )
