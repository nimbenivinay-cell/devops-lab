import sys

try:
    import docker
except ImportError:
    print("[ERROR] docker python package not installed. Run: pip install docker")
    sys.exit(1)

def main():
    print("=== Testing Restricted Actions under AppArmor Confinement ===")
    try:
        # Create a Docker client
        client = docker.from_env()

        # Run the container with the AppArmor profile
        print("Launching container with AppArmor profile...")
        container = client.containers.run(
            "flask-apparmor",
            ports={'5000/tcp': 5000},
            security_opt=["apparmor=my-apparmor-profile"],
            detach=True
        )
        print(f"Container started: {container.short_id}")

        # Test restricted action 1: Access /etc/passwd (should be denied)
        print("\n[Action 1] Attempting to read /etc/passwd...")
        exit_code, output = container.exec_run("cat /etc/passwd")
        print(f"Attempt to read /etc/passwd: Exit Code {exit_code}, Output: {output.decode().strip()}")

        # Test restricted action 2: Execute /bin/bash (should be denied)
        print("\n[Action 2] Attempting to execute /bin/bash...")
        exit_code, output = container.exec_run("/bin/bash -c 'whoami'")
        print(f"Attempt to execute /bin/bash: Exit Code {exit_code}, Output: {output.decode().strip()}")

        # Stop and remove the container
        print("\nStopping and cleaning up container...")
        container.stop()
        container.remove()
        print("Container stopped.")

    except docker.errors.DockerException as e:
        print(f"[ENVIRONMENT NOTICE] Docker daemon is not accessible: {e}")
        print("AppArmor testing requires a Linux host with AppArmor kernel module enabled.")

if __name__ == '__main__':
    main()
