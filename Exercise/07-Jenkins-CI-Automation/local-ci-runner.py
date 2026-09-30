"""
Local CI Workflow Simulator and Runner for Exercise 7.
Simulates each stage of the Jenkins CI pipeline:
1. Checkout simulation
2. Dependency verification
3. Automated test execution (unittest)
4. Build & Package (creates distribution tarball)
5. Feedback reporting
"""

import os
import sys
import subprocess
import tarfile
import unittest

def stage_checkout():
    print("[CI Stage 1: Checkout] Checking repository status...")
    app_dir = os.path.join(os.path.dirname(__file__), "sample-ci-app")
    if os.path.exists(app_dir):
        print(f" -> Workspace verified at: {app_dir}")
        return True
    print(" -> [ERROR] Application directory not found!")
    return False

def stage_dependencies():
    print("[CI Stage 2: Dependencies] Checking Python environment...")
    print(f" -> Python version: {sys.version.split()[0]}")
    req_file = os.path.join(os.path.dirname(__file__), "sample-ci-app", "requirements.txt")
    if os.path.exists(req_file):
        with open(req_file, 'r') as f:
            deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        print(f" -> Found dependencies in requirements.txt: {deps}")
    return True

def stage_test():
    print("[CI Stage 3: Automated Test] Running unit tests...")
    app_dir = os.path.join(os.path.dirname(__file__), "sample-ci-app")
    sys.path.insert(0, app_dir)

    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=app_dir, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if result.wasSuccessful():
        print(f" -> All {result.testsRun} tests PASSED.")
        return True
    else:
        print(f" -> [FAILURE] {len(result.failures)} failures, {len(result.errors)} errors encountered.")
        return False

def stage_package():
    print("[CI Stage 4: Package] Packaging build artifact...")
    dist_dir = os.path.join(os.path.dirname(__file__), "dist")
    os.makedirs(dist_dir, exist_ok=True)
    archive_path = os.path.join(dist_dir, "sample-ci-app.tar.gz")
    app_dir = os.path.join(os.path.dirname(__file__), "sample-ci-app")

    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(app_dir, arcname="sample-ci-app")

    print(f" -> Built release package: {archive_path} ({os.path.getsize(archive_path)} bytes)")
    return True

def main():
    print("==================================================")
    print("      CONTINUOUS INTEGRATION (CI) LOCAL PIPELINE  ")
    print("==================================================")

    stages = [
        ("Checkout", stage_checkout),
        ("Dependencies", stage_dependencies),
        ("Test", stage_test),
        ("Package", stage_package)
    ]

    for name, func in stages:
        success = func()
        if not success:
            print(f"\n[PIPELINE FAILED] Stage '{name}' did not succeed. Halting build.")
            sys.exit(1)

    print("\n==================================================")
    print(" [PIPELINE SUCCESS] All stages completed successfully!")
    print("==================================================")

if __name__ == '__main__':
    main()
