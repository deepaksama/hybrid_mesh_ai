# Local AI Assistant Ecosystem Documentation
## Architecture, Security, and Step-by-Step Deployment Guide

This document provides a comprehensive architectural strategy and step-by-step instructions to deploy a local LLM assistant ecosystem distributed across a Raspberry Pi 4 (4GB RAM) and an Intel MacBook Pro (32GB RAM).

---

## 1. Hardware Architecture Strategy
To optimize performance, availability, and resource management, the system utilizes a **Distributed Hybrid Architecture**.

### Workload Distribution
*   **Compute Node (MacBook Pro)**: Runs the Ollama server for heavy LLM inference execution using quantized GGUF models. It offers the raw CPU capabilities and memory bandwidth (32GB DDR4) necessary to sustain usable generation speeds (5–11 tokens/sec).
*   **Orchestration Node (Raspberry Pi 4)**: Functions as a 24/7, low-power lightweight gateway hosting the user interfaces, task automation runners, and local index files. 

### Network Topology
```
+---------------------------------------+         +---------------------------------------+
|  Raspberry Pi 4 (4GB RAM)             |         |  MacBook Pro (Intel i7, 32GB RAM)     |
|  - 24/7 Orchestration Gateway         |         |  - Compute Engine                     |
|  - n8n Automation Engine              |  <--->  |  - Ollama Server (LLM Backend)        |
|  - NanoBot Agent Host                 | (LAN)   |  - 8B to 14B GGUF Quantized Models    |
|  - Shared Storage Filesystem          |         |  - On-Demand Compute                  |
+---------------------------------------+         +---------------------------------------+
```

---

## 2. Hardening Local Network Security
Because Ollama does not include native authentication or traffic encryption, binding it to `0.0.0.0` exposes it to your entire local network. The steps below isolate and secure your environment.

### Restricting Access via the macOS Firewall (PF)
Configure the native macOS packet filter to allow inbound requests on port 11434 *only* if they originate from your specific Raspberry Pi IP address.

1. Create a security anchor configuration file on your Mac:
   ```bash
   sudo nano /etc/pf.anchors/local.llm.security
   ```
2. Insert the following rule (replace `<RASPBERRY_PI_IP>` with the actual IP address of your Pi):
   ```text
   pass in proto tcp from <RASPBERRY_PI_IP> to any port 11434
   ```
3. Load the rule within your primary configurations file (`/etc/pf.conf`) and reload the service:
   ```bash
   sudo pfctl -f /etc/pf.conf
   sudo pfctl -e
   ```

---

## 3. Co-Deployed Software Stack Configuration
This setup deploys **n8n** (for event-driven workflow automation) and **NanoBot** (for Model Context Protocol research and terminal chat interactions) side-by-side inside a single Docker Compose network.

### Preparing the Flexible Directory Architecture
Run these commands on the Raspberry Pi terminal to configure your directory paths before mounting:
```bash
mkdir -p ~/local-ai-system/storage/documentation
mkdir -p ~/local-ai-system/storage/mail_dumps
mkdir -p ~/local-ai-system/storage/research
mkdir -p ~/local-ai-system/storage/external_hdd
cd ~/local-ai-system
```

### The Integrated docker-compose.yml
Save the following configuration as `docker-compose.yml` inside `~/local-ai-system/`:

```yaml
version: '3.8'

networks:
  ai_shared_network:
    driver: bridge

services:
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
      - /home/pi/local-ai-system/storage:/data/storage

  nanobot:
    image: ghcr.io/hkuds/nanobot:latest
    container_name: local_nanobot_agent
    restart: always
    ports:
      - "8000:8000"
    networks:
      - ai_shared_network
    volumes:
      - ./nanobot_config.json:/app/config.json
      - /home/pi/local-ai-system/storage:/app/storage

volumes:
  n8n_data:
```

### Creating the Minimalist NanoBot Config
Save the following configuration as `nanobot_config.json` inside `~/local-ai-system/` (replace `<MACBOOK_IP_ADDRESS>` with your Mac's local network IP):

```json
{
  "agents": {
    "defaults": {
      "model": "ollama/llama3.1:8b-instruct-q4_K_M",
      "api_base": "http://<MACBOOK_IP_ADDRESS>:11434"
    }
  },
  "mcpServers": {
    "shared-filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/app/storage"]
    }
  }
}
```

Deploy the entire stack with a single command:
```bash
docker compose up -d
```

---

## 4. Zero-Restart External Storage Upgrades
To expand storage without modifying your Docker compose stacks or restarting running services, map your external drive directly to Linux mount blocks.

### Permanent Storage Mounting via /etc/fstab
1. Connect your external USB hard drive to one of the blue USB 3.0 ports on the Raspberry Pi.
2. Find the drive identifier (UUID) by running:
   ```bash
   sudo blkid
   ```
3. Open your file systems table file:
   ```bash
   sudo nano /etc/fstab
   ```
4. Add the line below at the end of the file to link your drive directly to the shared folder path (replace `YOUR-UUID-HERE` with your real identifier and use your drive's file system like `ext4` or `ntfs`):
   ```text
   UUID=YOUR-UUID-HERE /home/pi/local-ai-system/storage/external_hdd ext4 defaults,nofail 0 2
   ```
5. Reload the filesystems without a reboot:
   ```bash
   sudo mount -a
   ```
*Both n8n and NanoBot will instantly recognize the new storage capacity inside their respective environments without a single service restart.*

---

## 5. Specialized Automation & Research Blueprints

### Workflow A: Local Knowledge Engine & Research Retrieval
*   **The Architecture**: Instead of burning memory with a massive vector database engine on the Pi, text observations are saved as indexed lists or structural markdown files directly inside `/data/storage/research`.
*   **Execution Strategy**: Use the NanoBot browser UI at `http://<PI_IP>:8000`. Query topics via natural conversation. NanoBot uses the local filesystem Model Context Protocol (MCP) tool to read matching documents and forwards the parsed context chunks to Ollama on your Mac to extract precise, structured insights.

### Workflow B: Mailbox Cleanup and Documentation Pipelines
*   **The Architecture**: Use the n8n visual automation platform at `http://<PI_IP>:5678`.
*   **Execution Strategy**: Drag an IMAP Email Trigger node onto your blank n8n workflow canvas. Configure your email provider credentials. Route incoming email metadata (headers, subject strings) directly into an Advanced AI node linked to your MacBook's Ollama address. Instruct the model to analyze logs, classify senders, or draft data-cleanup batch files that dump straight into `/data/storage/mail_dumps` for systematic handling.
