
def test_homepage(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "Developer Intelligence" in response.get_data(as_text=True)
    assert response.mimetype == "text/html"


def test_unknown_route(client):
    response = client.get("/this-route-does-not-exist")

    assert response.status_code == 404