from pathlib import Path

from matthew_proctor_postcodes_client.data_dir import (
    DATA_DIR_ENV_VAR,
    DEFAULT_DATA_DIR,
)


def test_constants_define_default_storage_location() -> None:
    assert DATA_DIR_ENV_VAR == "MATTHEW_PROCTOR_DATA_DIR"
    assert DEFAULT_DATA_DIR == Path("data/matthewproctor")
