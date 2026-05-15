def test_full_flow(client):

    response = client.post(
        "/search",
        data={"use_saved": "true"}
    )

    assert response.status_code == 200

    response = client.post("/save/1")

    assert response.status_code == 200

    response = client.post("/delete/1")

    assert response.status_code == 200