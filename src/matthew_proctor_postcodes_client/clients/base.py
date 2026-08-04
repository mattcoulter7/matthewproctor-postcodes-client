"""Base async client for local or downloaded Matthew Proctor postcode databases."""

from __future__ import annotations

import csv
import os
import tempfile
from io import StringIO
from pathlib import Path
from typing import ClassVar
from urllib.parse import urlsplit

import aiofiles
import aiofiles.os
import httpx
from aiocache import cached

from matthew_proctor_postcodes_client.constants import (
    DATA_DIR_ENV_VAR,
    DEFAULT_DATA_DIR,
)
from matthew_proctor_postcodes_client.exceptions import (
    DatasetFormatError,
    DatasetUnavailableError,
)
from matthew_proctor_postcodes_client.models import MatthewProctorDatabaseType, MatthewProctorPostcodeInfo
from matthew_proctor_postcodes_client.utils import normalize_postcode

type DatabaseIndex = dict[str, tuple[MatthewProctorPostcodeInfo, ...]]


def default_data_dir() -> Path:
    """Resolve the configured on-disk database directory."""
    configured = os.getenv(DATA_DIR_ENV_VAR)
    return Path(configured).expanduser() if configured else DEFAULT_DATA_DIR


class MatthewProctorPostcodesClient[R: MatthewProctorPostcodeInfo]:
    """Generic client for one postcode database."""

    database_type: ClassVar[MatthewProctorDatabaseType]
    database_url: ClassVar[str]
    postcode_field_name: ClassVar[str]

    def __init__(
        self,
        *,
        data_dir: str | Path | None = None,
        request_timeout_seconds: float = 30.0,
        download_if_missing: bool = True,
    ) -> None:
        """Configure local storage, download behavior, and request timeout."""
        if request_timeout_seconds <= 0:
            raise ValueError("request_timeout_seconds must be greater than zero.")

        self.data_dir = Path(data_dir).expanduser() if data_dir is not None else default_data_dir()
        self.request_timeout_seconds = request_timeout_seconds
        self.download_if_missing = download_if_missing

    @property
    def database_path(self) -> Path:
        """Return the local CSV path for this client."""
        return self.data_dir / Path(urlsplit(self.database_url).path).name

    async def lookup(self, postcode: str) -> list[R]:
        """Return every row matching ``postcode``.

        A postcode can legitimately map to several localities, so the method always returns a
        list. An unknown but well-formed postcode returns an empty list.
        """
        normalized_postcode = normalize_postcode(postcode)
        index = await type(self)._load_database_cached(
            database_type=self.database_type,
            data_dir=str(self.data_dir.resolve()),
            database_url=self.database_url,
            postcode_field_name=self.postcode_field_name,
            download_if_missing=self.download_if_missing,
            request_timeout_seconds=self.request_timeout_seconds,
        )
        rows = index.get(normalized_postcode, ())
        return list(rows)

    @classmethod
    @cached(noself=True)
    async def _load_database_cached(
        cls,
        *,
        database_type: MatthewProctorDatabaseType,
        data_dir: str,
        database_url: str,
        postcode_field_name: str,
        download_if_missing: bool,
        request_timeout_seconds: float,
    ) -> DatabaseIndex:
        """Load and index a database once for each effective storage/source configuration."""
        return await cls._load_database(
            database_type=database_type,
            data_dir=data_dir,
            database_url=database_url,
            postcode_field_name=postcode_field_name,
            download_if_missing=download_if_missing,
            request_timeout_seconds=request_timeout_seconds,
        )

    @classmethod
    async def _load_database(
        cls,
        *,
        database_type: MatthewProctorDatabaseType,
        data_dir: str,
        database_url: str,
        postcode_field_name: str,
        download_if_missing: bool,
        request_timeout_seconds: float,
    ) -> DatabaseIndex:
        """Load and index a database once for each effective storage/source configuration."""
        path = Path(data_dir) / Path(urlsplit(database_url).path).name
        if not path.is_file():
            if not download_if_missing:
                raise DatasetUnavailableError(f"Postcode database does not exist at {path} and downloads are disabled.")
            await cls._download_database(
                database_url=database_url,
                destination=path,
                timeout_seconds=request_timeout_seconds,
            )

        return await cls._read_database(
            path,
            database_type=database_type,
            postcode_field_name=postcode_field_name,
        )

    @classmethod
    async def _download_database(
        cls,
        *,
        database_url: str,
        destination: Path,
        timeout_seconds: float,
    ) -> None:
        """Download a CSV and atomically persist it for subsequent process starts."""
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            async with httpx.AsyncClient(
                follow_redirects=True,
                timeout=timeout_seconds,
            ) as client:
                response = await client.get(database_url)
                response.raise_for_status()
        except httpx.HTTPError as error:
            raise DatasetUnavailableError(f"Could not download postcode database from {database_url}.") from error

        if not response.content:
            raise DatasetUnavailableError(f"Downloaded postcode database from {database_url} was empty.")

        await cls._atomic_write(destination, response.content)

    @classmethod
    async def _atomic_write(cls, destination: Path, content: bytes) -> None:
        """Write bytes to a temporary sibling and replace the destination atomically."""
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary_path: Path | None = None
        file_descriptor, temporary_name = tempfile.mkstemp(
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
        )
        os.close(file_descriptor)
        temporary_path = Path(temporary_name)

        try:
            async with aiofiles.open(temporary_path, mode="wb") as temporary_file:
                await temporary_file.write(content)
                await temporary_file.flush()
            await aiofiles.os.replace(temporary_path, destination)
        finally:
            if temporary_path is not None and await aiofiles.os.path.exists(temporary_path):
                await aiofiles.os.remove(temporary_path)

    @classmethod
    async def _read_database(
        cls,
        path: Path,
        *,
        database_type: MatthewProctorDatabaseType | None = None,
        postcode_field_name: str | None = None,
    ) -> DatabaseIndex:
        """Parse a CSV and construct a postcode-to-rows index."""
        resolved_database_type = database_type or cls.database_type
        resolved_postcode_field_name = postcode_field_name or cls.postcode_field_name
        try:
            async with aiofiles.open(path, encoding="utf-8-sig", newline="") as database_file:
                contents = await database_file.read()
        except OSError as error:
            raise DatasetUnavailableError(f"Could not read postcode database {path}.") from error
        except UnicodeError as error:
            raise DatasetFormatError(f"Database {path} is not valid UTF-8 CSV.") from error

        reader = csv.DictReader(StringIO(contents))
        if not reader.fieldnames:
            raise DatasetFormatError(f"Database {path} has no CSV header.")

        if resolved_postcode_field_name not in reader.fieldnames:
            raise DatasetFormatError(f"Database {path} does not contain a {resolved_postcode_field_name} column.")

        mutable_index: dict[str, list[DatabaseRow]] = {}
        for line_number, raw_row in enumerate(reader, start=2):
            if None in raw_row:
                raise DatasetFormatError(f"Database {path} has extra unheaded columns on line {line_number}.")

            row = {
                str(key).strip(): (None if value is None or not value.strip() else value.strip())
                for key, value in raw_row.items()
                if key is not None
            }
            postcode_value = row.get(resolved_postcode_field_name)
            if postcode_value is None:
                continue
            try:
                postcode = normalize_postcode(postcode_value)
            except ValueError as error:
                raise DatasetFormatError(
                    f"Database {path} contains invalid postcode {postcode_value!r} on line {line_number}."
                ) from error
            row["database"] = resolved_database_type
            row[resolved_postcode_field_name] = postcode
            mutable_index.setdefault(postcode, []).append(row)

        return {postcode: tuple(rows) for postcode, rows in mutable_index.items()}
