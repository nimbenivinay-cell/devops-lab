import unittest
import threading
import time
import urllib.request
import re
from prometheus_client import start_http_server
from delivery_metrics import simulate_delivery

class DeliveryMetricsTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start the Prometheus HTTP server on test port 8008 to avoid conflicts
        try:
            start_http_server(8008, addr="127.0.0.1")
        except Exception:
            pass
        # Run simulation once
        simulate_delivery()
        time.sleep(0.5)

    def test_metrics_endpoint(self):
        url = "http://127.0.0.1:8008/metrics"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=3) as response:
            self.assertEqual(response.status, 200)
            content = response.read().decode('utf-8')

            # Verify presence of custom metrics
            self.assertIn("total_deliveries", content)
            self.assertIn("pending_deliveries", content)
            self.assertIn("on_the_way_deliveries", content)
            self.assertIn("average_delivery_time", content)

            # Check that total_deliveries is a number
            match = re.search(r'total_deliveries\s+([0-9.]+)', content)
            self.assertIsNotNone(match, "total_deliveries metric value not found")
            val = float(match.group(1))
            self.assertGreater(val, 0)
            print(f"\n[TEST SUCCESS] Found total_deliveries = {val}")

if __name__ == '__main__':
    unittest.main()
