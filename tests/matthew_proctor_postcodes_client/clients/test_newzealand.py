from matthew_proctor_postcodes_client import (
    MatthewProctorDatabaseType,
    NZLMatthewProctorPostcodesClient,
)


def test_new_zealand_client_defines_database_and_default_url() -> None:
    assert NZLMatthewProctorPostcodesClient.database_type == MatthewProctorDatabaseType.NZL
    assert NZLMatthewProctorPostcodesClient.database_filename == "newzealand_postcodes.csv"
    assert NZLMatthewProctorPostcodesClient.database_urls == (
        "https://www.matthewproctor.com/Content/postcodes/newzealand_postcodes.csv",
        "https://raw.githubusercontent.com/matthewproctor/australianpostcodes/master/newzealand_postcodes.csv",
    )
