from fastapi.testclient import TestClient
from endpoints import app  # Replace 'main' with the filename where your app instance is defined

client = TestClient(app)

def test_get_fairest_sports():
    response = client.get("/api/fairestSports", params={"agg_level": "Sport", "gender": "M"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(isinstance(item, dict) for item in data)
    for item in data:
        assert "Sport" in item
        assert "total" in item
    print(data)

def test_get_fairest_sports_2():
    response = client.get("/api/fairestSports", params={"agg_level": "Event", "gender": "F"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(isinstance(item, dict) for item in data)
    for item in data:
        assert "Event" in item
        assert "total" in item
    print(data)

test_get_fairest_sports()
test_get_fairest_sports_2()
