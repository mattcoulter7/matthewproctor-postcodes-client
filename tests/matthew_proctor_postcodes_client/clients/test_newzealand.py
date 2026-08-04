from matthew_proctor_postcodes_client import (
    MatthewProctorDatabaseType,
    NZLMatthewProctorPostcodesClient,
)


def test_new_zealand_client_defines_database_and_default_url() -> None:
    assert NZLMatthewProctorPostcodesClient.database_type == MatthewProctorDatabaseType.NZL
    assert NZLMatthewProctorPostcodesClient.database_url.endswith("/newzealand_postcodes.csv")
