from matthew_proctor_postcodes_client import (
    AUSMatthewProctorPostcodesClient,
    MatthewProctorDatabaseType,
)


def test_australian_client_defines_database_and_default_url() -> None:
    assert AUSMatthewProctorPostcodesClient.database_type == MatthewProctorDatabaseType.AUS
    assert AUSMatthewProctorPostcodesClient.database_filename == "australian_postcodes.csv"
    assert AUSMatthewProctorPostcodesClient.database_urls == (
        "https://www.matthewproctor.com/Content/postcodes/australian_postcodes.csv",
        "https://raw.githubusercontent.com/matthewproctor/australianpostcodes/master/australian_postcodes.csv",
    )
