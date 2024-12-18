import unittest
import json



from app import app  # Import the Flask app from your file

class TestFlaskApp(unittest.TestCase):
    def setUp(self):
        # Set up the Flask test client
        self.app = app.test_client()
        self.app.testing = True

    def test_get_data(self):
        # Send a GET request to the '/data' endpoint
        response = self.app.get('/data')
        self.assertEqual(response.status_code, 200)  # Check status code

        # Parse the JSON response
        data = json.loads(response.data)

        # Check if the response contains the expected keys
        self.assertIn("array", data)
        self.assertIn("number", data)
        self.assertIn("timestamp", data)
        self.assertIn("dataframe", data)

        # Validate the content
        self.assertEqual(data["array"], [1, 2, 3])
        self.assertEqual(data["number"], 42.42)
        self.assertEqual(data["timestamp"], "2023-12-18T10:00:00")
        self.assertEqual(data["dataframe"], [{"A": 1, "B": 3}, {"A": 2, "B": 4}])

if __name__ == '__main__':
    unittest.main()
