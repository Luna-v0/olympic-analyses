import json

from fastapi.testclient import TestClient
from endpoints import app  # Replace 'main' with the filename where your app instance is defined

client = TestClient(app)

def test_get_fairest_sports():
    response = client.get("/api/fairestSports", params={"agg_level": "Sport", "gender": "M", "names": ["Football", "Basketball"],
})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(isinstance(item, dict) for item in data)
    for item in data:
        assert "Name" in item
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

def test_get_features_sport():
    response = client.get(
        "/api/getFeatures",
        params={
            "agg_level": "Sport",
            "names": ["Football", "Basketball"],
            "gender": "M"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list), "Response data should be a list"
    assert all(isinstance(item, dict) for item in data), "Each item in data should be a dict"
    for item in data:
        assert "Sport" in item, "Each item should contain 'Sport' key"
        # You can add more assertions here based on the expected keys in the item
    print(data)

def test_get_names_sport():
    response = client.get(
        "/api/getNames",
        params={
            "agg_level": "Sport",
            "gender": "M"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list), "Response data should be a list"
    assert all(isinstance(item, str) for item in data), "Each item in the response should be a string"
    print(data)


def test_get_sports_for_user():
    user_data = {
        "Height": 173,
        "Weight": 103,
        "Age": 24,
        "Sex": "M",
        "NOC": "BRA"
    }

    response = client.get(
        "/api/getSportsForUser",
        params={
            "_user_data": json.dumps(user_data),
            "agg_level": "Sport"  # Replace with the actual agg_level in your dataset
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list), "Response should be a list of dictionaries"
    assert all(isinstance(item, dict) for item in data), "Each item in the response should be a dictionary"
    for item in data:
        assert "Sport" in item or "Event" in item, "Each item should contain the aggregation level key"
        assert "Distance" in item, "Each item should contain a 'Distance' key"
    print(data)

def test_get_sports_distance():
    response = client.get(
        "/api/getSportsDistance",
        params={
            "agg_level": "Sport",
            "sex": "M",
            "features": ["Height", "BMI", "Age", "GDP"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list), "Response should be a list of dictionaries"
    assert all(isinstance(item, dict) for item in data), "Each item in the response should be a dictionary"
    for item in data:
        assert f"Sport_1" in item or f"Event_1" in item, "Each item should contain the first aggregation level key"
        assert f"Sport_2" in item or f"Event_2" in item, "Each item should contain the second aggregation level key"
        assert "Distance" in item, "Each item should contain a 'Distance' key"
        assert isinstance(item["Distance"], float), "Distance should be a float value"
    print(data)


def test_get_time_tendencies():
    # Define parameters for the request
    params = {
        "isSportsOrEvents": "sports",  # Replace with a valid value
        "feature": "Height",  # Replace with a valid feature
        "sportsOrEvents": ["Football", "Basketball"]  # Replace with valid sports/events
    }

    # Send GET request with parameters
    response = client.get("/api/timeTendencies", params=params)

    # Assertions to verify the response
    assert response.status_code == 200, "Expected status code 200"
    data = response.json()
    assert isinstance(data, list), "Response data should be a list"
    assert all(isinstance(item, dict) for item in data), "Each item in the response should be a dictionary"

    # Validate that expected keys are present in each item
    for item in data:
        assert "date" in item, "Each item should contain 'Time' key"
        assert "lines" in item, "Each item should contain 'Value' key"

    # Print the data for debugging
    print(data)


# Run the test
test_get_time_tendencies()
# test_get_fairest_sports()
# test_get_fairest_sports_2()
# test_get_features_sport()
# test_get_names_sport()
# test_get_sports_for_user()
# test_get_sports_distance()