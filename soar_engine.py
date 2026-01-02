from flask import Flask, request, jsonify
import requests
import json
import re
from datetime import datetime
import ai_analyst  # <--- IMPORTING THE BRAIN

app = Flask(__name__)

# ============================
# ⬇️ JIRA CONFIGURATION ⬇️
# ============================
JIRA_URL = "https://nifunaif612181.atlassian.net"
JIRA_EMAIL = "nifunaif612181@gmail.com"
JIRA_API_TOKEN = os.environ.get('JIRA_API_TOKEN')
PROJECT_KEY = "KAN"
# ============================

# Whitelist (Your VM Localhost) - Auto Close these
WHITELIST_IPS = ["127.0.0.1", "localhost"]

def close_ticket(issue_key):
    """Auto-closes False Positive tickets"""
    url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/transitions"
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    
    try:
        # Find the 'Done' transition ID dynamically
        r = requests.get(url, auth=auth, headers=headers)
        transitions = r.json().get("transitions", [])
        
        done_id = None
        for t in transitions:
            if t['name'] == "Done":
                done_id = t['id']
                break
        
        if done_id:
            payload = json.dumps({"transition": {"id": done_id}})
            requests.post(url, auth=auth, headers=headers, data=payload)
            print(f"[✅] Auto-Closed Ticket {issue_key}")
            
    except Exception as e:
        print(f"[-] Auto-Close Failed: {e}")

def create_issue(source_ip, alert_name, is_fp):
    url = f"{JIRA_URL}/rest/api/3/issue"
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    # --- 🧠 THE AI LOGIC ---
    if is_fp:
        # False Positive (Cheap & Fast)
        summary = f"[FP] Authorized Scan - {source_ip}"
        priority = "Low"
        description_text = (
            "**Status:** False Positive\n"
            "**Action:** Auto-Closed via AllowList."
        )
    else:
        # True Positive (Ask Agno for Intelligence)
        print("    ⚡ Invoking AI Analyst for Investigation...")
        summary = f"🚨 [TP] THREAT - {source_ip}"
        priority = "High"
        
        # Call the Agent!
        ai_report = ai_analyst.investigate_ip(source_ip, alert_name)
        
        description_text = (
            f"**⚠️ SOC AI INVESTIGATION REPORT**\n"
            f"-----------------------------------\n"
            f"**Alert:** {alert_name}\n"
            f"**Target:** {source_ip}\n\n"
            f"{ai_report}\n" # <--- INSERTING AI BRAIN HERE
            f"-----------------------------------\n"
            f"**Status:** Escalated for Human Review."
        )

    # Payload Construction
    payload = json.dumps({
        "fields": {
            "project": {"key": PROJECT_KEY},
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [{
                    "type": "paragraph",
                    "content": [{"type": "text", "text": description_text}]
                }]
            },
            "issuetype": {"name": "Task"},
            # "priority": {"name": priority}
        }
    })

    # API Request
    try:
        r = requests.post(url, headers=headers, data=payload, auth=auth)
        if r.status_code == 201:
            key = r.json().get("key")
            print(f"[+] Ticket Created: {key}")
            return key
        else:
            print(f"[-] Jira Error: {r.text}")
            return None
    except Exception as e:
        print(f"[-] Connect Error: {e}")
        return None

@app.route('/webhook', methods=['POST'])
def receive_alert():
    data = request.json
    raw_log = str(data.get("result", {}).get("_raw", ""))
    
    # Extract IP
    ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', raw_log)
    ip = ip_match.group(1) if ip_match else "Unknown"
    
    # Logic Check
    is_fp = ip in WHITELIST_IPS
    
    print(f"\n[!] Alert Received: {ip} | Type: {'FP' if is_fp else 'TP'}")
    
    # Execute Workflow
    ticket = create_issue(ip, "SSH Brute Force", is_fp)
    
    if is_fp and ticket:
        close_ticket(ticket)

    return jsonify({"status": "received"}), 200

if __name__ == '__main__':
    print("🚀 AI-POWERED SOAR ENGINE READY (Groq Llama 3.3)...")
    app.run(host='0.0.0.0', port=5000)
