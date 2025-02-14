import docker

NGINX_HOST_CONF_PATH = "/code/nginx.conf"  # Host machine path

docker_client = docker.from_env()

def update_nginx_config(username: str):
    """
    Update Nginx configuration to route traffic for the new container.
    Ensures the new location block is added inside the server block.
    """
    try:
        with open(NGINX_HOST_CONF_PATH, "r") as conf_file:
            lines = conf_file.readlines()

        new_location_block = f"""
    location /{username}/ {{
        proxy_pass http://{username}-code-server:8080/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        add_header X-Frame-Options SAMEORIGIN;
        add_header Content-Security-Policy "frame-ancestors 'self' *;";
    }}
"""

        # Insert before the last closing '}' of the server block
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip() == "}":
                lines.insert(i, new_location_block)
                break

        # Write the updated content back to the file
        with open(NGINX_HOST_CONF_PATH, "w") as conf_file:
            conf_file.writelines(lines)

        print(f"Nginx config updated for user: {username}")

    except Exception as e:
        raise Exception(f"Error updating Nginx config: {str(e)}")

def restart_nginx():
    """
    Restart the Nginx container to apply new configuration.
    """
    try:
        nginx_container = docker_client.containers.get("nginx")
        nginx_container.exec_run("nginx -s reload")
        print("Nginx restarted successfully.")
    except docker.errors.NotFound:
        raise Exception("Nginx container not found. Ensure it's running.")
    except Exception as e:
        raise Exception(f"Error restarting Nginx: {str(e)}")
