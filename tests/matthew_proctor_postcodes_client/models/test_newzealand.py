from typing import get_type_hints

from matthew_proctor_postcodes_client import NZLMatthewProctorPostcodeInfo


def test_new_zealand_model_uses_source_csv_headers() -> None:
    hints = get_type_hints(NZLMatthewProctorPostcodeInfo)

    assert set(hints) >= {
        "postcode",
        "locality",
        "region",
        "long",
        "lat",
        "territory",
        "island",
    }
    assert "longitude" not in hints
    assert "latitude" not in hints
