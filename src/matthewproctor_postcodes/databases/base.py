"""Base class for Matthew Proctor postcode databases."""

from __future__ import annotations

import csv
import os
import tempfile
import threading
from abc import ABC
from io import StringIO
from pathlib import Path
from typing import ClassVar, cast

import httpx

from matthewproctor_postcodes.data_dir import default_data_dir
from matthewproctor_postcodes.exceptions import (
    DatasetDownloadError,
    DatasetFormatError,
    DatasetUnavailableError,
)
from matthewproctor_postcodes.models import MatthewProctorDatabaseType, MatthewProctorPostcodeInfo
from matthewproctor_postcodes.normalization import normalize_postcode

type DatabaseIndex[R] = dict[str, tuple[R, ...]]


class MatthewProctorPostcodesDatabase[R: MatthewProctorPostcodeInfo](ABC):
    """Locally cached and indexed Matthew Proctor postcode database."""

    database_type: ClassVar[MatthewProctorDatabaseType]
    database_filename: ClassVar[str]
    database_urls: ClassVar[tuple[str, ...]]
    postcode_field_name: ClassVar[str] = "postcode"

    def __init__(self) -> None:
        """Initialize an unloaded database with a per-instance load lock."""
        self._index: DatabaseIndex[R] | None = None
        self._load_lock = threading.Lock()

    @property
    def database_path(self) -> Path:
        """Return the local CSV path for this database."""
        if not self.database_filename:
            raise ValueError("database_filename must be configured for this database.")
        return default_data_dir() / self.database_filename

    @property
    def is_loaded(self) -> bool:
        """Return whether this database has been loaded into memory."""
        return self._index is not None

    def lookup(
        self,
        postcode: str,
        *,
        request_timeout_seconds: float = 30.0,
        download_if_missing: bool = True,
    ) -> list[R]:
        """Return every row matching ``postcode``.

        A postcode can legitimately map to several localities, so the method always returns a
        list. An unknown but well-formed postcode returns an empty list.
        """
        normalized_postcode = normalize_postcode(postcode)
        self._ensure_loaded(
            download_if_missing=download_if_missing,
            request_timeout_seconds=request_timeout_seconds,
        )

        assert self._index is not None
        return list(self._index.get(normalized_postcode, ()))

    def _ensure_loaded(
        self,
        *,
        download_if_missing: bool,
        request_timeout_seconds: float,
    ) -> None:
        if self._index is not None:
            return
        if request_timeout_seconds <= 0:
            raise ValueError("request_timeout_seconds must be greater than zero.")

        with self._load_lock:
            if self._index is not None:
                return

            if not self.database_urls:
                raise DatasetUnavailableError("No database URLs were configured for this database.")
            if not self.database_filename:
                raise DatasetUnavailableError("No database filename was configured for this database.")

            path = self.database_path
            if not path.is_file():
                if not download_if_missing:
                    raise DatasetUnavailableError(
                        f"Postcode database does not exist at {path} and downloads are disabled."
                    )
                self._download_database(
                    destination=path,
                    timeout_seconds=request_timeout_seconds,
                )

            self._index = self._read_database(path)

    def _download_database(
        self,
        *,
        destination: Path,
        timeout_seconds: float,
    ) -> None:
        """Download a CSV from configured URLs and atomically persist it."""
        if not self.database_urls:
            raise DatasetUnavailableError("No database URLs were configured for this database.")

        destination.parent.mkdir(parents=True, exist_ok=True)
        errors: list[Exception] = []

        with httpx.Client(
            follow_redirects=True,
            timeout=timeout_seconds,
        ) as client:
            for database_url in self.database_urls:
                try:
                    response = client.get(database_url)
                    response.raise_for_status()
                except httpx.HTTPError as error:
                    error.add_note(f"Database URL: {database_url}")
                    errors.append(error)
                    continue

                if not response.content:
                    errors.append(DatasetUnavailableError(f"Database URL {database_url!r} returned an empty response."))
                    continue

                self._atomic_write(destination, response.content)
                return

        raise DatasetDownloadError(
            "Could not download the postcode database from any configured URL.",
            errors,
        )

    @staticmethod
    def _atomic_write(destination: Path, content: bytes) -> None:
        """Write bytes to a temporary sibling and replace the destination atomically."""
        destination.parent.mkdir(parents=True, exist_ok=True)
        file_descriptor, temporary_name = tempfile.mkstemp(
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
        )
        os.close(file_descriptor)
        temporary_path = Path(temporary_name)

        try:
            temporary_path.write_bytes(content)
            temporary_path.replace(destination)
        finally:
            temporary_path.unlink(missing_ok=True)

    def _read_database(self, path: Path) -> DatabaseIndex[R]:
        """Parse a CSV and construct a postcode-to-rows index."""
        try:
            with path.open(encoding="utf-8-sig", newline="") as file:
                contents = file.read()
        except OSError as error:
            raise DatasetUnavailableError(f"Could not read postcode database {path}.") from error
        except UnicodeError as error:
            raise DatasetFormatError(f"Database {path} is not valid UTF-8 CSV.") from error

        reader = csv.DictReader(StringIO(contents))
        if not reader.fieldnames:
            raise DatasetFormatError(f"Database {path} has no CSV header.")

        if self.postcode_field_name not in reader.fieldnames:
            raise DatasetFormatError(f"Database {path} does not contain a {self.postcode_field_name} column.")

        mutable_index: dict[str, list[R]] = {}
        for line_number, raw_row in enumerate(reader, start=2):
            row = self._parse_row(raw_row, path=path, line_number=line_number)
            if row is None:
                continue
            postcode = row[self.postcode_field_name]
            mutable_index.setdefault(postcode, []).append(row)

        return {postcode: tuple(rows) for postcode, rows in mutable_index.items()}

    def _parse_row(
        self,
        raw_row: dict[str | None, str | None],
        *,
        path: Path,
        line_number: int,
    ) -> R | None:
        if None in raw_row:
            raise DatasetFormatError(f"Database {path} has extra unheaded columns on line {line_number}.")

        row = {
            str(key).strip(): (None if value is None or not value.strip() else value.strip())
            for key, value in raw_row.items()
            if key is not None
        }
        postcode_value = row.get(self.postcode_field_name)
        if postcode_value is None:
            return None

        try:
            postcode = normalize_postcode(postcode_value)
        except ValueError as error:
            raise DatasetFormatError(
                f"Database {path} contains invalid postcode {postcode_value!r} on line {line_number}."
            ) from error

        row["database"] = self.database_type
        row[self.postcode_field_name] = postcode
        return cast(R, row)
