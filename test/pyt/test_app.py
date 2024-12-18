import json
import pytest
from app import app  # Import the Flask app from your file

@pytest.fixture
def client():
    # Set up the Flask test client
    app.testing = True
    with app.test_client() as client:
        yield client

def test_get_data(client):
    # Send a GET request to the '/data' endpoint
    response = client.get('/data')
    assert response.status_code == 200  # Check status code

    # Parse the JSON response
    data = json.loads(response.data)

    # Check if the response contains the expected keys
    assert "array" in data
    assert "number" in data
    assert "timestamp" in data
    assert "dataframe" in data

    # Validate the content
    assert data["array"] == [1, 2, 3]
    assert data["number"] == 42.42
    assert data["timestamp"] == "2023-12-18T10:00:00"
    assert data["dataframe"] == [{"A": 1, "B": 3}, {"A": 2, "B": 4}]
