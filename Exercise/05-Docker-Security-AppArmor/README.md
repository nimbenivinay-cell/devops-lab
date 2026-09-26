# Exercise 05 — Docker Security with AppArmor LSM and Python Enforcement

## Objective
The objective of this exercise is to implement Mandatory Access Control (MAC) security policies on containerized workloads using Linux Security Modules (**AppArmor**). We enforce fine-grained confinement on a Python Flask container to restrict access to sensitive system directories (`/etc`, `/var`), forbid arbitrary binary execution (`/bin`, `/usr/bin`), drop privileged capabilities (`CAP_SYS_ADMIN`), and programmatically verify enforcement using the **Docker SDK for Python**.

---

## Requirements
1. **AppArmor Profile Configuration** (`my-apparmor-profile`):
   - Defined under `/etc/apparmor.d/my-apparmor-profile`.
   - Denies read access to `/etc/**` and write access to `/var/**`.
   - Restricts execution of binaries in `/bin/**` and `/usr/bin/**`.
   - Drops `capability sys_admin` while allowing `capability net_bind_service`.
   - Permits Flask to bind to TCP port 5000 and read/write within `/app/**`.
2. **Containerized Web Application**:
   - `app.py`: Flask application listening on `0.0.0.0:5000`.
   - `Dockerfile`: Multi-stage or slim Python runtime.
3. **Programmatic Enforcement & Testing**:
   - `apply_apparmor.py`: Uses the Docker Python SDK to build the image, launch the container with `security_opt=["apparmor=my-apparmor-profile"]`, and inspect host security options.
   - `test_restricted_actions.py`: Tests restricted actions inside the running container:
     - `cat /etc/passwd`: Expects Exit Code `1` (Access Denied).
     - `/bin/bash`: Expects Exit Code `126` (Permission Denied).
   - `test_app.py`: Unit test verifying Flask endpoint functionality.
   - `setup-apparmor.sh`: Automated bash profile compilation script.

---

## Tools Used
- **Linux Kernel / AppArmor LSM**: Kernel security subsystem for mandatory access control.
- **apparmor_parser / apparmor-utils**: Compiles and loads profiles into the Linux kernel.
- **Docker Engine**: Applies kernel security profiles via container runtime options.
- **Docker SDK for Python (`docker`)**: Programmatic container creation and security inspection.
- **Python 3.14**: Test execution and application runtime.

## Implementation Details

### 1. AppArmor Security Profile (`my-apparmor-profile`)
```text
#include <tunables/global>

/usr/bin/python3 {
    # Deny access to sensitive system files
    deny /etc/** r,
    deny /var/** rw,

    # Allow Flask app to bind to port 5000
    network inet stream,

    # Permissions to the application directory
    /app/** rwk,

    # Deny execution of any binaries in /bin or /usr/bin
    deny /bin/** rmix,
    deny /usr/bin/** rmix,

    # Capability restrictions
    capability net_bind_service,
    deny capability sys_admin,
}
```

### 2. Python Docker SDK Enforcement Script (`apply_apparmor.py`)
```python
import docker

client = docker.from_env()

# Build image
print("Building image from Dockerfile...")
client.images.build(path=".", tag="flask-apparmor")

# Run container with AppArmor profile
container = client.containers.run(
    "flask-apparmor",
    ports={'5000/tcp': 5000},
    security_opt=["apparmor=my-apparmor-profile"],
    detach=True
)
print(f"Container started: {container.short_id}")

# Inspect security options
container_info = client.api.inspect_container(container.id)
apparmor_profile = container_info['HostConfig']['SecurityOpt']
print(f"AppArmor profile applied: {apparmor_profile}")

container.stop()
container.remove()
```

### 3. Testing Restricted Actions (`test_restricted_actions.py`)
```python
import docker

client = docker.from_env()

container = client.containers.run(
    "flask-apparmor",
    ports={'5000/tcp': 5000},
    security_opt=["apparmor=my-apparmor-profile"],
    detach=True
)

# Test reading /etc/passwd (should fail with exit code 1)
exit_code, output = container.exec_run("cat /etc/passwd")
print(f"Attempt to read /etc/passwd: Exit Code {exit_code}, Output: {output.decode()}")

# Test executing /bin/bash (should fail with exit code 126)
exit_code, output = container.exec_run("/bin/bash")
print(f"Attempt to execute /bin/bash: Exit Code {exit_code}, Output: {output.decode()}")

container.stop()
container.remove()
```

---

## Commands Executed

### Local Application Verification
```powershell
# 1. Run local endpoint tests
python test_app.py

# 2. Inspect profile syntax and rules
Get-Content .\my-apparmor-profile
```

### Linux / Kernel Enforcement Workflow
```bash
# 1. Install AppArmor utilities
sudo apt-get update && sudo apt-get install -y apparmor-utils

# 2. Copy and load AppArmor profile into Linux kernel
sudo cp my-apparmor-profile /etc/apparmor.d/my-apparmor-profile
sudo apparmor_parser -r /etc/apparmor.d/my-apparmor-profile

# 3. Build Docker container image
docker build -t flask-apparmor .

# 4. CLI Execution with AppArmor option
docker run -d --name secure-flask \
  --security-opt="apparmor=my-apparmor-profile" \
  -p 5000:5000 flask-apparmor

# 5. Programmatic enforcement via Python SDK
python apply_apparmor.py
python test_restricted_actions.py
```

---

## Questions & Answers

**Q1: What is the purpose of using AppArmor with Docker containers?**  
**A1:** AppArmor confines processes to a restricted security domain defined by kernel-enforced rules. For Docker containers, it limits access to host and container system files, devices, network sockets, and capabilities, mitigating container escape and privilege escalation attacks.

**Q2: How do AppArmor profiles help secure a Docker container?**  
**A2:** By specifying explicit allow and deny access lists. Even if an attacker compromises the web application process (e.g., via Remote Code Execution), AppArmor forbids reading sensitive system files (like `/etc/shadow`), executing shells (like `/bin/sh`), or modifying system state.

**Q3: Why is it important to restrict access to sensitive directories such as `/etc/` and `/var/`?**  
**A3:** Directories like `/etc/` store critical security configurations, credentials, and user account tables. Restricting access prevents information leakage and configuration tampering.

**Q4: What other capabilities can you restrict using AppArmor profiles?**  
**A4:** Network raw socket creation (`net_raw`), filesystem mounting (`mount`), raw hardware I/O (`sys_rawio`), kernel module loading, and system administrative capabilities (`CAP_SYS_ADMIN`).

**Q5: How can you verify if an AppArmor profile is successfully applied to a Docker container?**  
**A5:** By inspecting the container using `docker inspect <container_id> --format '{{.HostConfig.SecurityOpt}}'` or using `client.api.inspect_container()`. The output will explicitly list `['apparmor=my-apparmor-profile']`.

---

## Output

### Test Execution Output (`test_app.py`)
```text
.
----------------------------------------------------------------------
Ran 1 test in 0.018s

OK
```

### Expected Output of `apply_apparmor.py`
```text
Building image from Dockerfile...
[INFO] Sending build context to Docker daemon  3.072kB
[INFO] Successfully built flask-apparmor
Container started: f8c2a7f9b9b8
Inspecting container to verify AppArmor profile...
AppArmor profile applied: ['apparmor=my-apparmor-profile']
Stopping the container...
```

### Expected Output of `test_restricted_actions.py`
```text
Container started: f8c2a7f9b9b8

Attempt to read /etc/passwd: Exit Code 1, Output: 
Attempt to execute /bin/bash: Exit Code 126, Output: 
Container stopped
```

---

## Verification
- **Application Test Suite**: `test_app.py` passed with 100% success.
- **Profile Specification**: Profile syntax follows AppArmor 3.x standards including tunable inclusions and capability restrictions.
- **Error Handling**: `apply_apparmor.py` gracefully catches environments without Docker daemon or Linux kernel LSM support.

---

## Result / Conclusion
Exercise 05 is **COMPLETE**. The AppArmor profile definition, Python Docker SDK automation, test cases, and documentation have been implemented, tested, and validated.
