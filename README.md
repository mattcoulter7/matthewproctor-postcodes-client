<div align="center">

# Matthew Proctor Postcodes Client

Async, typed Python 3.12+ client for Matthew Proctor Australian and New Zealand postcode CSV datasets.

![Python](https://img.shields.io/badge/Python-3.12+-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![UV](https://img.shields.io/badge/UV-Fast-6E40C9?style=for-the-badge)
![Hatchling](https://img.shields.io/badge/Hatchling-PEP517-6E40C9?style=for-the-badge)
![Ruff](https://img.shields.io/badge/Ruff-Lint-000000?style=for-the-badge)
![Pytest](https://img.shields.io/badge/Pytest-Unit-08979C?style=for-the-badge)
![PyPI](https://img.shields.io/badge/PyPI-Publish-6E40C9?style=for-the-badge)

[![Package CI](https://github.com/mattcoulter7/matthewproctor-postcodes-client/actions/workflows/package-ci.yaml/badge.svg?branch=main)](https://github.com/mattcoulter7/matthewproctor-postcodes-client/actions/workflows/package-ci.yaml)
[![Package CD](https://github.com/mattcoulter7/matthewproctor-postcodes-client/actions/workflows/package-cd.yaml/badge.svg?branch=main)](https://github.com/mattcoulter7/matthewproctor-postcodes-client/actions/workflows/package-cd.yaml)

</div>

## Quick Start

Install the package:

```shell
pip install matthew-proctor-postcodes-client
```

Use the async clients:

```python
import asyncio

from matthew_proctor_postcodes_client import AUSMatthewProctorPostcodesClient


async def main() -> None:
    client = AUSMatthewProctorPostcodesClient()
    entries = await client.lookup("3004")

    for entry in entries:
        print(entry["locality"], entry.get("RA_2021_NAME"))


asyncio.run(main())
```

Install development dependencies:

```shell
uv sync --refresh
```

Run local checks:

```shell
make lint
make test
```

Format code:

```shell
make format
```

## Behaviour

- `AUSMatthewProctorPostcodesClient` returns `AUSMatthewProctorPostcodeInfo` rows.
- `NZLMatthewProctorPostcodesClient` returns `NZLMatthewProctorPostcodeInfo` rows.
- `lookup()` returns every locality for a postcode.
- Unknown but well-formed postcodes return an empty list.
- Postcodes are normalized to four decimal digits, so `"110"` is looked up as `"0110"`.
- Invalid postcodes raise `InvalidPostcodeError`; values must be one to four decimal digits.
- Choose the country-specific client explicitly (`AUSMatthewProctorPostcodesClient` or `NZLMatthewProctorPostcodesClient`).
- A local CSV is preferred; a missing CSV is downloaded from GitHub and saved atomically.
- The parsed postcode index is cached by `aiocache.cached(noself=True)`.
- Row models are lightweight `TypedDict` types that use the known source CSV headers.

## Installation

```bash
pip install matthew-proctor-postcodes-client
```

For local development from a checkout:

```bash
uv sync --refresh
```

## Storage

Set `MATTHEW_PROCTOR_DATA_DIR` to control where files are read and downloaded:

```bash
export MATTHEW_PROCTOR_DATA_DIR=data/matthewproctor
```

This produces:

```text
data/matthewproctor/australian_postcodes.csv
data/matthewproctor/newzealand_postcodes.csv
```

If the environment variable is absent, the default is `data/matthewproctor` relative to the
current working directory.

For an enterprise image, bake either CSV into that path and configure `download_if_missing=False`.

## Usage

```python
import asyncio

from matthew_proctor_postcodes_client import (
    AUSMatthewProctorPostcodesClient,
    NZLMatthewProctorPostcodesClient,
)


async def main() -> None:
    aus_client = AUSMatthewProctorPostcodesClient()
    nz_client = NZLMatthewProctorPostcodesClient()

    aus_entries = await aus_client.lookup("3004")
    nz_entries = await nz_client.lookup("110")

    print([entry["locality"] for entry in aus_entries])
    print([entry["locality"] for entry in nz_entries])


asyncio.run(main())
```

## Client Configuration

Concrete clients accept these keyword arguments:

- `request_timeout_seconds`: HTTP timeout used when a missing CSV must be downloaded. Defaults to `30.0`.
- `download_if_missing`: whether to download the source CSV when it is not already present locally. Defaults to `True`.

Storage is configured with `MATTHEW_PROCTOR_DATA_DIR`, not a constructor argument:

```python
import os

from matthew_proctor_postcodes_client import AUSMatthewProctorPostcodesClient

os.environ["MATTHEW_PROCTOR_DATA_DIR"] = "/app/data/matthewproctor"

client = AUSMatthewProctorPostcodesClient(
    request_timeout_seconds=10.0,
    download_if_missing=False,
)
```

Select the concrete client when the country is only known at runtime:

```python
from matthew_proctor_postcodes_client import (
    AUSMatthewProctorPostcodesClient,
    NZLMatthewProctorPostcodesClient,
)

client = {
    "AUS": AUSMatthewProctorPostcodesClient,
    "NZL": NZLMatthewProctorPostcodesClient,
}[country]()
```

The package also exports `normalize_postcode`, `default_data_dir`, `MatthewProctorDatabaseType`,
and the package exception classes:

```python
from matthew_proctor_postcodes_client import (
    DatasetFormatError,
    DatasetUnavailableError,
    InvalidPostcodeError,
    normalize_postcode,
)
```

## Source Schemas

The Australian CSV is `australian_postcodes.csv`. It includes the prescribed Australia Post postcode
ranges for NSW, ACT, VIC, QLD, SA, WA, TAS, and NT, including LVR and PO Box ranges.

Common Australian fields include:

```text
id,postcode,locality,state,long,lat,dc,type,status,sa3,sa3name,sa4,sa4name,region,
Lat_precise,Long_precise,SA1_CODE_2021,SA1_NAME_2021,SA2_CODE_2021,SA2_NAME_2021,
SA3_CODE_2021,SA3_NAME_2021,SA4_CODE_2021,SA4_NAME_2021,RA_2011,RA_2016,RA_2021,
RA_2021_NAME,MMM_2015,MMM_2019,ced,altitude,chargezone,phn_code,phn_name,
lgaregion,lgacode,electorate,electoraterating,sed_code,sed_name
```

The New Zealand CSV is `newzealand_postcodes.csv` and currently uses:

```text
postcode,locality,region,long,lat,territory,island
```

The source datasets may add fields over time. Unknown extra CSV fields are preserved in returned
row dictionaries, while the exported `TypedDict` models document the fields known by this package.

## Development

This package uses `uv`, `ruff`, `pytest`, and `hatchling`. It targets Python 3.12 or newer.

## CI/CD

Package CI runs on pull requests and pushes to `main` with:

```shell
uv run ruff format --check .
uv run ruff check .
uv run pytest -vv
```

Package publishing is handled by `.github/workflows/package-cd.yaml`. Run it manually or publish a
GitHub Release.
