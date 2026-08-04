"""New Zealand postcode client."""

from __future__ import annotations

from matthew_proctor_postcodes_client.clients.base import MatthewProctorPostcodesClient
from matthew_proctor_postcodes_client.models import MatthewProctorDatabaseType
from matthew_proctor_postcodes_client.models.newzealand import NZLMatthewProctorPostcodeInfo


class NZLMatthewProctorPostcodesClient(MatthewProctorPostcodesClient[NZLMatthewProctorPostcodeInfo]):
    """Client for the New Zealand postcode database."""

    database_type = MatthewProctorDatabaseType.NZL
    database_url = (
        "https://raw.githubusercontent.com/matthewproctor/australianpostcodes/master/newzealand_postcodes.csv"
    )
