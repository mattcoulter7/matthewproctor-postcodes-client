from matthew_proctor_postcodes_client import (
    AUSMatthewProctorPostcodesClient,
    MatthewProctorDatabaseType,
)


def test_australian_client_defines_database_and_default_url() -> None:
    assert AUSMatthewProctorPostcodesClient.database_type == MatthewProctorDatabaseType.AUS
    assert AUSMatthewProctorPostcodesClient.database_url.endswith("/australian_postcodes.csv")
