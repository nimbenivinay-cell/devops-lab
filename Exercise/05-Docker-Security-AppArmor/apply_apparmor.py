import sys

try:
    import docker
except ImportError:
    print("[ERROR] docker python package not installed. Run: pip install docker")
    sys.exit(1)

def main():
    print("=== Applying AppArmor Profile using Docker SDK for Python ===")
    try:
        # Create a Docker client
        client = docker.from_env()

        # Build the Docker image
        print("Building image from Dockerfile...")
        client.images.build(path=".", tag="flask-apparmor")
        print("Successfully built flask-apparmor image.")

        # Run the container with the AppArmor profile
        print("Running container with AppArmor profile 'my-apparmor-profile'...")
        container = client.containers.run(
            "flask-apparmor",
            ports={'5000/tcp': 5000},
            security_opt=["apparmor=my-apparmor-profile"],
            detach=True
        )

        print(f"Container started: {container.short_id}")

        # Verify AppArmor profile applied
        print("Inspecting container to verify AppArmor profile...")
        container_info = client.api.inspect_container(container.id)
        apparmor_profile = container_info['HostConfig']['SecurityOpt']

        print(f"AppArmor profile applied: {apparmor_profile}")

        # Stop and remove the container
        print("Stopping the container...")
        container.stop()
        container.remove()
        print("Container stopped and cleaned up.")
    except docker.errors.DockerException as e:
        print(f"[ENVIRONMENT NOTICE] Docker daemon is not accessible: {e}")
        print("To run this test, ensure Docker Desktop / dockerd is active with AppArmor support on a Linux host.")

if __name__ == '__main__':
    main()
