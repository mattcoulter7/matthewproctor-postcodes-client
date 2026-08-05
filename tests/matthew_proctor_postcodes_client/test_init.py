import matthew_proctor_postcodes_client as package


def test_package_exports_public_api() -> None:
    assert package.__all__ == [
        "AUSMatthewProctorPostcodeInfo",
        "MatthewProctorPostcodeInfo",
        "NZLMatthewProctorPostcodeInfo",
        "lookup_postcode",
    ]
    assert "AUSMatthewProctorPostcodesClient" not in package.__all__
    assert "NZLMatthewProctorPostcodesClient" not in package.__all__
    assert "MatthewProctorDatabaseType" not in package.__all__
    assert "create_client" not in package.__all__
    assert "normalize_country" not in package.__all__
    assert "DATABASE_FILENAMES" not in package.__all__
    assert "DATABASE_URLS" not in package.__all__
