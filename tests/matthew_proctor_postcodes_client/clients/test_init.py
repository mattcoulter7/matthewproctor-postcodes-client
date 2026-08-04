import matthew_proctor_postcodes_client.clients as clients


def test_clients_exports_public_client_types() -> None:
    assert "AUSMatthewProctorPostcodesClient" in clients.__all__
    assert "MatthewProctorPostcodesClient" in clients.__all__
    assert "NZLMatthewProctorPostcodesClient" in clients.__all__
    assert "create_client" not in clients.__all__
