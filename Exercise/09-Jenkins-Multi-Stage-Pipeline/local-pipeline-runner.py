"""
Local Multi-Stage Pipeline Runner for Exercise 9.
Simulates and executes all 5 stages of the Jenkins pipeline locally:
Stage 1: BUILD - Prepare environment and check dependencies
Stage 2: TEST - Run unit tests with unittest
Stage 3: DEPLOY - Copy application to deployment directory
Stage 4: RUN APPLICATION - Start background Flask process
Stage 5: TEST APPLICATION - Verify HTTP endpoint against running server
Post Actions: Clean up process and report status
"""

import os
import sys
import shutil
import time
import subprocess
import urllib.request
import unittest

WORKSPACE = os.path.dirname(os.path.abspath(__file__))
DEPLOY_DIR = os.path.join(WORKSPACE, "python-app-deploy")

def stage_build():
    print("\n--- [STAGE 1: BUILD] ---")
    print("Preparing virtual environment and checking dependencies...")
    req_file = os.path.join(WORKSPACE, "requirements.txt")
    if os.path.exists(req_file):
        with open(req_file) as f:
            print("Dependencies listed in requirements.txt:", [line.strip() for line in f if line.strip()])
    print("Build stage completed successfully.")
    return True

def stage_test():
    print("\n--- [STAGE 2: TEST] ---")
    print("Executing unit tests via unittest discover...")
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=WORKSPACE, pattern="test_app.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if result.wasSuccessful():
        print("Test stage passed: 100% tests successful.")
        return True
    else:
        print("Test stage FAILED.")
        return False

def stage_deploy():
    print("\n--- [STAGE 3: DEPLOY] ---")
    print(f"Deploying application to: {DEPLOY_DIR}")
    os.makedirs(DEPLOY_DIR, exist_ok=True)
    src_app = os.path.join(WORKSPACE, "app.py")
    dst_app = os.path.join(DEPLOY_DIR, "app.py")
    shutil.copy2(src_app, dst_app)
    print("Deployed app.py to deployment directory.")
    return True

def stage_run_and_test_application():
    print("\n--- [STAGE 4: RUN APPLICATION & STAGE 5: TEST APPLICATION] ---")
    print("Starting Flask application process on port 5000...")
    deployed_app = os.path.join(DEPLOY_DIR, "app.py")
    log_file = open(os.path.join(DEPLOY_DIR, "app.log"), "w")

    process = subprocess.Popen(
        [sys.executable, deployed_app],
        stdout=log_file,
        stderr=log_file
    )
    print(f"Flask process started with PID {process.pid}. Waiting 2 seconds for server initialization...")
    time.sleep(2)

    try:
        url = "http://127.0.0.1:5000/"
        print(f"Pinging deployed endpoint {url}...")
        with urllib.request.urlopen(url, timeout=5) as resp:
            status = resp.status
            body = resp.read().decode('utf-8')
            print(f"Response Status: {status}")
            print(f"Response Body  : {body}")
            assert status == 200, f"Expected 200, got {status}"
            assert body == "Hello, Jenkins Multi-Stage Pipeline!", f"Unexpected body: {body}"
        print("Application live HTTP test PASSED.")
        success = True
    except Exception as e:
        print(f"Application live HTTP test FAILED: {e}")
        success = False
    finally:
        print("Terminating background application process...")
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
        log_file.close()
        print("Process terminated.")

    return success

def main():
    print("==========================================================")
    print("     JENKINS MULTI-STAGE PIPELINE: LOCAL EXECUTION        ")
    print("==========================================================")

    if not stage_build():
        print("[PIPELINE FAILED] in Build stage")
        sys.exit(1)

    if not stage_test():
        print("[PIPELINE FAILED] in Test stage")
        sys.exit(1)

    if not stage_deploy():
        print("[PIPELINE FAILED] in Deploy stage")
        sys.exit(1)

    if not stage_run_and_test_application():
        print("[PIPELINE FAILED] in Application Run/Test stage")
        sys.exit(1)

    print("\n==========================================================")
    print(" [PIPELINE SUCCESS] Pipeline completed successfully!")
    print("==========================================================")

if __name__ == '__main__':
    main()
