from typing import get_type_hints

from matthew_proctor_postcodes_client import AUSMatthewProctorPostcodeInfo


def test_australian_model_uses_source_csv_headers() -> None:
    hints = get_type_hints(AUSMatthewProctorPostcodeInfo)

    assert "postcode" in hints
    assert "long" in hints
    assert "lat" in hints
    assert "RA_2021_NAME" in hints
    assert "distribution_centre" not in hints
    assert "ra_2021_name" not in hints
