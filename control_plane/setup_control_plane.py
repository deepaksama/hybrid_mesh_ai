#!/usr/bin/env python3
import os
import sys
import subprocess
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
    print("   RASPBERRY PI 4 - SIMPLIFIED SYSTEM DEPLOYMENT SCRIPT")
    print("=" * 65)

    # Step 1: Collect your Mac Node IP
    mac_ip = input("Enter the fixed local Wi-Fi IP of your Mac (compute_node): ").strip()
    if not mac_ip:
        print("[-] Error: Mac IP is required to link the inference backend. Exiting.")
        sys.exit(1)

    # Step 2: Set up absolute system directory paths
    base_dir = os.path.abspath(os.path.expanduser("~/hybrid_mesh_ai"))
    control_dir = os.path.join(base_dir, "control_plane")
    compose_path = os.path.join(control_dir, "docker-compose.yml")
    vault_base = os.path.join(base_dir, "vault")

    # Double check that your compose blueprint actually exists before running
    if not os.path.exists(compose_path):
        print(f"[-] Error: Could not find docker-compose.yml at {compose_path}.")
        print("Please verify the file path or regenerate it before running this script.")
        sys.exit(1)

    print("\n[1/2] Updating assistant connection configuration profiles...")
    # Update only the NanoBot JSON configuration with the current Mac IP address
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
    print(f"    [+] Updated backend endpoint pointing to: http://{mac_ip}:11434")

    # Step 3: Natively boot up the containers using your existing file
    print("\n[2/2] Launching system containers via native compose engine...")
    print("    -> Initializing image layers in background task windows...")
    
    boot_cmd = f"sudo docker-compose -f {compose_path} up -d"
    success, out = run_cmd(boot_cmd)
    
    if success:
        print("\n" + "=" * 65)
        print("SUCCESS: SYSTEM COMPLETELY CONFIGURED AND ONLINE!")
        print("=" * 65)
        print(f"-> Access your Conversational Research Panel: http://localhost:8000")
        print(f"-> Access your Visual Task-Automation Mesh: http://localhost:5678")
        print(f"\nAll data paths safely bound to your vault folder: {vault_base}")
    else:
        print(f"[-] Final deployment execution layer failed: {out}")
        sys.exit(1)

if __name__ == "__main__":
    main()
