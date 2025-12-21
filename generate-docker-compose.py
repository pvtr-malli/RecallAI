#!/usr/bin/env python3
"""Generate docker-compose.yml with volumes from config.yaml."""

import yaml
from pathlib import Path
import os

def expand_path(path: str) -> str:
    """Expand ~ and environment variables in path."""
    return os.path.expanduser(os.path.expandvars(path))

def generate_docker_compose():
    """Generate docker-compose.yml with volumes from config.yaml."""

    # Read config.yaml
    config_path = Path("config.yaml")
    if not config_path.exists():
        print("❌ config.yaml not found. Please create it first.")
        return

    with open(config_path) as f:
        config = yaml.safe_load(f)

    folders = config["indexing"].get("folders", [])

    if not folders:
        print("⚠️  No folders configured in config.yaml")
        print("Using default home directory mount")
        folders = []

    # Base docker-compose structure
    compose = {
        "services": {
            "ollama": {
                "image": "ollama/ollama:latest",
                "container_name": "recallai-ollama",
                "ports": ["11434:11434"],
                "volumes": ["ollama_data:/root/.ollama"],
                "healthcheck": {
                    "test": ["CMD", "ollama", "list"],
                    "interval": "10s",
                    "timeout": "5s",
                    "retries": 5
                }
            },
            "recallai": {
                "build": {
                    "context": ".",
                    "dockerfile": "Dockerfile"
                },
                "container_name": "recallai-app",
                "ports": ["8000:8000"],
                "volumes": [],
                "environment": [
                    "OLLAMA_BASE_URL=http://ollama:11434"
                ],
                "depends_on": {
                    "ollama": {
                        "condition": "service_healthy"
                    }
                },
                "restart": "unless-stopped"
            }
        },
        "volumes": {
            "ollama_data": {
                "driver": "local"
            }
        }
    }

    # Add volume mounts
    volumes = []

    # Add indexed folders as read-only mounts
    if folders:
        for idx, folder in enumerate(folders):
            expanded = expand_path(folder)
            # Use /data/folder_N for each indexed folder
            volumes.append(f"{expanded}:/data/folder_{idx}:ro")
        print(f"✅ Configured {len(folders)} folder(s) for indexing:")
        for idx, folder in enumerate(folders):
            print(f"   {folder} → /data/folder_{idx}")
    else:
        # Fallback to home directory if no folders configured
        volumes.append("${HOME}:/host_home:ro")
        print("✅ Using home directory mount: ${HOME} → /host_home")

    # Add persistent storage volumes
    config_file = "./config.docker.yaml:/app/config.yaml" if folders else "./config.yaml:/app/config.yaml"
    volumes.extend([
        "./indexes:/app/indexes",
        "./models:/app/models",
        "./logs:/app/logs",
        config_file
    ])

    compose["services"]["recallai"]["volumes"] = volumes

    # Write docker-compose.yml
    output_path = Path("docker-compose.yml")
    with open(output_path, "w") as f:
        yaml.dump(compose, f, default_flow_style=False, sort_keys=False)

    print(f"✅ Generated docker-compose.yml")

    # Generate docker-specific config.yaml with mapped paths
    if folders:
        docker_config = config.copy()
        docker_config["indexing"]["folders"] = [f"/data/folder_{idx}" for idx in range(len(folders))]

        with open("config.docker.yaml", "w") as f:
            yaml.dump(docker_config, f, default_flow_style=False, sort_keys=False)

        print(f"✅ Generated config.docker.yaml with Docker paths")

    print()
    print("📝 Folders mapped:")
    if folders:
        for idx, folder in enumerate(folders):
            print(f"   {folder} → /data/folder_{idx}")
    else:
        print("   ${HOME} → /host_home")
    print()
    print("🚀 Start with: docker-compose up -d")

if __name__ == "__main__":
    generate_docker_compose()
