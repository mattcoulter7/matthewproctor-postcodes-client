from pathlib import Path

from matthewproctor_postcodes.data_dir import (
    DATA_DIR_ENV_VAR,
    DEFAULT_DATA_DIR,
)


def test_constants_define_default_storage_location() -> None:
    assert DATA_DIR_ENV_VAR == "matthewproctor_DATA_DIR"
    assert DEFAULT_DATA_DIR == Path("data/matthewproctor")
