from matthewproctor_postcodes.databases import AUSMatthewProctorPostcodesDatabase
from matthewproctor_postcodes.models import MatthewProctorDatabaseType


def test_australian_database_defines_database_and_default_url() -> None:
    assert AUSMatthewProctorPostcodesDatabase.database_type == MatthewProctorDatabaseType.AUS
    assert AUSMatthewProctorPostcodesDatabase.database_filename == "australian_postcodes.csv"
    assert AUSMatthewProctorPostcodesDatabase.database_urls == (
        "https://www.matthewproctor.com/Content/postcodes/australian_postcodes.csv",
        "https://raw.githubusercontent.com/matthewproctor/australianpostcodes/master/australian_postcodes.csv",
    )
