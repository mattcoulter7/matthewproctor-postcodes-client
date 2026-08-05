import matthewproctor_postcodes.databases as databases


def test_databases_exports_database_types() -> None:
    assert "AUSMatthewProctorPostcodesDatabase" in databases.__all__
    assert "MatthewProctorPostcodesDatabase" in databases.__all__
    assert "NZLMatthewProctorPostcodesDatabase" in databases.__all__
    assert "AUSMatthewProctorPostcodesClient" not in databases.__all__
