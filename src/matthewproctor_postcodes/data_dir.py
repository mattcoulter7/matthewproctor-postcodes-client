"""Package-level constants."""

import os
from pathlib import Path

DATA_DIR_ENV_VAR = "matthewproctor_DATA_DIR"
DEFAULT_DATA_DIR = Path("data/matthewproctor")


def default_data_dir() -> Path:
    """Resolve the configured on-disk database directory."""
    configured = os.getenv(DATA_DIR_ENV_VAR)
    return Path(configured).expanduser() if configured else DEFAULT_DATA_DIR
