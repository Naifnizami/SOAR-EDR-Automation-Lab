# 🛡️ AI Security Analyst Agent (Production Grade)

A containerized Security Orchestration, Automation, and Response (SOAR) microservice that acts as a **Tier-1 SOC Analyst**. It integrates **Splunk** (SIEM), **Groq/Llama-3** (AI Analysis), and **Jira** (Ticketing) into a fully automated SOC pipeline.

This is not just a script, this is a **deployment-ready Dockerized application** served via Gunicorn.

---

### 🎥 Demo Video
[**Click here to watch the Automated Triage Demo**](AI_SOC_Agent_Automated_Triage_Demo.mp4)  
*(Note: If the video does not play inside the GitHub mobile app, please tap "View Raw" or download the file.)*

---

## 🚀 What This Agent Does
1.  **Ingest:** Receives webhook alerts from Splunk when an attack is detected.
2.  **Triage:** Automatically checks if the IP is a "False Positive" (Local/Whitelisted) or a "True Threat".
3.  **Investigate:** Uses **Llama-3 (70B)** to perform a threat analysis on malicious IPs.
4.  **Act:**
    *   **Auto-Close:** Resolves Jira tickets immediately for safe alerts (saving analyst time).
    *   **Escalate:** Creates high-severity Jira incidents with a full AI-written report for real threats.

## 🏗️ Core Capabilities
*   **Production Architecture:** Runs on **Gunicorn** with 4 parallel worker processes for high concurrency.
*   **Containerized:** Deploys via **Docker (Debian Slim)**; environment agnostic (runs on AWS, Azure, or Local Linux).
*   **Smart Detection:** Includes logic to whitelist localhost/private scans vs. external attackers.
*   **AI-Powered:** Utilizes the Groq API for sub-second inference speeds.

## 🛠️ Architecture Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Runtime** | Docker (Python 3.10-slim) | Isolated, reproducible environment. |
| **Server** | Gunicorn (WSGI) | Production-grade server for handling concurrent webhooks. |
| **SIEM** | Splunk Enterprise | Monitors system logs (`/var/log/auth.log`) for attacks. |
| **Intelligence** | Llama 3 (via Groq) | Analyzes IPs and writes incident reports. |
| **Ticketing** | Jira Cloud API | Workflow automation. |

---

## 📦 Quick Start (Production Deployment)

### 1. Clone & Configure
```bash
git clone https://github.com/Naifnizami/AI-Security-Analyst-Agent.git
cd AI-Security-Analyst-Agent
mv .env.example .env
```

### 2. Add Credentials
Edit the `.env` file with your keys:
```ini
GROQ_API_KEY=gsk_your_key_here
JIRA_API_TOKEN=your_jira_token_here
JIRA_EMAIL=your_email@example.com
```

### 3. Build & Run
```bash
# Build the optimized production image
sudo docker build -t sec-agent:prod .

# Run the agent (Listening on Port 5000)
sudo docker run -p 5000:5000 --env-file .env sec-agent:prod
```
*Your AI SOC Analyst is now live and listening.*

---

## 🧪 Verification & Demo Methodology

The demo video showcases two specific methods of testing the pipeline:

### ♦ Method 1: Direct Injection (Fast Triage)
Used in the video to instantly verify the Agent's Python/AI logic without waiting for Splunk indexing.
```bash
# This sends a "True Positive" payload directly to the agent
curl -X POST http://127.0.0.1:5000/webhook \
     -H "Content-Type: application/json" \
     -d '{"result": {"_raw": "Suspicious outbound traffic to 185.196.8.2"}}'
```
*   **Note:** Because this uses `curl` to talk directly to the container, these specific demo events do not appear in Splunk logs. They are used to stress-test the Agent.

### ♦ Method 2: The Real-World Pipeline (End-to-End)
Used to verify the full SOC integration:
1.  **Attacker:** Runs `ssh root@localhost` and fails password.
2.  **OS Log:** Linux writes event to `/var/log/auth.log`.
3.  **Splunk:** Reads the log and fires a Trigger Action (Webhook).
4.  **Agent:** Receives data, analyzes it, and creates the Jira ticket.

---

## 📂 Project Structure
```text
/
├── config/              # Centralized configuration (Allowlists, Thresholds)
├── src/
│   ├── main.py          # Flask Webhook & Gunicorn Entrypoint (The "Engine")
│   └── agent_logic.py   # AI Agent Logic & Llama-3 Instructions (The "Brain")
├── Dockerfile           # Multi-stage production build instruction
├── requirements.txt     # Locked dependencies for stability
└── README.md
```

## ⚖️ Disclaimer
This project is intended for educational and defensive security purposes only. Ensure you have explicit authorization before monitoring networks or automating responses on enterprise infrastructure.
