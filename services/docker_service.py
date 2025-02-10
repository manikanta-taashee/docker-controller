import docker
from utils.helpers import find_available_port
import os
mapping_path = os.getenv("MAPPING_PATH")
if mapping_path[-1] == "/":
    mapping_path = mapping_path[:-1]

docker_client = docker.from_env()

def create_container(username: str):
    """
    Create a new container with a unique username as the container name.
    Assign a dynamically available port and use the nginx:stable-alpine3.20-slim image.
    """
    try:
        # Validate username
        if not username or not username.isalnum():
            raise ValueError("Username must be alphanumeric and non-empty.")

        # Check if a container with the same name already exists
        try:
            existing_container = docker_client.containers.get(username)
            if existing_container:
                raise ValueError(f"A container with the name '{username}' already exists.")
        except docker.errors.NotFound:
            pass  # No existing container with this name

        # Find an available port
        port = find_available_port()

        # Create the container
        container = docker_client.containers.run(
            "codercom/code-server:latest",
            detach=True,
            name=f"{username}-code-server",
            user="root",
            ports={'8080/tcp': port},  # Map container port 8080 to host port 8080
            volumes={f"{mapping_path}/{username}": {"bind": "/home/coder", "mode": "rw"}},  # Volume mapping
            environment={"PASSWORD": f"coder-{username}"},  # Set password
            restart_policy={"Name": "always"},  # Restart policy
            tty=True
        )

        # Return container details
        return {
            "message": "Container created successfully!",
            "container_id": container.id,
            "container_name": f"{username}-code-server",
            "access_url": f"http://10.21.34.204:{port}",
            "port": port
        }

    except Exception as e:
        raise Exception(f"Error creating container: {str(e)}")

def get_container(container_name: str):
    """
    Retrieve details of a container by its name.
    """
    try:
        container = docker_client.containers.get(container_name)
        return {
            "container_id": container.id,
            "status": container.status,
            "ports": container.attrs['HostConfig']['PortBindings'].get('80/tcp', [])
        }
    except docker.errors.NotFound:
        return None
    except Exception as e:
        raise Exception(f"Error retrieving container: {str(e)}")

def remove_container(container_name: str):
    """
    Stop and remove a container by its name.
    """
    try:
        container = docker_client.containers.get(container_name)
        container.stop()
        container.remove()
        return {"message": f"Container '{container_name}' removed successfully!"}
    except docker.errors.NotFound:
        return None
    except Exception as e:
        raise Exception(f"Error removing container: {str(e)}")


def list_containers():
    """
    List all running and stopped containers.
    Handle cases where PortBindings is None or '80/tcp' is missing.
    """
    try:
        containers = docker_client.containers.list(all=True)  # Include both running and stopped containers
        container_list = []

        for c in containers:
            if "code-server" not in c.name:
                continue
            
            # Retrieve port mappings
            ports_info = c.attrs['NetworkSettings']['Ports']
            mapped_ports = {}

            if ports_info:
                for port, bindings in ports_info.items():
                    mapped_ports[port] = [binding['HostPort'] for binding in bindings] if bindings else []
            
            # Append container details to the list
            container_list.append({
                "id": c.id,
                "name": c.name,
                "status": c.status,
                "ports": mapped_ports
            })
        
        return container_list

    except Exception as e:
        raise Exception(f"Error listing containers: {str(e)}")
