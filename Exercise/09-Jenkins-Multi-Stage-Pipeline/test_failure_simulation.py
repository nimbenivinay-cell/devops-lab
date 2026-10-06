"""
Test Failure Simulation for Exercise 9.
Validates requirement: "Ensure a failed test causes the pipeline to fail."
"""

import sys
import unittest

class FailingTestCase(unittest.TestCase):
    def test_intentional_failure(self):
        print("\n[SIMULATION] Executing test with intentional assertion failure...")
        self.assertEqual("Actual Result", "Expected Result", "Intentional failure to test CI pipeline stoppage")

def run_failing_pipeline():
    print("=== Testing Pipeline Failure Behavior on Test Failure ===")
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(FailingTestCase)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if not result.wasSuccessful():
        print("\n[VERIFIED] Test failure detected! Pipeline would halt immediately at Test stage.")
        print("Deploy stage and Run stages will NOT execute.")
        return 0
    else:
        print("[ERROR] Test unexpectedly passed.")
        return 1

if __name__ == '__main__':
    sys.exit(run_failing_pipeline())
