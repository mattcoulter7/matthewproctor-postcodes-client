"""Australian postcode client."""

from __future__ import annotations

from matthew_proctor_postcodes_client.clients.base import MatthewProctorPostcodesClient
from matthew_proctor_postcodes_client.models import MatthewProctorDatabaseType
from matthew_proctor_postcodes_client.models.australia import AUSMatthewProctorPostcodeInfo


class AUSMatthewProctorPostcodesClient(MatthewProctorPostcodesClient[AUSMatthewProctorPostcodeInfo]):
    """Client for the Australian postcode database."""

    database_type = MatthewProctorDatabaseType.AUS
    database_url = (
        "https://raw.githubusercontent.com/matthewproctor/australianpostcodes/master/australian_postcodes.csv"
    )
    postcode_field_name = "postcode"
