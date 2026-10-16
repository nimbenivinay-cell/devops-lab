import unittest
import json
from product_catalog import app as catalog_app
from shopping_cart import app as cart_app

class MultiAppTestCase(unittest.TestCase):
    def test_product_catalog(self):
        client = catalog_app.test_client()
        response = client.get('/products')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]['name'], 'Laptop')
        self.assertEqual(data[0]['price'], 1200)

    def test_shopping_cart(self):
        client = cart_app.test_client()
        # Initial empty cart
        get_res = client.get('/cart')
        self.assertEqual(get_res.status_code, 200)
        cart = get_res.get_json()
        self.assertIsInstance(cart, list)

        # Add item
        post_res = client.post(
            '/cart',
            data=json.dumps({"id": 1, "name": "Laptop", "quantity": 1}),
            content_type='application/json'
        )
        self.assertEqual(post_res.status_code, 201)
        updated_cart = post_res.get_json()
        self.assertGreaterEqual(len(updated_cart), 1)
        self.assertEqual(updated_cart[-1]['name'], 'Laptop')

if __name__ == '__main__':
    unittest.main()
