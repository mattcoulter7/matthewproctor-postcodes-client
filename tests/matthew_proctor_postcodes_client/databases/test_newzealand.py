from matthew_proctor_postcodes_client.databases import NZLMatthewProctorPostcodesDatabase
from matthew_proctor_postcodes_client.models import MatthewProctorDatabaseType


def test_new_zealand_database_defines_database_and_default_url() -> None:
    assert NZLMatthewProctorPostcodesDatabase.database_type == MatthewProctorDatabaseType.NZL
    assert NZLMatthewProctorPostcodesDatabase.database_filename == "newzealand_postcodes.csv"
    assert NZLMatthewProctorPostcodesDatabase.database_urls == (
        "https://www.matthewproctor.com/Content/postcodes/newzealand_postcodes.csv",
        "https://raw.githubusercontent.com/matthewproctor/australianpostcodes/master/newzealand_postcodes.csv",
    )
