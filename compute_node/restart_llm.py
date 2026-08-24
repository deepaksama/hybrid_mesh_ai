#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil

def run_cmd(cmd):
    """Executes a system shell command and returns success status."""
    try:
        subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def start_services():
    print("=" * 65)
    print("         LAUNCHING SYSTEM: CONNECTING MESH COMPUTE NODE")
    print("=" * 65)
    
    # 1. Force Ollama to bind to the Wi-Fi network interface
    print("[1/3] Binding Ollama service to listen on 0.0.0.0 (Wi-Fi)...")
    run_cmd('launchctl setenv OLLAMA_HOST "0.0.0.0"')
    
    # 2. Restart the background engine to apply the configuration change
    print("[2/3] Restarting Ollama background system service engine...")
    if shutil.which("brew"):
        run_cmd("brew services restart ollama")
    else:
        print("[-] Error: Homebrew not detected. Ensure Ollama is running manually.")
        
    # 3. Handle the macOS Firewall Rules
    print("[3/3] Temporarily disabling macOS Packet Filter firewall blocks...")
    print("[!] Please enter your Mac login password if prompted by 'sudo' below:")
    if run_cmd("sudo pfctl -d"):
        print("[+] Firewall successfully dropped. Network lanes are open!")
    else:
        print("[-] Warning: Failed to drop firewall. Traffic may be blocked.")

    print("\n" + "=" * 65)
    print("SUCCESS: ENGINE RECONFIGURED AND WAITING FOR PI OVER THE AIR!")
    print("=" * 65)

def stop_services():
    print("=" * 65)
    print("         STOPPING SYSTEM: LOCKING DOWN COMPUTE NODE")
    print("=" * 65)
    
    # 1. Re-engage the native macOS Packet Filter firewall for safety
    print("[1/2] Re-enforcing native macOS firewall tables (Securing ports)...")
    print("[!] Please enter your Mac login password if prompted by 'sudo' below:")
    run_cmd("sudo pfctl -e")
    
    # 2. Re-bind Ollama strictly back to Localhost for safety when you are done
    print("[2/2] Restricting Ollama back to local machine loopback (127.0.0.1)...")
    run_cmd('launchctl setenv OLLAMA_HOST "127.0.0.1"')
    if shutil.which("brew"):
        run_cmd("brew services restart ollama")
        
    print("\n" + "=" * 65)
    print("SUCCESS: SYSTEM PROTECTED AND CLOSED TO THE LOCAL NETWORK.")
    print("=" * 65)

def main():
    if len(sys.argv) < 2:
        print("Usage Commands:")
        print("  python3 manage_compute_node.py start  -> Connect Mac to Pi over Wi-Fi")
        print("  python3 manage_compute_node.py stop   -> Close network ports & lock down Mac")
        sys.exit(1)
        
    action = sys.argv[1].lower().strip()
    if action == "start":
        start_services()
    elif action == "stop":
        stop_services()
    else:
        print(f"Unknown command option: '{action}'. Please use 'start' or 'stop'.")

if __name__ == "__main__":
    main()
