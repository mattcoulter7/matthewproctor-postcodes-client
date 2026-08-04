from pathlib import Path

import httpx
import pytest

import matthew_proctor_postcodes_client.clients.base as base_module
from matthew_proctor_postcodes_client import (
    CountryMismatchError,
    DatasetFormatError,
    DatasetUnavailableError,
    MatthewProctorDatabaseType,
    UnsupportedCountryError,
)
from matthew_proctor_postcodes_client.clients.base import MatthewProctorPostcodesClient


class ExamplePostcodesClient(MatthewProctorPostcodesClient[dict[str, object]]):
    """Concrete test client for base client behavior."""

    database = MatthewProctorDatabaseType.AUS
    default_download_url = "https://example.test/data/custom_postcodes.csv"


@pytest.mark.asyncio
async def test_lookup_uses_local_file_and_returns_all_rows(tmp_path: Path) -> None:
    database = tmp_path / "custom_postcodes.csv"
    database.write_text(
        "id,postcode,locality,state,long,lat,dc,type,status,sa3,sa3name,RA_2021\n"
        '1,"3004","MELBOURNE","VIC","144.98","-37.83","MELBOURNE",'
        '"Delivery Area","Updated","20605","Port Phillip","20"\n'
        '2,"3004","ST KILDA ROAD CENTRAL","VIC","144.97","-37.84","MELBOURNE",'
        '"Delivery Area","Updated","20605","Port Phillip","20"\n',
        encoding="utf-8",
    )
    client = ExamplePostcodesClient(
        data_dir=tmp_path,
        download_if_missing=False,
    )

    entries = await client.lookup("3004", "AUS")

    assert [entry["locality"] for entry in entries] == [
        "MELBOURNE",
        "ST KILDA ROAD CENTRAL",
    ]
    assert all(entry["database"] == MatthewProctorDatabaseType.AUS for entry in entries)
    assert entries[0]["dc"] == "MELBOURNE"


def test_database_path_uses_filename_from_download_url(tmp_path: Path) -> None:
    client = ExamplePostcodesClient(data_dir=tmp_path)

    assert client.database_path == tmp_path / "custom_postcodes.csv"


def test_database_path_uses_filename_from_configured_source_url(tmp_path: Path) -> None:
    client = ExamplePostcodesClient(
        data_dir=tmp_path,
        source_url="https://example.test/other/source.csv",
    )

    assert client.database_path == tmp_path / "source.csv"


def test_default_data_dir_uses_environment_value(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("MATTHEW_PROCTOR_DATA_DIR", str(tmp_path))

    assert base_module.default_data_dir() == tmp_path


def test_default_data_dir_uses_package_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MATTHEW_PROCTOR_DATA_DIR", raising=False)

    assert base_module.default_data_dir() == Path("data/matthewproctor")


@pytest.mark.asyncio
async def test_country_must_match_client(tmp_path: Path) -> None:
    client = ExamplePostcodesClient(data_dir=tmp_path)

    with pytest.raises(CountryMismatchError):
        await client.lookup("3000", "NZL")


@pytest.mark.asyncio
async def test_alpha_two_country_codes_are_not_supported(tmp_path: Path) -> None:
    client = ExamplePostcodesClient(data_dir=tmp_path)

    with pytest.raises(UnsupportedCountryError):
        await client.lookup("3000", "AU")


@pytest.mark.asyncio
async def test_missing_baked_file_can_disable_download(tmp_path: Path) -> None:
    client = ExamplePostcodesClient(
        data_dir=tmp_path,
        download_if_missing=False,
    )

    with pytest.raises(DatasetUnavailableError):
        await client.lookup("3000", "AUS")


@pytest.mark.asyncio
async def test_missing_file_can_be_downloaded(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    client = ExamplePostcodesClient(data_dir=tmp_path)

    async def fake_download(*, source_url: str, destination: Path, timeout_seconds: float) -> None:
        _ = (source_url, timeout_seconds)
        destination.write_text("postcode,locality\n3000,MELBOURNE\n", encoding="utf-8")

    monkeypatch.setattr(client, "_download_database", fake_download)

    entries = await client.lookup("3000", "AUS")

    assert entries == [
        {
            "database": MatthewProctorDatabaseType.AUS,
            "postcode": "3000",
            "locality": "MELBOURNE",
        }
    ]


@pytest.mark.asyncio
async def test_extra_unheaded_columns_raise_dataset_format_error(tmp_path: Path) -> None:
    database = tmp_path / "custom_postcodes.csv"
    database.write_text("postcode,locality\n3000,MELBOURNE,extra\n", encoding="utf-8")
    client = ExamplePostcodesClient(data_dir=tmp_path, download_if_missing=False)

    with pytest.raises(DatasetFormatError):
        await client.lookup("3000", "AUS")


@pytest.mark.asyncio
async def test_empty_csv_raises_dataset_format_error(tmp_path: Path) -> None:
    database = tmp_path / "custom_postcodes.csv"
    database.write_text("", encoding="utf-8")
    client = ExamplePostcodesClient(data_dir=tmp_path, download_if_missing=False)

    with pytest.raises(DatasetFormatError):
        await client.lookup("3000", "AUS")


@pytest.mark.asyncio
async def test_csv_without_postcode_column_raises_dataset_format_error(tmp_path: Path) -> None:
    database = tmp_path / "custom_postcodes.csv"
    database.write_text("locality\nMELBOURNE\n", encoding="utf-8")
    client = ExamplePostcodesClient(data_dir=tmp_path, download_if_missing=False)

    with pytest.raises(DatasetFormatError):
        await client.lookup("3000", "AUS")


@pytest.mark.asyncio
async def test_invalid_csv_postcode_raises_dataset_format_error(tmp_path: Path) -> None:
    database = tmp_path / "custom_postcodes.csv"
    database.write_text("postcode,locality\ninvalid,MELBOURNE\n", encoding="utf-8")
    client = ExamplePostcodesClient(data_dir=tmp_path, download_if_missing=False)

    with pytest.raises(DatasetFormatError):
        await client.lookup("3000", "AUS")


@pytest.mark.asyncio
async def test_blank_csv_postcode_rows_are_skipped(tmp_path: Path) -> None:
    database = tmp_path / "custom_postcodes.csv"
    database.write_text('postcode,locality\n,"MISSING"\n3000,"MELBOURNE"\n', encoding="utf-8")
    client = ExamplePostcodesClient(data_dir=tmp_path, download_if_missing=False)

    entries = await client.lookup("3000", "AUS")

    assert len(entries) == 1
    assert entries[0]["locality"] == "MELBOURNE"


@pytest.mark.asyncio
async def test_missing_csv_read_raises_dataset_unavailable_error(tmp_path: Path) -> None:
    with pytest.raises(DatasetUnavailableError):
        await ExamplePostcodesClient._read_database(tmp_path / "missing.csv")


@pytest.mark.asyncio
async def test_non_utf8_csv_raises_dataset_format_error(tmp_path: Path) -> None:
    database = tmp_path / "custom_postcodes.csv"
    database.write_bytes(b"\xff")

    with pytest.raises(DatasetFormatError):
        await ExamplePostcodesClient._read_database(database)


@pytest.mark.asyncio
async def test_atomic_write_replaces_destination(tmp_path: Path) -> None:
    destination = tmp_path / "custom_postcodes.csv"

    await ExamplePostcodesClient._atomic_write(destination, b"postcode,locality\n3000,MELBOURNE\n")

    assert destination.read_text(encoding="utf-8") == "postcode,locality\n3000,MELBOURNE\n"


@pytest.mark.asyncio
async def test_atomic_write_removes_temporary_file_when_replace_fails(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    destination = tmp_path / "custom_postcodes.csv"

    async def fake_replace(source: Path, target: Path) -> None:
        _ = (source, target)
        raise OSError("boom")

    monkeypatch.setattr(base_module.aiofiles.os, "replace", fake_replace)

    with pytest.raises(OSError):
        await ExamplePostcodesClient._atomic_write(destination, b"postcode,locality\n3000,MELBOURNE\n")

    assert list(tmp_path.glob(".custom_postcodes.csv.*.tmp")) == []


class FakeResponse:
    """Minimal httpx response stand-in for download tests."""

    def __init__(self, content: bytes, error: httpx.HTTPError | None = None) -> None:
        self.content = content
        self.error = error

    def raise_for_status(self) -> None:
        if self.error is not None:
            raise self.error


class FakeAsyncClient:
    """Minimal async client stand-in for download tests."""

    response = FakeResponse(b"postcode,locality\n3000,MELBOURNE\n")

    def __init__(self, **kwargs: object) -> None:
        self.kwargs = kwargs

    async def __aenter__(self) -> "FakeAsyncClient":
        return self

    async def __aexit__(self, *args: object) -> None:
        return None

    async def get(self, source_url: str) -> FakeResponse:
        self.source_url = source_url
        return self.response


@pytest.mark.asyncio
async def test_download_database_writes_response_content(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(base_module.httpx, "AsyncClient", FakeAsyncClient)
    destination = tmp_path / "custom_postcodes.csv"

    await ExamplePostcodesClient()._download_database(
        source_url="https://example.test/custom_postcodes.csv",
        destination=destination,
        timeout_seconds=1,
    )

    assert destination.read_bytes() == b"postcode,locality\n3000,MELBOURNE\n"


@pytest.mark.asyncio
async def test_download_database_raises_when_response_is_empty(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(base_module.httpx, "AsyncClient", FakeAsyncClient)
    FakeAsyncClient.response = FakeResponse(b"")

    with pytest.raises(DatasetUnavailableError):
        await ExamplePostcodesClient()._download_database(
            source_url="https://example.test/custom_postcodes.csv",
            destination=tmp_path / "custom_postcodes.csv",
            timeout_seconds=1,
        )

    FakeAsyncClient.response = FakeResponse(b"postcode,locality\n3000,MELBOURNE\n")


@pytest.mark.asyncio
async def test_download_database_wraps_http_errors(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(base_module.httpx, "AsyncClient", FakeAsyncClient)
    FakeAsyncClient.response = FakeResponse(b"", httpx.HTTPError("boom"))

    with pytest.raises(DatasetUnavailableError):
        await ExamplePostcodesClient()._download_database(
            source_url="https://example.test/custom_postcodes.csv",
            destination=tmp_path / "custom_postcodes.csv",
            timeout_seconds=1,
        )

    FakeAsyncClient.response = FakeResponse(b"postcode,locality\n3000,MELBOURNE\n")


def test_client_configuration_rejects_mismatched_database() -> None:
    with pytest.raises(CountryMismatchError):
        ExamplePostcodesClient(database="NZL")


def test_request_timeout_must_be_positive() -> None:
    with pytest.raises(ValueError):
        ExamplePostcodesClient(request_timeout_seconds=0)
