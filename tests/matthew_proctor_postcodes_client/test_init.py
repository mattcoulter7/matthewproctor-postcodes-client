import matthew_proctor_postcodes_client as package


def test_package_exports_public_api() -> None:
    assert "AUSMatthewProctorPostcodesClient" in package.__all__
    assert "NZLMatthewProctorPostcodesClient" in package.__all__
    assert "MatthewProctorDatabaseType" in package.__all__
    assert "normalize_postcode" in package.__all__
    assert "create_client" not in package.__all__
    assert "normalize_country" not in package.__all__
    assert "DATABASE_FILENAMES" not in package.__all__
    assert "DATABASE_URLS" not in package.__all__
