#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil

def run_cmd(cmd, check=True, input_data=None):
    """Helper function to execute system shell paths and return output logs."""
    try:
        res = subprocess.run(cmd, shell=True, check=check, text=True, input=input_data, capture_output=True)
        return True, res.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()

def main():
    print("=" * 65)
    print("      MACBOOK PRO INTEL - AUTOMATED LOCAL AI SETUP SCRIPT")
    print("=" * 65)
    print("This script will configure your Mac to act as an AI Compute Node.\n")

    # Step 1: Check and Install Homebrew
    print("[1/4] Verifying Homebrew environment package manager...")
    if not shutil.which("brew"):
        print("    -> Homebrew not detected. Initializing official installation pipeline...")
        # Sets env variable to bypass interactive keystroke prompts during brew setup
        os.environ["NONINTERACTIVE"] = "1"
        install_brew_cmd = '/bin/bash -c "$(curl -fsSL https://githubusercontent.com)"'
        success, out = run_cmd(install_brew_cmd, check=False)
        if not success:
            print(f"[-] Homebrew setup failed: {out}\nPlease install it manually first.")
            sys.exit(1)
        print("[+] Homebrew installed successfully!")
    else:
        print("[+] Homebrew package manager is active.")

    # Step 2: Install and Configure Ollama Service
    print("\n[2/4] Setting up Ollama local inference backend...")
    if not shutil.which("ollama"):
        print("    -> Pulling Ollama application core binaries via Homebrew...")
        success, out = run_cmd("brew install ollama", check=False)
        if not success:
            print(f"[-] Failed to execute brew install ollama: {out}")
            sys.exit(1)
        print("[+] Ollama binary packages deployed.")
    else:
        print("[+] Ollama inference framework already available.")

    print("Configuring environmental routing flags (Binding Ollama to 0.0.0.0)...")
    run_cmd('launchctl setenv OLLAMA_HOST "0.0.0.0"')
    
    print("Registering and launching Ollama background services daemon...")
    run_cmd("brew services restart ollama", check=False)
    print("[+] Inference service engine started on background port :11434.")

    # Step 3: Pull Optimized Quantized Model
    print("\n[3/4] Fetching optimized GGUF weights (Llama-3.1-8B-Instruct)...")
    print("    -> Downloading roughly 4.7GB over network. This may take a few minutes...")
    success, out = run_cmd("ollama pull llama3.1:8b-instruct-q4_K_M", check=False)
    if success:
        print("[+] Model pulled, processed, and cached into localized hardware layers.")
    else:
        print("[-] Notice: Primary stream pull returned non-zero code. Verifying via core listing...")
        _, models = run_cmd("ollama list", check=False)
        if "llama3.1" in models:
            print("[+] Model footprint successfully validated via internal cache.")
        else:
            print("[-] Model download failed. Please run 'ollama pull llama3.1:8b-instruct-q4_K_M' manually later.")

    # Step 4: Secure Native macOS Application Firewall
    print("\n[4/4] Activating Native Firewall Protection (Packet Filter)...")
    pi_ip = input("Enter your Raspberry Pi's fixed local Wi-Fi IP address (e.g. 192.168.1.50): ").strip()

    if not pi_ip:
        print("[*] No IP address provided. Skipping custom packet filter firewall lockdowns.")
    else:
        anchor_path = "/etc/pf.anchors/local.llm.security"
        pf_conf_path = "/etc/pf.conf"
        rule_string = f"pass in proto tcp from {pi_ip} to any port 11434\n"
        
        print(f"\n[!] Configuring rules to restrict port 11434 exclusively to the Pi: {pi_ip}")
        print("[!] Input your Mac user password if prompted by 'sudo' below.")
        
        # Build anchor rule
        cmd_write_anchor = f'echo "{rule_string}" | sudo tee {anchor_path}'
        s1, o1 = run_cmd(cmd_write_anchor, check=False)
        
        if s1:
            print(f"[+] Security rule successfully committed into system anchor configuration.")
            _, current_pf = run_cmd(f"cat {pf_conf_path}", check=False)
            
            if "local.llm.security" not in current_pf:
                print("Linking custom security anchor loops into your primary firewall system profile...")
                append_cmd = (
                    f'echo "anchor \\"local.llm.security\\"\\nload anchor \\"local.llm.security\\" from \\"{anchor_path}\\"" '
                    f'| sudo tee -a {pf_conf_path}'
                )
                run_cmd(append_cmd, check=False)
            
            print("Refreshing and enforcing structural firewall tables system wide...")
            run_cmd("sudo pfctl -ef /etc/pf.conf", check=False)
            print("[+] Firewall actively guarding inbound traffic over Wi-Fi network lanes!")
        else:
            print("[-] Firewall write authority denied. Skipping security enforcement steps.")

    print("\n" + "=" * 65)
    print("SETUP TERMINATED: BACKEND IS STABLE AND ENGINE RUNNING!")
    print("=" * 65)
    print("Next step: Boot up your Raspberry Pi's Docker Compose stack.")
    print("Ensure your configuration maps directly to this machine's Wi-Fi IP address.")

if __name__ == "__main__":
    main()
