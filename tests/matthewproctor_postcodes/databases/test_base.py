from pathlib import Path

import httpx
import pytest

import matthewproctor_postcodes.databases.base as base_module
from matthewproctor_postcodes.databases.base import MatthewProctorPostcodesDatabase
from matthewproctor_postcodes.exceptions import (
    DatasetDownloadError,
    DatasetFormatError,
    DatasetUnavailableError,
)
from matthewproctor_postcodes.models import MatthewProctorDatabaseType


class ExamplePostcodesDatabase(MatthewProctorPostcodesDatabase[dict[str, object]]):
    """Concrete test database for base behavior."""

    database_type = MatthewProctorDatabaseType.AUS
    database_filename = "custom_postcodes.csv"
    database_urls = ("https://example.test/data/custom_postcodes.csv",)
    postcode_field_name = "postcode"


class CustomPostcodeFieldDatabase(MatthewProctorPostcodesDatabase[dict[str, object]]):
    """Concrete test database with a non-standard postcode header."""

    database_type = MatthewProctorDatabaseType.NZL
    database_filename = "custom_field_postcodes.csv"
    database_urls = ("https://example.test/data/custom_field_postcodes.csv",)
    postcode_field_name = "postal_code"


def test_lookup_uses_local_file_and_returns_all_rows(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    database_path = tmp_path / "custom_postcodes.csv"
    database_path.write_text(
        "id,postcode,locality,state,long,lat,dc,type,status,sa3,sa3name,RA_2021\n"
        '1,"3004","MELBOURNE","VIC","144.98","-37.83","MELBOURNE",'
        '"Delivery Area","Updated","20605","Port Phillip","20"\n'
        '2,"3004","ST KILDA ROAD CENTRAL","VIC","144.97","-37.84","MELBOURNE",'
        '"Delivery Area","Updated","20605","Port Phillip","20"\n',
        encoding="utf-8",
    )
    monkeypatch.setenv("matthewproctor_DATA_DIR", str(tmp_path))

    entries = ExamplePostcodesDatabase().lookup("3004", download_if_missing=False)

    assert [entry["locality"] for entry in entries] == [
        "MELBOURNE",
        "ST KILDA ROAD CENTRAL",
    ]
    assert all(entry["database"] == MatthewProctorDatabaseType.AUS for entry in entries)
    assert entries[0]["dc"] == "MELBOURNE"


def test_database_path_uses_explicit_database_filename(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("matthewproctor_DATA_DIR", str(tmp_path))

    assert ExamplePostcodesDatabase().database_path == tmp_path / "custom_postcodes.csv"


def test_database_path_ignores_database_url_path_and_uses_configured_filename(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    class DifferentUrlSameFilenameDatabase(ExamplePostcodesDatabase):
        database_urls = ("https://example.test/other/source.csv",)

    monkeypatch.setenv("matthewproctor_DATA_DIR", str(tmp_path))

    assert DifferentUrlSameFilenameDatabase().database_path == tmp_path / "custom_postcodes.csv"


def test_missing_baked_file_can_disable_download(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("matthewproctor_DATA_DIR", str(tmp_path))
    database = ExamplePostcodesDatabase()

    with pytest.raises(DatasetUnavailableError):
        database.lookup("3000", download_if_missing=False)

    assert not database.is_loaded


def test_failed_no_download_call_does_not_poison_later_download(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("matthewproctor_DATA_DIR", str(tmp_path))
    database = ExamplePostcodesDatabase()

    with pytest.raises(DatasetUnavailableError):
        database.lookup("3000", download_if_missing=False)

    def fake_download(*, destination: Path, timeout_seconds: float) -> None:
        assert timeout_seconds == 5
        destination.write_text("postcode,locality\n3000,MELBOURNE\n", encoding="utf-8")

    monkeypatch.setattr(database, "_download_database", fake_download)

    assert database.lookup("3000", request_timeout_seconds=5) == [
        {
            "database": MatthewProctorDatabaseType.AUS,
            "postcode": "3000",
            "locality": "MELBOURNE",
        }
    ]


def test_loaded_database_ignores_later_lifecycle_options(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    database_path = tmp_path / "custom_postcodes.csv"
    database_path.write_text("postcode,locality\n3000,MELBOURNE\n", encoding="utf-8")
    monkeypatch.setenv("matthewproctor_DATA_DIR", str(tmp_path))

    database = ExamplePostcodesDatabase()
    assert database.lookup("3000", download_if_missing=False) != []

    database_path.unlink()

    assert database.lookup("3000", download_if_missing=False, request_timeout_seconds=0) != []


def test_missing_file_can_be_downloaded(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("matthewproctor_DATA_DIR", str(tmp_path))
    database = ExamplePostcodesDatabase()

    def fake_download(*, destination: Path, timeout_seconds: float) -> None:
        assert timeout_seconds == 30.0
        destination.write_text("postcode,locality\n3000,MELBOURNE\n", encoding="utf-8")

    monkeypatch.setattr(database, "_download_database", fake_download)

    assert database.lookup("3000") == [
        {
            "database": MatthewProctorDatabaseType.AUS,
            "postcode": "3000",
            "locality": "MELBOURNE",
        }
    ]


def test_postcode_field_name_comes_from_class_configuration(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "custom_field_postcodes.csv"
    database_path.write_text("postal_code,locality\n0110,Abbey Caves\n", encoding="utf-8")
    monkeypatch.setenv("matthewproctor_DATA_DIR", str(tmp_path))

    entries = CustomPostcodeFieldDatabase().lookup("110", download_if_missing=False)

    assert entries == [
        {
            "database": MatthewProctorDatabaseType.NZL,
            "postal_code": "0110",
            "locality": "Abbey Caves",
        }
    ]


def test_extra_unheaded_columns_raise_dataset_format_error(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    (tmp_path / "custom_postcodes.csv").write_text("postcode,locality\n3000,MELBOURNE,extra\n", encoding="utf-8")
    monkeypatch.setenv("matthewproctor_DATA_DIR", str(tmp_path))

    with pytest.raises(DatasetFormatError):
        ExamplePostcodesDatabase().lookup("3000", download_if_missing=False)


def test_empty_csv_raises_dataset_format_error(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    (tmp_path / "custom_postcodes.csv").write_text("", encoding="utf-8")
    monkeypatch.setenv("matthewproctor_DATA_DIR", str(tmp_path))

    with pytest.raises(DatasetFormatError):
        ExamplePostcodesDatabase().lookup("3000", download_if_missing=False)


def test_csv_without_postcode_column_raises_dataset_format_error(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    (tmp_path / "custom_postcodes.csv").write_text("locality\nMELBOURNE\n", encoding="utf-8")
    monkeypatch.setenv("matthewproctor_DATA_DIR", str(tmp_path))

    with pytest.raises(DatasetFormatError):
        ExamplePostcodesDatabase().lookup("3000", download_if_missing=False)


def test_invalid_csv_postcode_raises_dataset_format_error(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    (tmp_path / "custom_postcodes.csv").write_text("postcode,locality\ninvalid,MELBOURNE\n", encoding="utf-8")
    monkeypatch.setenv("matthewproctor_DATA_DIR", str(tmp_path))

    with pytest.raises(DatasetFormatError):
        ExamplePostcodesDatabase().lookup("3000", download_if_missing=False)


def test_blank_csv_postcode_rows_are_skipped(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    (tmp_path / "custom_postcodes.csv").write_text(
        'postcode,locality\n,"MISSING"\n3000,"MELBOURNE"\n',
        encoding="utf-8",
    )
    monkeypatch.setenv("matthewproctor_DATA_DIR", str(tmp_path))

    entries = ExamplePostcodesDatabase().lookup("3000", download_if_missing=False)

    assert len(entries) == 1
    assert entries[0]["locality"] == "MELBOURNE"


def test_missing_csv_read_raises_dataset_unavailable_error(tmp_path: Path) -> None:
    with pytest.raises(DatasetUnavailableError):
        ExamplePostcodesDatabase()._read_database(tmp_path / "missing.csv")


def test_non_utf8_csv_raises_dataset_format_error(tmp_path: Path) -> None:
    database_path = tmp_path / "custom_postcodes.csv"
    database_path.write_bytes(b"\xff")

    with pytest.raises(DatasetFormatError):
        ExamplePostcodesDatabase()._read_database(database_path)


def test_atomic_write_replaces_destination(tmp_path: Path) -> None:
    destination = tmp_path / "custom_postcodes.csv"

    ExamplePostcodesDatabase._atomic_write(destination, b"postcode,locality\n3000,MELBOURNE\n")

    assert destination.read_text(encoding="utf-8") == "postcode,locality\n3000,MELBOURNE\n"


def test_atomic_write_removes_temporary_file_when_replace_fails(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    destination = tmp_path / "custom_postcodes.csv"

    def fake_replace(self: Path, target: Path) -> Path:
        _ = (self, target)
        raise OSError("boom")

    monkeypatch.setattr(base_module.Path, "replace", fake_replace)

    with pytest.raises(OSError):
        ExamplePostcodesDatabase._atomic_write(destination, b"postcode,locality\n3000,MELBOURNE\n")

    assert list(tmp_path.glob(".custom_postcodes.csv.*.tmp")) == []


class FakeResponse:
    """Minimal httpx response stand-in for download tests."""

    def __init__(self, content: bytes, error: httpx.HTTPError | None = None) -> None:
        self.content = content
        self.error = error

    def raise_for_status(self) -> None:
        if self.error is not None:
            raise self.error


class FakeClient:
    """Minimal client stand-in for download tests."""

    response = FakeResponse(b"postcode,locality\n3000,MELBOURNE\n")
    requested_urls: list[str] = []

    def __init__(self, **kwargs: object) -> None:
        self.kwargs = kwargs

    def __enter__(self) -> "FakeClient":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def get(self, source_url: str) -> FakeResponse:
        self.source_url = source_url
        type(self).requested_urls.append(source_url)
        return self.response


def test_download_database_writes_response_content(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(base_module.httpx, "Client", FakeClient)
    FakeClient.requested_urls = []
    destination = tmp_path / "custom_postcodes.csv"

    ExamplePostcodesDatabase()._download_database(
        destination=destination,
        timeout_seconds=1,
    )

    assert FakeClient.requested_urls == ["https://example.test/data/custom_postcodes.csv"]
    assert destination.read_bytes() == b"postcode,locality\n3000,MELBOURNE\n"


def test_download_database_raises_when_response_is_empty(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(base_module.httpx, "Client", FakeClient)
    FakeClient.requested_urls = []
    FakeClient.response = FakeResponse(b"")

    with pytest.raises(DatasetDownloadError) as error_info:
        ExamplePostcodesDatabase()._download_database(
            destination=tmp_path / "custom_postcodes.csv",
            timeout_seconds=1,
        )

    assert len(error_info.value.exceptions) == 1
    assert isinstance(error_info.value.exceptions[0], DatasetUnavailableError)

    FakeClient.response = FakeResponse(b"postcode,locality\n3000,MELBOURNE\n")


def test_download_database_wraps_http_errors(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(base_module.httpx, "Client", FakeClient)
    FakeClient.requested_urls = []
    FakeClient.response = FakeResponse(b"", httpx.HTTPError("boom"))

    with pytest.raises(DatasetDownloadError) as error_info:
        ExamplePostcodesDatabase()._download_database(
            destination=tmp_path / "custom_postcodes.csv",
            timeout_seconds=1,
        )

    assert error_info.value.exceptions == (FakeClient.response.error,)
    assert FakeClient.response.error is not None
    assert FakeClient.response.error.__notes__ == ["Database URL: https://example.test/data/custom_postcodes.csv"]

    FakeClient.response = FakeResponse(b"postcode,locality\n3000,MELBOURNE\n")


def test_download_database_groups_every_source_failure(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    class MultiUrlDatabase(ExamplePostcodesDatabase):
        database_urls = ("https://example.test/first.csv", "https://example.test/second.csv")

    monkeypatch.setattr(base_module.httpx, "Client", FakeClient)
    responses = {
        "https://example.test/first.csv": FakeResponse(b"", httpx.TimeoutException("too slow")),
        "https://example.test/second.csv": FakeResponse(b""),
    }

    def fake_get(self: FakeClient, source_url: str) -> FakeResponse:
        type(self).requested_urls.append(source_url)
        return responses[source_url]

    FakeClient.requested_urls = []
    monkeypatch.setattr(FakeClient, "get", fake_get)

    with pytest.raises(DatasetDownloadError) as error_info:
        MultiUrlDatabase()._download_database(
            destination=tmp_path / "custom_postcodes.csv",
            timeout_seconds=1,
        )

    assert FakeClient.requested_urls == ["https://example.test/first.csv", "https://example.test/second.csv"]
    assert isinstance(error_info.value.exceptions[0], httpx.TimeoutException)
    assert isinstance(error_info.value.exceptions[1], DatasetUnavailableError)
    assert error_info.value.exceptions[0].__notes__ == ["Database URL: https://example.test/first.csv"]


def test_download_database_tries_next_url_when_first_fails(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    class MultiUrlDatabase(ExamplePostcodesDatabase):
        database_urls = ("https://example.test/first.csv", "https://example.test/second.csv")

    monkeypatch.setattr(base_module.httpx, "Client", FakeClient)
    destination = tmp_path / "custom_postcodes.csv"

    responses = {
        "https://example.test/first.csv": FakeResponse(b"", httpx.HTTPError("boom")),
        "https://example.test/second.csv": FakeResponse(b"postcode,locality\n3000,MELBOURNE\n"),
    }

    def fake_get(self: FakeClient, source_url: str) -> FakeResponse:
        type(self).requested_urls.append(source_url)
        return responses[source_url]

    FakeClient.requested_urls = []
    monkeypatch.setattr(FakeClient, "get", fake_get)

    MultiUrlDatabase()._download_database(
        destination=destination,
        timeout_seconds=1,
    )

    assert FakeClient.requested_urls == ["https://example.test/first.csv", "https://example.test/second.csv"]
    assert destination.read_bytes() == b"postcode,locality\n3000,MELBOURNE\n"


def test_request_timeout_must_be_positive(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("matthewproctor_DATA_DIR", str(tmp_path))

    with pytest.raises(ValueError):
        ExamplePostcodesDatabase().lookup("3000", request_timeout_seconds=0)
