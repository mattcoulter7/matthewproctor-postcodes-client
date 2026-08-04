from pathlib import Path

import httpx
import pytest

import matthew_proctor_postcodes_client.clients.base as base_module
from matthew_proctor_postcodes_client import (
    DatasetFormatError,
    DatasetUnavailableError,
    MatthewProctorDatabaseType,
)
from matthew_proctor_postcodes_client.clients.base import MatthewProctorPostcodesClient


class ExamplePostcodesClient(MatthewProctorPostcodesClient[dict[str, object]]):
    """Concrete test client for base client behavior."""

    database_type = MatthewProctorDatabaseType.AUS
    database_filename = "custom_postcodes.csv"
    database_urls = ("https://example.test/data/custom_postcodes.csv",)
    postcode_field_name = "postcode"


class CustomPostcodeFieldClient(MatthewProctorPostcodesClient[dict[str, object]]):
    """Concrete test client with a non-standard postcode header."""

    database_type = MatthewProctorDatabaseType.NZL
    database_filename = "custom_field_postcodes.csv"
    database_urls = ("https://example.test/data/custom_field_postcodes.csv",)
    postcode_field_name = "postal_code"


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
        download_if_missing=False,
    )
    client.data_dir = tmp_path

    entries = await client.lookup("3004")

    assert [entry["locality"] for entry in entries] == [
        "MELBOURNE",
        "ST KILDA ROAD CENTRAL",
    ]
    assert all(entry["database"] == MatthewProctorDatabaseType.AUS for entry in entries)
    assert entries[0]["dc"] == "MELBOURNE"


def test_database_path_uses_explicit_database_filename(tmp_path: Path) -> None:
    client = ExamplePostcodesClient()
    client.data_dir = tmp_path

    assert client.database_path == tmp_path / "custom_postcodes.csv"


def test_database_path_ignores_database_url_path_and_uses_configured_filename(tmp_path: Path) -> None:
    class DifferentUrlSameFilenameClient(ExamplePostcodesClient):
        database_urls = ("https://example.test/other/source.csv",)

    client = DifferentUrlSameFilenameClient()
    client.data_dir = tmp_path

    assert client.database_path == tmp_path / "custom_postcodes.csv"


def test_default_data_dir_uses_environment_value(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("MATTHEW_PROCTOR_DATA_DIR", str(tmp_path))

    assert base_module.default_data_dir() == tmp_path


def test_default_data_dir_uses_package_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MATTHEW_PROCTOR_DATA_DIR", raising=False)

    assert base_module.default_data_dir() == Path("data/matthewproctor")


@pytest.mark.asyncio
async def test_missing_baked_file_can_disable_download(tmp_path: Path) -> None:
    client = ExamplePostcodesClient(
        download_if_missing=False,
    )
    client.data_dir = tmp_path

    with pytest.raises(DatasetUnavailableError):
        await client.lookup("3000")


@pytest.mark.asyncio
async def test_missing_file_can_be_downloaded(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    client = ExamplePostcodesClient()
    client.data_dir = tmp_path

    async def fake_download(
        cls: type[ExamplePostcodesClient],
        *,
        database_urls: tuple[str, ...],
        destination: Path,
        timeout_seconds: float,
    ) -> None:
        _ = (cls, database_urls, timeout_seconds)
        destination.write_text("postcode,locality\n3000,MELBOURNE\n", encoding="utf-8")

    monkeypatch.setattr(ExamplePostcodesClient, "_download_database", classmethod(fake_download))

    entries = await client.lookup("3000")

    assert entries == [
        {
            "database": MatthewProctorDatabaseType.AUS,
            "postcode": "3000",
            "locality": "MELBOURNE",
        }
    ]


@pytest.mark.asyncio
async def test_postcode_field_name_comes_from_class_configuration(tmp_path: Path) -> None:
    database = tmp_path / "custom_field_postcodes.csv"
    database.write_text("postal_code,locality\n0110,Abbey Caves\n", encoding="utf-8")
    client = CustomPostcodeFieldClient(download_if_missing=False)
    client.data_dir = tmp_path

    entries = await client.lookup("110")

    assert entries == [
        {
            "database": MatthewProctorDatabaseType.NZL,
            "postal_code": "0110",
            "locality": "Abbey Caves",
        }
    ]


@pytest.mark.asyncio
async def test_extra_unheaded_columns_raise_dataset_format_error(tmp_path: Path) -> None:
    database = tmp_path / "custom_postcodes.csv"
    database.write_text("postcode,locality\n3000,MELBOURNE,extra\n", encoding="utf-8")
    client = ExamplePostcodesClient(download_if_missing=False)
    client.data_dir = tmp_path

    with pytest.raises(DatasetFormatError):
        await client.lookup("3000")


@pytest.mark.asyncio
async def test_empty_csv_raises_dataset_format_error(tmp_path: Path) -> None:
    database = tmp_path / "custom_postcodes.csv"
    database.write_text("", encoding="utf-8")
    client = ExamplePostcodesClient(download_if_missing=False)
    client.data_dir = tmp_path

    with pytest.raises(DatasetFormatError):
        await client.lookup("3000")


@pytest.mark.asyncio
async def test_csv_without_postcode_column_raises_dataset_format_error(tmp_path: Path) -> None:
    database = tmp_path / "custom_postcodes.csv"
    database.write_text("locality\nMELBOURNE\n", encoding="utf-8")
    client = ExamplePostcodesClient(download_if_missing=False)
    client.data_dir = tmp_path

    with pytest.raises(DatasetFormatError):
        await client.lookup("3000")


@pytest.mark.asyncio
async def test_invalid_csv_postcode_raises_dataset_format_error(tmp_path: Path) -> None:
    database = tmp_path / "custom_postcodes.csv"
    database.write_text("postcode,locality\ninvalid,MELBOURNE\n", encoding="utf-8")
    client = ExamplePostcodesClient(download_if_missing=False)
    client.data_dir = tmp_path

    with pytest.raises(DatasetFormatError):
        await client.lookup("3000")


@pytest.mark.asyncio
async def test_blank_csv_postcode_rows_are_skipped(tmp_path: Path) -> None:
    database = tmp_path / "custom_postcodes.csv"
    database.write_text('postcode,locality\n,"MISSING"\n3000,"MELBOURNE"\n', encoding="utf-8")
    client = ExamplePostcodesClient(download_if_missing=False)
    client.data_dir = tmp_path

    entries = await client.lookup("3000")

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
    requested_urls: list[str] = []

    def __init__(self, **kwargs: object) -> None:
        self.kwargs = kwargs

    async def __aenter__(self) -> "FakeAsyncClient":
        return self

    async def __aexit__(self, *args: object) -> None:
        return None

    async def get(self, source_url: str) -> FakeResponse:
        self.source_url = source_url
        type(self).requested_urls.append(source_url)
        return self.response


@pytest.mark.asyncio
async def test_download_database_writes_response_content(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(base_module.httpx, "AsyncClient", FakeAsyncClient)
    FakeAsyncClient.requested_urls = []
    destination = tmp_path / "custom_postcodes.csv"

    await ExamplePostcodesClient()._download_database(
        database_urls=("https://example.test/custom_postcodes.csv",),
        destination=destination,
        timeout_seconds=1,
    )

    assert FakeAsyncClient.requested_urls == ["https://example.test/custom_postcodes.csv"]
    assert destination.read_bytes() == b"postcode,locality\n3000,MELBOURNE\n"


@pytest.mark.asyncio
async def test_download_database_raises_when_response_is_empty(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(base_module.httpx, "AsyncClient", FakeAsyncClient)
    FakeAsyncClient.requested_urls = []
    FakeAsyncClient.response = FakeResponse(b"")

    with pytest.raises(DatasetUnavailableError):
        await ExamplePostcodesClient()._download_database(
            database_urls=("https://example.test/custom_postcodes.csv",),
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
    FakeAsyncClient.requested_urls = []
    FakeAsyncClient.response = FakeResponse(b"", httpx.HTTPError("boom"))

    with pytest.raises(DatasetUnavailableError):
        await ExamplePostcodesClient()._download_database(
            database_urls=("https://example.test/custom_postcodes.csv",),
            destination=tmp_path / "custom_postcodes.csv",
            timeout_seconds=1,
        )

    FakeAsyncClient.response = FakeResponse(b"postcode,locality\n3000,MELBOURNE\n")


@pytest.mark.asyncio
async def test_download_database_tries_next_url_when_first_fails(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(base_module.httpx, "AsyncClient", FakeAsyncClient)
    destination = tmp_path / "custom_postcodes.csv"

    responses = {
        "https://example.test/first.csv": FakeResponse(b"", httpx.HTTPError("boom")),
        "https://example.test/second.csv": FakeResponse(b"postcode,locality\n3000,MELBOURNE\n"),
    }

    async def fake_get(self: FakeAsyncClient, source_url: str) -> FakeResponse:
        type(self).requested_urls.append(source_url)
        return responses[source_url]

    FakeAsyncClient.requested_urls = []
    monkeypatch.setattr(FakeAsyncClient, "get", fake_get)

    await ExamplePostcodesClient()._download_database(
        database_urls=("https://example.test/first.csv", "https://example.test/second.csv"),
        destination=destination,
        timeout_seconds=1,
    )

    assert FakeAsyncClient.requested_urls == ["https://example.test/first.csv", "https://example.test/second.csv"]
    assert destination.read_bytes() == b"postcode,locality\n3000,MELBOURNE\n"


def test_request_timeout_must_be_positive() -> None:
    with pytest.raises(ValueError):
        ExamplePostcodesClient(request_timeout_seconds=0)
