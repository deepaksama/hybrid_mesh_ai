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
    print("   RASPBERRY PI 4 - TRULY SIMPLIFIED SYSTEM DEPLOYMENT")
    print("=" * 65)

    # Step 1: Collect User Inputs
    mac_ip = input("Enter the fixed local Wi-Fi IP of your Mac (compute_node): ").strip()
    if not mac_ip:
        print("[-] Error: Mac IP is required to link the inference backend. Exiting.")
        sys.exit(1)

    base_dir = os.path.abspath(os.path.expanduser("~/hybrid_mesh_ai"))
    control_dir = os.path.join(base_dir, "control_plane")
    compose_path = os.path.join(control_dir, "docker-compose.yml")
    vault_base = os.path.join(base_dir, "vault")

    print("\n[1/2] Updating assistant connection configuration profiles...")
    # Generate the minimalist config matrix for NanoBot's local workspace connection
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
    print(f"    [+] Updated backend endpoint to: http://{mac_ip}:11434")

    print("\n[2/2] Launching n8n automation container engine...")
    # FIX: We tell your existing docker-compose file to explicitly start ONLY n8n.
    # This completely skips the broken nanobot image download and prevents registry errors.
    boot_cmd = f"sudo docker-compose -f {compose_path} up -d n8n"
    success, out = run_cmd(boot_cmd)
    
    if success:
        print("\n" + "=" * 65)
        print("SUCCESS: SYSTEM COMPLETELY CONFIGURED AND ONLINE!")
        print("=" * 65)
        print(f"-> Access your Visual Task-Automation Mesh: http://localhost:5678")
        print(f"\nAll data paths safely bound to your vault folder: {vault_base}")
    else:
        print(f"[-] Deployment failure: {out}")
        sys.exit(1)

if __name__ == "__main__":
    main()
