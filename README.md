<div align="center">

# Matthew Proctor Postcodes

Typed Python 3.12+ lookup API for Matthew Proctor Australian and New Zealand postcode CSV datasets.

![Python](https://img.shields.io/badge/Python-3.12+-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![UV](https://img.shields.io/badge/UV-Fast-6E40C9?style=for-the-badge)
![Hatchling](https://img.shields.io/badge/Hatchling-PEP517-6E40C9?style=for-the-badge)
![Ruff](https://img.shields.io/badge/Ruff-Lint-000000?style=for-the-badge)
![Pytest](https://img.shields.io/badge/Pytest-Unit-08979C?style=for-the-badge)
![PyPI](https://img.shields.io/badge/PyPI-Publish-6E40C9?style=for-the-badge)

[![Package CI](https://github.com/mattcoulter7/matthewproctor-postcodes/actions/workflows/package-ci.yaml/badge.svg?branch=main)](https://github.com/mattcoulter7/matthewproctor-postcodes/actions/workflows/package-ci.yaml)
[![Package CD](https://github.com/mattcoulter7/matthewproctor-postcodes/actions/workflows/package-cd.yaml/badge.svg?branch=main)](https://github.com/mattcoulter7/matthewproctor-postcodes/actions/workflows/package-cd.yaml)

</div>

## Quick Start

Install the package:

```shell
pip install matthewproctor-postcodes
```

Look up a postcode:

```python
from matthewproctor_postcodes import lookup_postcode

entries = lookup_postcode("3004", "AUS")

for entry in entries:
    print(entry["locality"], entry.get("RA_2021_NAME"))
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

- `lookup_postcode("3004", "AUS")` returns a read-only sequence of `AUSMatthewProctorPostcodeInfo` rows.
- `lookup_postcode("110", "NZL")` returns a read-only sequence of `NZLMatthewProctorPostcodeInfo` rows.
- Country codes are normalized to uppercase alpha-3 values.
- A lookup returns every locality for a postcode.
- Unknown but well-formed postcodes return an empty sequence.
- Postcodes are normalized to four decimal digits, so `"110"` is looked up as `"0110"`.
- Invalid postcodes raise `InvalidPostcodeError`; values must be one to four decimal digits.
- Unsupported countries raise `UnsupportedCountryError`.
- Failed downloads from every configured source raise `DatasetDownloadError`, preserving the
  original per-source exceptions for `except*` handling.
- A local CSV is preferred; a missing CSV is downloaded and saved atomically.
- Each country database is loaded lazily once, then reused as an in-memory index.
- Row models are lightweight `TypedDict` types that use the known source CSV headers.

## Installation

```bash
pip install matthewproctor-postcodes
```

For local development from a checkout:

```bash
uv sync --refresh
```

## Storage

Set `matthewproctor_DATA_DIR` to control where files are read and downloaded:

```bash
export matthewproctor_DATA_DIR=data/matthewproctor
```

This produces:

```text
data/matthewproctor/australian_postcodes.csv
data/matthewproctor/newzealand_postcodes.csv
```

If the environment variable is absent, the default is `data/matthewproctor` relative to the
current working directory.

For an enterprise image, bake either CSV into that path and pass `download_if_missing=False`.

## Usage

```python
from matthewproctor_postcodes import lookup_postcode

aus_entries = lookup_postcode("3004", "AUS")
nz_entries = lookup_postcode("110", "NZL")

print([entry["locality"] for entry in aus_entries])
print([entry["locality"] for entry in nz_entries])
```

`lookup_postcode()` is the top-level public API and returns a `collections.abc.Sequence` so callers
can safely consume country-specific row types through the shared `MatthewProctorPostcodeInfo` union.
Convert it with `list(...)` if your code needs to mutate or serialize a concrete list object:

```python
entries = list(lookup_postcode("3004", "AUS"))
```

## Lookup Options

`lookup_postcode()` accepts these keyword arguments:

- `request_timeout_seconds`: HTTP timeout used when a missing CSV must be downloaded. Defaults to `30.0`.
- `download_if_missing`: whether to download the source CSV when it is not already present locally. Defaults to `True`.

Storage is configured with `matthewproctor_DATA_DIR`:

```python
import os

from matthewproctor_postcodes import lookup_postcode

os.environ["matthewproctor_DATA_DIR"] = "/app/data/matthewproctor"

entries = lookup_postcode(
    "3004",
    "AUS",
    request_timeout_seconds=10.0,
    download_if_missing=False,
)
```

Lifecycle options only affect an attempt to load an unloaded database. Once a country database has
loaded, later calls use the same in-memory index and do not make another request. A failed call with
`download_if_missing=False` does not poison the database; a later call with downloads enabled may
still load it.

Exception classes and lower-level helpers are available from their owning modules:

```python
from matthewproctor_postcodes.exceptions import DatasetDownloadError
from matthewproctor_postcodes.normalization import normalize_postcode
```

Database classes are available from `matthewproctor_postcodes.databases` for advanced use,
and `MatthewProctorDatabaseType` is available from `matthewproctor_postcodes.models`.

`DatasetDownloadError` is an `ExceptionGroup`, so callers can either handle the whole download
failure or selectively handle grouped source failures:

```python
import httpx

try:
    lookup_postcode("3000", "AUS")
except* httpx.TimeoutException as errors:
    for error in errors.exceptions:
        print(error)
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
Returned rows also include a `database` field injected by this package with the source
`MatthewProctorDatabaseType`.

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
