import unittest
from app import app

class SecureFlaskTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_home_endpoint(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data.decode('utf-8'),
            "Hello, this is a secure Flask application running inside a Docker container!"
        )

if __name__ == '__main__':
    unittest.main()
