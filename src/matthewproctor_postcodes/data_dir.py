"""Package-level constants."""

import os
from pathlib import Path

DATA_DIR_ENV_VAR = "MATTHEWPROCTOR_POSTCODES"
DEFAULT_DATA_DIR = Path("data/matthewproctor")


def default_data_dir() -> Path:
    """Resolve the configured on-disk database directory."""
    configured = os.getenv(DATA_DIR_ENV_VAR)
    return Path(configured).expanduser() if configured else DEFAULT_DATA_DIR
