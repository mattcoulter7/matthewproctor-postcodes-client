import matthewproctor_postcodes as package


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


def test_package_does_not_export_database_objects() -> None:
    assert "AUSMatthewProctorPostcodesDatabase" not in package.__all__
    assert "MatthewProctorPostcodesDatabase" not in package.__all__
    assert "NZLMatthewProctorPostcodesDatabase" not in package.__all__
    assert "_DATABASES" not in package.__all__
