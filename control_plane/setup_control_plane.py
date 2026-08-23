#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
import json

def run_cmd(cmd, check=True):
    """Executes a system shell command and returns status/output logs."""
    try:
        res = subprocess.run(cmd, shell=True, check=check, text=True, capture_output=True)
        return True, res.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()

def main():
    print("=" * 65)
    print("      RASPBERRY PI 4 - NATIVE CONTROL-PLANE SETUP SCRIPT")
    print("=" * 65)
    print("This script will build your local orchestration and assistant stack.\n")

    # Step 1: Collect User Inputs
    mac_ip = input("Enter the fixed local Wi-Fi IP of your Mac (compute_node): ").strip()
    if not mac_ip:
        print("[-] Error: Mac IP is required to link the inference backend. Exiting.")
        sys.exit(1)

    print("\n[1/4] Establishing structural workspace directories...")
    # Base configuration directories matching your exact naming preferences
    base_dir = os.path.expanduser("~/hybrid_mesh_ai")
    control_dir = os.path.join(base_dir, "control_plane")
    vault_base = os.path.join(base_dir, "vault")
    sub_directories = ["documentation", "mail_dumps", "research", "external_hdd"]

    os.makedirs(control_dir, exist_ok=True)
    for folder in sub_directories:
        path = os.path.join(vault_base, folder)
        os.makedirs(path, exist_ok=True)
        print(f"    [+] Created: {path}")

    # Step 2: Native Docker Installation
    print("\n[2/4] Verifying local Docker runtime status...")
    if not shutil.which("docker"):
        print("    -> Docker not detected. Initializing native repository mirrors...")
        
        print("    -> Updating system package listings...")
        run_cmd("sudo apt update")
        
        print("    -> Installing Docker engine packages natively...")
        # Installs native system engine alongside modern compose v2 specifications
        success, out = run_cmd("sudo apt install -y docker.io docker-compose-v2")
        if not success:
            print(f"[-] Native Docker installation failed: {out}")
            sys.exit(1)
            
        print("    -> Injecting user configurations into system groups...")
        # Dynamically grabs active session name to add to the docker group access matrix
        user = os.getlogin() if os.getlogin() else "pi"
        run_cmd(f"sudo usermod -aG docker {user}")
        print("[+] Docker runtime successfully deployed to system binaries.")
    else:
        print("[+] Docker environment is fully active.")

    # Step 3: Write Configuration Files
    print("\n[3/4] Writing minimalist configuration maps to storage layout...")
    
    # 3a. Write NanoBot Config JSON (Placed inside control_plane/)
    nanobot_config = {
        "agents": {
            "defaults": {
                "model": "ollama/llama3.1:8b-instruct-q4_K_M",
                "api_base": f"http://{mac_ip}:11434"
            }
        },
        "mcpServers": {
            "shared-filesystem": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", "/app/storage"]
            }
        }
    }
    
    nanobot_conf_path = os.path.join(control_dir, "nanobot_config.json")
    with open(nanobot_conf_path, "w") as f:
        json.dump(nanobot_config, f, indent=2)
    print(f"    [+] Generated: {nanobot_conf_path}")

    # 3b. Write Docker Compose Template (Placed inside control_plane/)
    docker_compose_content = f"""version: '3.8'

networks:
  ai_shared_network:
    driver: bridge

services:
  # Logistics & Event Automation Layer
  n8n:
    image: docker.n8n.io/n8nio/n8n:latest
    container_name: local_n8n_orchestrator
    restart: always
    ports:
      - "5678:5678"
    networks:
      - ai_shared_network
    environment:
      - N8N_HOST=0.0.0.0
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - EXECUTIONS_DATA_PRUNE=true
      - EXECUTIONS_DATA_MAX_AGE=48
    volumes:
      - n8n_data:/home/node/.n8n
      - {vault_base}:/data/storage

  # Conversational Interface Layer
  nanobot:
    image: ghcr.io/hkuds/nanobot:latest
    container_name: local_nanobot_agent
    restart: always
    ports:
      - "8000:8000"
    networks:
      - ai_shared_network
    volumes:
      - {nanobot_conf_path}:/app/config.json
      - {vault_base}:/app/storage

volumes:
  n8n_data:
"""
    
    compose_path = os.path.join(control_dir, "docker-compose.yml")
    with open(compose_path, "w") as f:
        f.write(docker_compose_content)
    print(f"    [+] Generated: {compose_path}")

    # Step 4: Boot Containers
    print("\n[4/4] Deploying applications into background runtime...")
    print("    -> Pulling container configurations from network layers...")
    
    # Change context directory to the control_plane workspace
    os.chdir(control_dir)
    
    # Executing through sudo fallback to ensure permissions handle fresh service boots safely
    success, out = run_cmd("sudo docker compose up -d")
    
    if success:
        print("[+] Containers spun up successfully!")
    else:
        print(f"[-] Final deployment failure: {out}")
        print("[*] Troubleshooting: Please verify hardware memory, then run 'sudo docker compose up -d' manually.")
        sys.exit(1)

    print("\n" + "=" * 65)
    print("SETUP TERMINATED: CONTROL_PLANE ECOSYSTEM IS STANDING PROUD!")
    print("=" * 65)
    print(f"-> Access your Conversational Research Panel: http://localhost:8000")
    print(f"-> Access your Visual Task-Automation Mesh: http://localhost:5678")
    print(f"\nAll files mapped seamlessly into your shared vault: {vault_base}")

if __name__ == "__main__":
    main()
