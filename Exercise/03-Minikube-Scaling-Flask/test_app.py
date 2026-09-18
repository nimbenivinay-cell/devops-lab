import unittest
from app import app

class FlashSaleAppTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get("message"), "Welcome to Big Sale!")
        self.assertIn("pod", data)
        self.assertIn("ts", data)

    def test_buy_endpoint(self):
        response = self.client.get('/buy?user=customer99')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get("status"), "success")
        self.assertEqual(data.get("user"), "customer99")
        self.assertIn(data.get("item"), ["Smartphone", "Shoes", "Headphones", "Laptop"])
        self.assertIn("served_by_pod", data)

    def test_health_endpoint(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get("status"), "healthy")
        self.assertIn("pod", data)

if __name__ == '__main__':
    unittest.main()
