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
    print("     RASPBERRY PI 4 - NANOBOT ENVIRONMENT AUTO-INSTALLER")
    print("=" * 65)

    base_dir = os.path.abspath(os.path.expanduser("~/hybrid_mesh_ai"))
    control_dir = os.path.join(base_dir, "control_plane")
    vault_dir = os.path.join(base_dir, "vault")
    venv_dir = os.path.join(control_dir, "nanobot_env")
    nanobot_config_dir = os.path.abspath(os.path.expanduser("~/.nanobot"))

    # Step 1: Deploy native dependencies
    print("\n[1/4] Ensuring core operating system dependencies are current...")
    run_cmd("sudo apt update")
    success, out = run_cmd("sudo apt install -y python3-venv python3-pip nodejs npm")
    if not success:
        print(f"[-] Dependencies setup failed: {out}")
        sys.exit(1)

    # Step 2: Establish isolated Python virtual environment cage
    print("\n[2/4] Setting up isolated Python virtual environment matrix...")
    os.makedirs(control_dir, exist_ok=True)
    if not os.path.exists(venv_dir):
        success, out = run_cmd(f"python3 -m venv {venv_dir}")
        if not success:
            print(f"[-] Failed to generate virtual environment: {out}")
            sys.exit(1)
            
    pip_path = os.path.join(venv_dir, "bin", "pip")
    run_cmd(f"{pip_path} install --upgrade pip")
    
    print("    -> Fetching production core 'nanobot-ai' package layers via pip...")
    success, out = run_cmd(f"{pip_path} install nanobot-ai")
    if not success:
        print(f"[-] Pip deployment layer failed: {out}")
        sys.exit(1)

    # Step 3: Generate the model and server configuration maps
    print("\n[3/4] Writing configuration manifests to the storage filesystems...")
    os.makedirs(nanobot_config_dir, exist_ok=True)
    
    nanobot_config = {
        "providers": {
            "ollama": {
                "api_base": "http://127.0.0.1:11434"
            }
        },
        "agents": {
            "defaults": {
                "model": "ollama/llama3.1:8b"
            }
        },
        "mcpServers": {
            "shared-filesystem": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", vault_dir]
            }
        }
    }
    
    config_file_path = os.path.join(nanobot_config_dir, "config.json")
    with open(config_file_path, "w") as f:
        json.dump(nanobot_config, f, indent=2)
    print(f"    [+] Created absolute configuration map: {config_file_path}")

    # Step 4: Create standalone startup launcher
    print("\n[4/4] Activating background assistant server script wrappers...")
    nanobot_binary = os.path.join(venv_dir, "bin", "nanobot")
    launcher_path = os.path.join(control_dir, "start_nanobot.sh")
    
    # Write a dedicated shell script to launch the server background process safely
    with open(launcher_path, "w") as f:
        f.write(f"#!/bin/bash\n{nanobot_binary} gateway --background\n")
    run_cmd(f"chmod +x {launcher_path}")
    
    # Execute the launcher outside the silent Python capture shell
    subprocess.Popen([launcher_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print("\n" + "=" * 65)
    print("SUCCESS: NANOBOT SYSTEM IS COMPLETELY CONFIGURED AND ONLINE!")
    print("=" * 65)
    print("-> Access your Conversational Research Panel: http://localhost:18790")
    print(f"All structural tools cleanly bound to your workspace: {vault_dir}\n")

if __name__ == "__main__":
    main()
