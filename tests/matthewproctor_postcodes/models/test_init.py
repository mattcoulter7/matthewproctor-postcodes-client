import matthewproctor_postcodes.models as models


def test_models_exports_public_types() -> None:
    assert "AUSMatthewProctorPostcodeInfo" in models.__all__
    assert "MatthewProctorDatabaseType" in models.__all__
    assert "MatthewProctorPostcodeInfo" in models.__all__
    assert "NZLMatthewProctorPostcodeInfo" in models.__all__
    assert "MatthewProctorPostcodeEntry" not in models.__all__
