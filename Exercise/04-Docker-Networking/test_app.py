import unittest
from app import app

class DockerNetworkingAppTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_about_endpoint(self):
        response = self.client.get('/about')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get("name"), "Simple REST API")
        self.assertEqual(data.get("version"), "1.0")
        self.assertEqual(data.get("description"), "This is a simple REST API built with Flask.")

    def test_health_endpoint(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get("status"), "healthy")

if __name__ == '__main__':
    unittest.main()
