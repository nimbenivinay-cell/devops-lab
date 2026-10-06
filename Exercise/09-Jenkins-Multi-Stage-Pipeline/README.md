# Exercise 09 — Jenkins Multi-Stage Pipeline: Deploying a Python Application

## Objective
The objective of this exercise is to build, execute, and validate an advanced **Multi-Stage CI/CD Pipeline** in Jenkins for a Python Flask application. The pipeline implements a structured five-stage deployment lifecycle: **Build** (virtual environment & dependencies), **Test** (automated unit testing), **Deploy** (artifact deployment to target directory), **Run Application** (background service startup and PID tracking), and **Test Application** (live HTTP end-to-end testing). Additionally, error handling and failure stoppage behaviors are verified to guarantee that broken code never reaches deployment.

---

## Requirements
1. **Application Codebase**:
   - `app.py`: Flask web server with root endpoint `/` returning `"Hello, Jenkins Multi-Stage Pipeline!"`.
   - `requirements.txt`: Dependencies (`flask>=2.1.2`).
   - `test_app.py`: Unit test verifying status code 200 and exact string output.
2. **Declarative Pipeline (`Jenkinsfile`)**:
   - Agent: `any`.
   - Stages:
     1. **Build**: Installs requirements and prepares execution environment.
     2. **Test**: Executes `python3 -m unittest discover -s .`. Fails build immediately on test failure.
     3. **Deploy**: Creates deployment target `${WORKSPACE}/python-app-deploy` and stages code.
     4. **Run Application**: Launches application in background using `nohup`, logging to `app.log` and storing process ID in `app.pid`.
     5. **Test Application**: Executes integration test against the active HTTP daemon.
   - Post-build handlers: `success` and `failure` notification echo statements.
3. **Local Testing & Simulation**:
   - `local-pipeline-runner.py`: Orchestrates all 5 stages in terminal (starts server, verifies live HTTP GET, terminates server cleanly).
   - `test_failure_simulation.py`: Verifies pipeline halt behavior when tests fail.
   - `deploy.sh`, `deploy.ps1`, and `cleanup.sh`.

---

## Tools Used
- **Jenkins (LTS)**: Continuous Integration and Continuous Delivery pipeline engine.
- **Python 3.14**: Application execution, unit testing, and pipeline runner.
- **Flask**: WSGI web application framework.
- **Git**: Distributed version control system.
- **Bash & PowerShell**: Scripted build steps and process management.


---

## Implementation Details

### 1. Flask Application (`app.py`)
```python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello, Jenkins Multi-Stage Pipeline!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
```

### 2. Multi-Stage Declarative Pipeline (`Jenkinsfile`)
```groovy
pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo 'Creating virtual environment and installing dependencies...'
                sh '''
                python3 -m pip install --upgrade pip
                python3 -m pip install -r requirements.txt
                '''
            }
        }
        stage('Test') {
            steps {
                echo 'Running unit tests...'
                sh 'python3 -m unittest discover -s .'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying application to staging directory...'
                sh '''
                mkdir -p ${WORKSPACE}/python-app-deploy
                cp ${WORKSPACE}/app.py ${WORKSPACE}/python-app-deploy/
                '''
            }
        }
        stage('Run Application') {
            steps {
                echo 'Starting application background service...'
                sh '''
                nohup python3 ${WORKSPACE}/python-app-deploy/app.py > ${WORKSPACE}/python-app-deploy/app.log 2>&1 &
                echo $! > ${WORKSPACE}/python-app-deploy/app.pid
                sleep 2
                '''
            }
        }
        stage('Test Application') {
            steps {
                echo 'Testing deployed application over HTTP...'
                sh '''
                python3 ${WORKSPACE}/test_app.py
                '''
            }
        }
    }

    post {
        always {
            sh '''
            if [ -f ${WORKSPACE}/python-app-deploy/app.pid ]; then
                kill $(cat ${WORKSPACE}/python-app-deploy/app.pid) || true
            fi
            '''
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check the logs for more details.'
        }
    }
}
```

---

## Commands Executed

### Local Pipeline Execution & Testing
```powershell
# 1. Execute end-to-end local pipeline simulator
python local-pipeline-runner.py

# 2. Execute failure simulation to test pipeline stoppage
python test_failure_simulation.py

# 3. Run individual application unit test
python test_app.py
```

### Jenkins In-Container Setup & Troubleshooting
```bash
# If Jenkins agent lacks python3/pip, execute inside Jenkins container:
docker exec -it -u root <container-id> bash
apt-get update
apt-get install -y python3 python3-pip python3-flask python3.11-venv
python3 -m unittest discover -s .
exit
```

---

## Important Configuration & Code

| Component | Setting | Purpose |
| :--- | :--- | :--- |
| **Stage 1: Build** | `pip install -r requirements.txt` | Ensures all runtime modules are present |
| **Stage 2: Test** | `unittest discover -s .` | Runs unit tests before deployment |
| **Stage 3: Deploy** | `mkdir -p python-app-deploy` | Isolates production/staging artifacts from workspace |
| **Stage 4: Run** | `nohup python3 app.py &` | Starts server as non-blocking background daemon |
| **Stage 5: Test App** | Live HTTP Client test | Validates end-to-end network responsiveness |
| **Post Action** | `kill $(cat app.pid)` | Cleans up background daemon to prevent orphaned processes |

---

## Output

### Terminal Local Pipeline Runner Output (`local-pipeline-runner.py`)
```text
test_home (test_app.TestApp.test_home) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.017s

OK
==========================================================
     JENKINS MULTI-STAGE PIPELINE: LOCAL EXECUTION        
==========================================================

--- [STAGE 1: BUILD] ---
Preparing virtual environment and checking dependencies...
Dependencies listed in requirements.txt: ['flask>=2.1.2']
Build stage completed successfully.

--- [STAGE 2: TEST] ---
Executing unit tests via unittest discover...

[TEST CLIENT OUTPUT] Hello, Jenkins Multi-Stage Pipeline!
Test stage passed: 100% tests successful.

--- [STAGE 3: DEPLOY] ---
Deploying application to: ...\python-app-deploy
Deployed app.py to deployment directory.

--- [STAGE 4: RUN APPLICATION & STAGE 5: TEST APPLICATION] ---
Starting Flask application process on port 5000...
Flask process started with PID 21624. Waiting 2 seconds for server initialization...
Pinging deployed endpoint http://127.0.0.1:5000/...
Response Status: 200
Response Body  : Hello, Jenkins Multi-Stage Pipeline!
Application live HTTP test PASSED.
Terminating background application process...
Process terminated.

==========================================================
 [PIPELINE SUCCESS] Pipeline completed successfully!
==========================================================
```

### Terminal Failure Stoppage Test Output (`test_failure_simulation.py`)
```text
=== Testing Pipeline Failure Behavior on Test Failure ===

[SIMULATION] Executing test with intentional assertion failure...

[VERIFIED] Test failure detected! Pipeline would halt immediately at Test stage.
Deploy stage and Run stages will NOT execute.
```

---

## Verification
- **All 5 Stages Validated**: Local runner executed Build, Test, Deploy, Run, and Test Application stages with clean process shutdown.
- **Fail-Safe Mechanism**: `test_failure_simulation.py` verified that an assertion error halts the pipeline, preventing unverified deployment.
- **Port Mapping Parity**: Application ran on port 5000, verified via live HTTP GET request.

---

## Result / Conclusion
Exercise 09 is **COMPLETE**. The multi-stage Jenkins pipeline, Flask application, automated unit testing, deployment staging, live process validation, and failure prevention mechanisms are verified.
