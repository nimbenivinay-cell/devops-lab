# Exercise 08 — Creating "Hello World" Jenkins Freestyle Job

## Objective
The objective of this exercise is to configure and execute a foundational **Freestyle Project** in Jenkins. The workflow demonstrates integrating a Git source code repository, creating an executable build script (`hello-world.sh` / `hello-world.ps1`), authoring declarative Jenkins job configurations (`job-config.xml`), triggering manual builds, and analyzing the resulting console logs and execution artifacts.

---

## Requirements
1. **Build Scripts**:
   - `hello-world.sh`: Executable bash script printing `"Hello, Jenkins!"`.
   - `hello-world.ps1`: Windows PowerShell alternative printing `"Hello, Jenkins!"`.
2. **Jenkins Job Configuration**:
   - Project Name: `HelloWorld`.
   - Project Type: **Freestyle Project**.
   - Build Step: Execute shell (`sh hello-world.sh`).
   - Declarative `job-config.xml`: XML schema defining description, SCM, builders, and publishers.
   - Declarative `Jenkinsfile`: Pipeline alternative for pipeline-as-code environments.
3. **Automated Verification**:
   - `test_script.py`: Python unit test verifying script existence, execution permissions, output matching, and exit codes.

---

## Tools Used
- **Jenkins (LTS)**: Automation server for freestyle job orchestration.
- **Git & GitHub**: Version control system and remote repository hosting.
- **Bash / Shell**: Script execution runtime on Linux build agents.
- **PowerShell**: Script execution runtime on Windows agents.
- **Python 3.14**: Test validation and cross-platform verification.

## Implementation Details

### 1. Shell Script (`hello-world.sh`)
```bash
#!/bin/bash
echo "Hello, Jenkins!"
```

### 2. PowerShell Script (`hello-world.ps1`)
```powershell
Write-Output "Hello, Jenkins!"
```

### 3. Declarative Jenkins Job XML (`job-config.xml`)
```xml
<?xml version='1.1' encoding='UTF-8'?>
<project>
  <actions/>
  <description>Hello World! Jenkins freestyle job demonstrating script execution.</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <scm class="hudson.plugins.git.GitSCM" plugin="git@5.2.1">
    <configVersion>2</configVersion>
    <userRemoteConfigs>
      <hudson.plugins.git.UserRemoteConfig>
        <url>https://github.com/urmsandeep/devops-sample-code.git</url>
      </hudson.plugins.git.UserRemoteConfig>
    </userRemoteConfigs>
    <branches>
      <hudson.plugins.git.BranchSpec>
        <name>*/main</name>
      </hudson.plugins.git.BranchSpec>
    </branches>
  </scm>
  <builders>
    <hudson.tasks.Shell>
      <command>sh hello-world.sh</command>
    </hudson.tasks.Shell>
  </builders>
  <publishers/>
</project>
```

### 4. Declarative Pipeline Alternative (`Jenkinsfile`)
```groovy
pipeline {
    agent any
    stages {
        stage('Execute Hello World') {
            steps {
                sh 'sh hello-world.sh'
            }
        }
    }
}
```

---

## Commands Executed

### Local Script & Unit Test Verification
```powershell
# 1. Execute script via PowerShell
powershell -ExecutionPolicy Bypass -File .\hello-world.ps1

# 2. Run automated test suite
python test_script.py

# 3. Inspect XML configuration
Get-Content .\job-config.xml
```

### Jenkins Web UI & CLI Workflow
```bash
# 1. Access Jenkins Web Console at http://localhost:8080
# 2. Navigate to: New Item -> Project Name: 'HelloWorld' -> Select 'Freestyle project'
# 3. Under 'Build Steps', select: 'Execute shell'
# 4. Enter command: sh hello-world.sh
# 5. Click 'Save' and 'Build Now'
# 6. Check 'Console Output' under Build #1
```

---

## Important Configuration & Code

| Component | Setting | Purpose |
| :--- | :--- | :--- |
| **Project Type** | Freestyle Project | Basic single-step automated task runner in Jenkins |
| **Execution Script** | `sh hello-world.sh` | Shell interpreter invocation in build container |
| **Exit Code** | `0` (Success) | Jenkins marks build as SUCCESS only when command exits with code 0 |
| **Unit Test** | `test_script.py` | Validates script execution, stdout capture, and error handling |

---

## Output

### Terminal Test Output (`test_script.py`)
```text
Hello, Jenkins!
..
----------------------------------------------------------------------
Ran 2 tests in 0.399s

OK
```

### Expected Jenkins Console Output (Build #1)
```text
Started by user Admin
Building in workspace /var/jenkins_home/workspace/HelloWorld
[HelloWorld] $ /bin/sh -xe /tmp/jenkins1281930102.sh
+ echo 'Hello, Jenkins!'
Hello, Jenkins!
Finished: SUCCESS
```

---

## Verification
- **Output Exact Match**: Script execution produces exact string `"Hello, Jenkins!"` followed by a newline.
- **Cross-Platform Compatibility**: Provided both Bash (`.sh`) for POSIX Jenkins agents and PowerShell (`.ps1`) for Windows worker nodes.
- **XML Schema Conformance**: `job-config.xml` conforms to standard Jenkins Freestyle configuration XML.

---

## Result / Conclusion
Exercise 08 is **COMPLETE**. The shell scripts, PowerShell alternatives, Jenkins freestyle job configuration, and automated tests are fully implemented and verified.
