# 🛡️ AI-Powered SOAR Engine: Splunk ➡️ Jira ➡️ Agno (Llama 3)
> **Agentic Security Incident Response & Threat Enrichment Pipeline**

## 🎥 Project Demo (V3 Architecture)
**[CLICK HERE TO WATCH THE DEMO VIDEO](PASTE_YOUR_EXISTING_VIDEO_LINK_HERE)**

> **⚠️ NOTE: V4 AI Upgrade Released!**
> The video above demonstrates the V3 Automation Logic (Auto-Close vs Escalate). 
> **This repository has since been upgraded to V4**, which integrates an **AI Agent (Agno/Phidata + Groq)** to perform intelligent OSINT investigations on threat actors.
> *A new demo video showcasing the AI Agent's reasoning capabilities is coming soon.*

---

## 📝 Project Overview
This project evolves the traditional SOC playbook from "Automation" to "Agentic Intelligence."

Originally built to handle high-volume brute-force alerts from **Splunk Enterprise**, the engine uses a **Python Middleware** to ingest Webhooks. In **Version 4**, I integrated an autonomous AI Agent (**Agno/Llama-3**) to act as a Tier 1 Analyst. The Agent actively investigates source IPs, determines context (Private vs Public network), scans for threat reputation, and writes a human-readable investigation report directly into the **Jira** ticket.

### 🧠 V4.0 Agentic Capabilities
*   **🤖 AI Analyst Integration:** Utilizes **Agno (formerly Phidata)** running the **Llama-3-70b** model via **Groq LPU** for sub-second inference.
*   **🔍 Autonomous Investigation:** The Agent distinguishes between internal authorized scans (Private IPs) and external threats. It performs web searches (DuckDuckGo) to validate reputation.
*   **📝 Natural Language Reporting:** Instead of dumping raw JSON logs, the system creates Jira tickets with a written "Analyst Report" summarizing the findings.

### ⚡ Core Automation Features
*   **Self-Healing Triage:** False Positives (Whitelist/Internal IPs) are auto-ticketed and immediately transitioned to **DONE** (Closed) to prevent analyst fatigue.
*   **Loop Prevention:** Splunk alerting optimized with precise cron scheduling (`-1m@m`) to eliminate duplicate alerts for the same event.

## 🏗️ Architecture Flow (V4)
```mermaid
graph TD
    A[Attacker] -->|SSH Brute Force| B(Kali Linux Logs)
    B -->|Splunk Monitor| C{Splunk Enterprise}
    C -->|Webhook Alert| D[Python SOAR Engine]
    
    subgraph "The AI Brain (Agno + Groq)"
        D -->|Send IP & Context| E{AI Agent (Llama 3)}
        E -->|Reasoning Process| F[Check Context / OSINT]
        F -->|Return Analysis| D
    end
    
    D -- Analysis = Safe --> G[Auto-Close Ticket]
    D -- Analysis = Threat --> H[Escalate to High Priority]
    
    G -->|API| I[Jira Board: DONE]
    H -->|API + AI Report| J[Jira Board: TO DO]

🛠️ Tech Stack
SIEM: Splunk Enterprise 10.x
AI Framework: Agno (Phidata)
LLM Engine: Groq API (Llama-3.3-70b-versatile)
Development: Python 3 (Flask, Requests, RegEx)
Infrastructure: Kali Linux, Jira Cloud API
🔧 Installation & Usage
Clone the Repo:
code
Bash
git clone https://github.com/Naifnizami/SOAR-EDR-Automation-Lab.git
cd SOAR-EDR-Automation-Lab
Install Requirements:
code
Bash
pip install -r requirements.txt
Configure Credentials:
Set your JIRA_API_TOKEN and GROQ_API_KEY as environment variables (Recommended) or update the soar_engine.py / ai_analyst.py config sections locally.
Run the Engine:
code
Bash
python3 soar_engine.py
Configure Splunk: Point Webhook action to http://<your-ip>:5000/webhook.
Developed by Naif Nizami - 2026
