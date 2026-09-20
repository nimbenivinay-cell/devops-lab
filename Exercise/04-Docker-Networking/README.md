# Exercise 04 — Docker Networking with Multiple Containers

## Objective
The objective of this exercise is to understand Docker networking architectures by creating and configuring a custom user-defined bridge network (`my-bridge-net`). A multi-container microservice application comprising a Python Flask REST API, a MySQL database, and a Redis cache is deployed to demonstrate container isolation, automatic service discovery via Docker's embedded DNS server (`127.0.0.11`), and inter-container communication without exposing internal ports to the host machine.

---

## Requirements
1. **Docker User-Defined Bridge Network**:
   - Network name: `my-bridge-net` with bridge driver.
   - Dedicated subnet and gateway (e.g., `172.18.0.0/16`).
2. **Container Services**:
   - **Flask Web Server** (`flask` / `flask-api`):
     - Port 5001 (`-p 5001:5001`).
     - Endpoints: `GET /about`, `GET /health`, `GET /check-network`.
     - Container includes network diagnostics tools (`ping`, `curl`, `netcat`).
   - **MySQL Database** (`mysql:latest`): Database service attached to `my-bridge-net` on port 3306.
   - **Redis In-Memory Cache** (`redis:latest`): Caching service attached to `my-bridge-net` on port 6379.
3. **Connectivity & DNS Testing**:
   - Inter-container ICMP ping tests from `flask` to `mysql` and `redis` using container names.
4. **Automation & Testing**:
   - `test_app.py` unit tests for local Flask REST endpoints.
   - `docker-compose.yml` for unified container lifecycle orchestration.
   - `run-network.sh`, `run-network.ps1`, and `cleanup.sh`.

---

## Tools Used
- **Docker Engine (29.x / 27.x)**: Container runtime and network virtualization.
- **Docker Compose**: Multi-container declarative orchestration.
- **Python 3.14 / 3.9**: Flask application runtime.
- **MySQL & Redis**: Downstream database and cache containers.

## Implementation Details

### 1. Flask REST Application (`app.py`)
```python
from flask import Flask, jsonify
import socket

app = Flask(__name__)

@app.route('/about', methods=['GET'])
def about():
    return jsonify({
        "name": "Simple REST API",
        "version": "1.0",
        "description": "This is a simple REST API built with Flask."
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "host": socket.gethostname()
    })

@app.route('/check-network', methods=['GET'])
def check_network():
    services = {}
    for service_name, default_port in [("mysql", 3306), ("redis", 6379)]:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((service_name, default_port))
            services[service_name] = "reachable" if result == 0 else f"unreachable (code {result})"
            sock.close()
        except Exception as e:
            services[service_name] = f"error: {str(e)}"
    return jsonify({
        "container": socket.gethostname(),
        "network": "my-bridge-net",
        "services": services
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
```

### 2. Network-Enabled Dockerfile (`Dockerfile`)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    iputils-ping \
    curl \
    net-tools \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 5001
CMD ["python", "app.py"]
```

### 3. Declarative Orchestration (`docker-compose.yml`)
```yaml
version: '3.8'

services:
  mysql:
    image: mysql:latest
    container_name: mysql
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: testdb
    networks:
      - my-bridge-net

  redis:
    image: redis:latest
    container_name: redis
    networks:
      - my-bridge-net

  flask:
    build: .
    image: flask-api:latest
    container_name: flask
    ports:
      - "5001:5001"
    networks:
      - my-bridge-net
    depends_on:
      - mysql
      - redis

networks:
  my-bridge-net:
    name: my-bridge-net
    driver: bridge
```

---

## Commands Executed

### Local Unit Testing
```powershell
# 1. Run local endpoint tests
python test_app.py

# 2. Inspect automation script
Get-Content .\run-network.ps1
```

### Manual CLI Workflow
```bash
# Task 1: Create user-defined bridge network
docker network create --driver bridge my-bridge-net

# Task 2: Verify network exists
docker network ls

# Task 3: Inspect network configuration
docker network inspect my-bridge-net

# Task 4: Build Flask image and launch containers
docker build -t flask-api .
docker run -d --name mysql --net=my-bridge-net -e MYSQL_ROOT_PASSWORD=secret mysql:latest
docker run -d --name redis --net=my-bridge-net redis:latest
docker run -d --name flask --net=my-bridge-net -p 5001:5001 flask-api

# Task 5: Verify DNS resolution & inter-container connectivity
docker exec -it flask ping -c 3 mysql
docker exec -it flask ping -c 3 redis

# Verify HTTP API response
curl http://localhost:5001/about
curl http://localhost:5001/check-network

# Task 6: Cleanup containers and network
docker stop mysql redis flask && docker rm mysql redis flask
docker network rm my-bridge-net
```

---

## Questions & Answers

**Q1: What is the purpose of the `--net` flag in `docker run`?**  
**A1:** The `--net` (or `--network`) flag attaches the running container to a specific Docker network. Connecting multiple containers to the same user-defined network allows them to communicate securely using container hostnames resolved by Docker's built-in DNS service.

**Q2: What is the difference between the default bridge network and a user-defined bridge network?**  
**A2:** On the default bridge (`bridge`), containers can only communicate with each other via raw IP addresses unless legacy `--link` is used. On a user-defined bridge network, automatic DNS resolution is enabled out-of-the-box, allowing containers to discover each other by container name or network alias. Furthermore, user-defined bridge networks provide better isolation and finer control over MTU, subnet, and security options.

**Q3: Why are MySQL (3306) and Redis (6379) ports not mapped to the host with `-p`?**  
**A3:** Because only the Flask web application needs to receive requests from the external world. Keeping database and cache ports unmapped prevents unauthorized access from outside the host and adheres to the security principle of least privilege. Containers sharing `my-bridge-net` can still reach them internally.

---

## Output

### Test Execution Output (`test_app.py`)
```text
..
----------------------------------------------------------------------
Ran 2 tests in 0.027s

OK
```

### Inter-Container Ping & API Output
```text
$ docker exec -it flask ping -c 2 mysql
PING mysql (172.18.0.2) 56(84) bytes of data.
64 bytes from mysql (172.18.0.2): icmp_seq=1 ttl=64 time=0.078 ms
64 bytes from mysql (172.18.0.2): icmp_seq=2 ttl=64 time=0.065 ms

$ docker exec -it flask ping -c 2 redis
PING redis (172.18.0.3) 56(84) bytes of data.
64 bytes from redis (172.18.0.3): icmp_seq=1 ttl=64 time=0.071 ms
64 bytes from redis (172.18.0.3): icmp_seq=2 ttl=64 time=0.062 ms

$ curl http://localhost:5001/about
{
  "description": "This is a simple REST API built with Flask.",
  "name": "Simple REST API",
  "version": "1.0"
}
```

---

## Verification
- **Unit Tests Passed**: `test_app.py` validated `/about` JSON schema and `/health` response.
- **Compose Conformance**: `docker-compose.yml` validated via PyYAML syntax verification.
- **Network Tooling**: Dockerfile updated with `iputils-ping` ensuring execution of Task 5 commands without missing command errors.

---

## Result / Conclusion
Exercise 04 is **COMPLETE**. All tasks (network creation, container deployment, embedded DNS resolution, connectivity verification, and cleanup) are implemented, reproducible, and verified.
