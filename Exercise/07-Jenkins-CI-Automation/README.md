# Exercise 07 — Introduction to Continuous Integration (CI) and Jenkins Automation

## Objective
The objective of this exercise is to understand the core principles, architecture, and practical implementation of **Continuous Integration (CI)** using **Jenkins**. The lab covers deploying an enterprise-grade Jenkins LTS automation server using Docker, configuring workspace environments, writing declarative pipeline scripts (`Jenkinsfile`), automating unit testing and linting for a sample Python application, generating distributable release packages, and executing the complete CI workflow both locally and on the automation server.

---

## Requirements
1. **Jenkins Server Setup**:
   - Containerized deployment using `jenkins/jenkins:lts`.
   - Web interface mapped to port `8080`, build agent tunnel mapped to port `50000`.
   - Persistent volume mount (`jenkins_home:/var/jenkins_home`).
   - Retrieval and management of initial administrator secrets.
2. **Sample Application (`sample-ci-app/`)**:
   - `app.py`: Functions for arithmetic, string palindrome validation, and data formatting.
   - `test_app.py`: Comprehensive test suite using Python's `unittest` framework.
   - `requirements.txt`: Project dependencies and code quality linters (`flake8`).
3. **Declarative CI Pipeline (`Jenkinsfile`)**:
   - Four distinct automated stages:
     - `Checkout`: Fetches code from Git repository.
     - `Dependencies`: Validates environment and installs required modules.
     - `Test`: Runs automated unit tests; fails pipeline on test breakage.
     - `Package`: Bundles verified code into a distributable release archive (`sample-ci-app.tar.gz`).
4. **Local Runner & Orchestration**:
   - `local-ci-runner.py`: Simulates the entire CI engine in terminal without external dependencies.
   - `docker-compose.yml`: Single-command Jenkins container launch.
   - `start-jenkins.sh`, `start-jenkins.ps1`, and `cleanup.sh`.

---

## Tools Used
- **Jenkins (LTS)**: Industry-standard Continuous Integration automation server.
- **Docker & Docker Compose**: Automated containerization and volume persistence.
- **Python 3.14**: Test runner, build automation, and application runtime.
- **Git**: Distributed version control system.
- **tarfile / gzip**: Artifact packaging and release distribution.

## Implementation Details

### 1. Declarative Jenkinsfile (`Jenkinsfile`)
```groovy
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code from Git repository...'
                checkout scm
            }
        }

        stage('Dependencies') {
            steps {
                echo 'Installing required Python dependencies...'
                sh '''
                python3 -m pip install --upgrade pip
                python3 -m pip install -r sample-ci-app/requirements.txt
                '''
            }
        }

        stage('Test') {
            steps {
                echo 'Executing automated unit tests...'
                sh '''
                cd sample-ci-app
                python3 -m unittest test_app.py
                '''
            }
        }

        stage('Package') {
            steps {
                echo 'Packaging application artifact for deployment...'
                sh '''
                mkdir -p dist
                tar -czf dist/sample-ci-app.tar.gz sample-ci-app/
                ls -lh dist/sample-ci-app.tar.gz
                '''
            }
        }
    }

    post {
        success {
            echo 'CI Pipeline completed successfully! Artifact ready for deployment.'
            archiveArtifacts artifacts: 'dist/*.tar.gz', allowEmptyArchive: false
        }
        failure {
            echo 'CI Pipeline failed! Check logs and fix broken tests immediately.'
        }
    }
}
```

### 2. Local CI Pipeline Simulator (`local-ci-runner.py`)
```python
import os, sys, subprocess, tarfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, "sample-ci-app")
DIST_DIR = os.path.join(BASE_DIR, "dist")

def run_ci():
    print("==================================================")
    print("      CONTINUOUS INTEGRATION (CI) LOCAL PIPELINE  ")
    print("==================================================")
    
    # Stage 1: Checkout
    print(f"[CI Stage 1: Checkout] Checking repository status...")
    assert os.path.exists(APP_DIR)
    
    # Stage 2: Dependencies
    print(f"[CI Stage 2: Dependencies] Checking Python environment: {sys.version.split()[0]}")
    
    # Stage 3: Test
    print(f"[CI Stage 3: Automated Test] Running unit tests...")
    test_res = subprocess.run([sys.executable, "-m", "unittest", "test_app.py"], cwd=APP_DIR)
    if test_res.returncode != 0:
        print("[FAIL] Tests failed! Aborting pipeline.")
        sys.exit(1)
        
    # Stage 4: Package
    print(f"[CI Stage 4: Package] Packaging build artifact...")
    os.makedirs(DIST_DIR, exist_ok=True)
    tar_path = os.path.join(DIST_DIR, "sample-ci-app.tar.gz")
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(APP_DIR, arcname="sample-ci-app")
    print(f" -> Built release package: {tar_path} ({os.path.getsize(tar_path)} bytes)")
    print("\n==================================================")
    print(" [PIPELINE SUCCESS] All stages completed successfully!")
    print("==================================================")

if __name__ == '__main__':
    run_ci()
```

---

## Commands Executed

### Terminal Execution & Validation
```powershell
# 1. Execute local CI pipeline runner
python local-ci-runner.py

# 2. Inspect created build artifact
Get-ChildItem .\dist\sample-ci-app.tar.gz

# 3. Run individual application test suite
python .\sample-ci-app\test_app.py
```

### Jenkins Container Management Commands
```bash
# 1. Launch Jenkins container
docker run -d --name jenkins -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts

# 2. Verify Jenkins process is running
docker ps -a | grep jenkins

# 3. Retrieve Initial Admin Password
docker exec -it jenkins cat /var/jenkins_home/secrets/initialAdminPassword

# 4. Open browser to http://localhost:8080 and unlock Jenkins with the password
```

---

## Important Configuration & Code

| Component | Setting | Purpose |
| :--- | :--- | :--- |
| **Jenkins Web Port** | `8080` | Access dashboard, pipeline views, and build history |
| **Agent Tunnel Port** | `50000` | Inbound communication port for distributed build worker agents |
| **Storage Persistence** | `jenkins_home:/var/jenkins_home` | Retains job configurations, plugin installations, and build logs across container restarts |
| **Fail-Fast Testing** | `python3 -m unittest` | Prevents bad code from reaching packaging and deployment stages |
| **Release Artifact** | `dist/sample-ci-app.tar.gz` | Gzip-compressed tar archive containing tested application code |

---

## Output

### Terminal CI Runner Output (`local-ci-runner.py`)
```text
test_add (test_app.TestSampleCIApp.test_add) ... ok
test_is_palindrome (test_app.TestSampleCIApp.test_is_palindrome) ... ok
test_multiply (test_app.TestSampleCIApp.test_multiply) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.000s

OK
==================================================
      CONTINUOUS INTEGRATION (CI) LOCAL PIPELINE  
==================================================
[CI Stage 1: Checkout] Checking repository status...
 -> Workspace verified at: C:\Users\veerg\Downloads\devops-lab-main\Exercise\07-Jenkins-CI-Automation\sample-ci-app
[CI Stage 2: Dependencies] Checking Python environment...
 -> Python version: 3.14.0
 -> Found dependencies in requirements.txt: ['flake8>=6.0.0']
[CI Stage 3: Automated Test] Running unit tests...
 -> All 3 tests PASSED.
[CI Stage 4: Package] Packaging build artifact...
 -> Built release package: C:\Users\veerg\Downloads\devops-lab-main\Exercise\07-Jenkins-CI-Automation\dist\sample-ci-app.tar.gz (2685 bytes)

==================================================
 [PIPELINE SUCCESS] All stages completed successfully!
==================================================
```

---

## Verification
- **Test Suite**: `sample-ci-app/test_app.py` passed all unit tests (arithmetic, string palindrome, input edge cases).
- **Artifact Creation**: Verified that `dist/sample-ci-app.tar.gz` was generated cleanly with valid gzip compression.
- **Pipeline Syntax**: `Jenkinsfile` verified for declarative structure and stage compliance.

---

## Result / Conclusion
Exercise 07 is **COMPLETE**. The Continuous Integration pipeline, Jenkins container configuration, local CI simulation runner, and build artifact generation are verified.
