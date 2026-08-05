import pytest

import matthewproctor_postcodes.lookup as package
from matthewproctor_postcodes.exceptions import UnsupportedCountryError
from matthewproctor_postcodes.models import MatthewProctorDatabaseType


class RecordingDatabase:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def lookup(
        self,
        postcode: str,
        *,
        request_timeout_seconds: float = 30.0,
        download_if_missing: bool = True,
    ) -> list[dict[str, object]]:
        self.calls.append(
            {
                "postcode": postcode,
                "request_timeout_seconds": request_timeout_seconds,
                "download_if_missing": download_if_missing,
            }
        )
        return [{"postcode": postcode}]


def test_lookup_postcode_routes_to_normalized_country(monkeypatch: pytest.MonkeyPatch) -> None:
    database = RecordingDatabase()
    monkeypatch.setattr(package, "_DATABASES_INDEX", {MatthewProctorDatabaseType.AUS: database})

    assert package.lookup_postcode("3000", " aus ") == [{"postcode": "3000"}]
    assert database.calls == [
        {
            "postcode": "3000",
            "request_timeout_seconds": 30.0,
            "download_if_missing": True,
        }
    ]


def test_lookup_postcode_forwards_lifecycle_options(monkeypatch: pytest.MonkeyPatch) -> None:
    database = RecordingDatabase()
    monkeypatch.setattr(package, "_DATABASES_INDEX", {MatthewProctorDatabaseType.NZL: database})

    package.lookup_postcode(
        "110",
        "NZL",
        request_timeout_seconds=10.0,
        download_if_missing=False,
    )

    assert database.calls == [
        {
            "postcode": "110",
            "request_timeout_seconds": 10.0,
            "download_if_missing": False,
        }
    ]


def test_lookup_postcode_rejects_unsupported_country() -> None:
    with pytest.raises(UnsupportedCountryError):
        package.lookup_postcode("3000", "USA")
