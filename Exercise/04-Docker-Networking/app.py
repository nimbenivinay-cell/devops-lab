from flask import Flask, jsonify
import socket
import os

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
    """Verify connectivity to MySQL and Redis containers via Docker DNS."""
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
    # Running on 0.0.0.0 and port 5001 as required by the exercise
    app.run(host='0.0.0.0', port=5001, debug=True)
