# 🛡️ SOAR-EDR Automation Lab: Splunk ➡️ Jira Integration

## 🎥 Project Demo
**Automated Triage & Response in Action (Wait for video to load):**

### 🎬 [Click Here to Watch the Demo Video](./SOC%20Project.mp4)
*(Note: For the best view of terminal commands, we recommend downloading the raw video file using the 'Download' button on the next page).*

## 📝 Project Overview
This project simulates a corporate SOC environment handling high-volume alerts. I engineered a solution to automate the Triage phase, which typically consumes 40% of an analyst's day. By integrating **Splunk Enterprise** (Detection) with **Jira** (Response) via a custom **Python Middleware**, I achieved fully automated Ticket creation and closure.

### ⚡ Key Capabilities
*   **Ingestion:** Python Flask listener captures Webhooks from Splunk in real-time.
*   **Enrichment:** Middleware extracts attacker IPs using Regex (`src_ip`) and parses log payloads.
*   **Decision Logic:** 
    *   **False Positive:** If IP is in `Whitelist` (e.g. Authorized Scanners), the ticket is created and **Auto-Closed**.
    *   **True Positive:** If IP is unauthorized, the ticket is created with **High Priority** and Analyst assignment.
*   **Loop Prevention:** Optimized Splunk Search scheduling (Cron `-1m@m`) to eliminate duplicate alert firing.

## 🏗️ Architecture Flow
```mermaid
graph TD
    A[Attacker/Scanner] -->|SSH Brute Force| B(Kali Linux Logs)
    B -->|Monitor| C{Splunk Enterprise}
    C -->|Trigger Alert| D[Python Middleware]
    
    subgraph "Logic Engine"
        D --> E{IP Whitelisted?}
        E -- Yes --> F[Action: Auto-Close]
        E -- No --> G[Action: Escalate Severity]
    end
    
    F -->|API POST| H[Jira Ticket: DONE]
    G -->|API POST| I[Jira Ticket: TO DO]
