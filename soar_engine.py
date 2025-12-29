from flask import Flask, request, jsonify
import requests
import json
import re
from datetime import datetime

app = Flask(__name__)

# ==========================================
# ⬇️ CONFIGURATION: UPDATED ONE LAST TIME ⬇️
# =========================================
JIRA_URL = "https://YOUR-DOMAIN.atlassian.net"
JIRA_EMAIL = "your-email@example.com"
JIRA_API_TOKEN = "os.environ.get('JIRA_API_TOKEN')" # For security, use env vars or secret manager
PROJECT_KEY = "KAN"
# ==========================================

# Known "Safe" IPs (Your Kali VM)
WHITELIST_IPS = ["127.0.0.1", "localhost", "0.0.0.0"]

def close_ticket(issue_key):
    """
    Finds the transition ID for 'Done' and moves the ticket there.
    """
    url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/transitions"
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    
    try:
        # 1. Ask Jira: "What transitions are possible for this ticket?"
        r = requests.get(url, auth=auth, headers=headers)
        transitions = r.json().get("transitions", [])
        
        # 2. Find the ID for "Done"
        done_id = None
        for t in transitions:
            if t['name'] == "Done":
                done_id = t['id']
                break
        
        # 3. Move the ticket
        if done_id:
            payload = json.dumps({"transition": {"id": done_id}})
            move_req = requests.post(url, auth=auth, headers=headers, data=payload)
            if move_req.status_code == 204:
                print(f"[✅] SUCCESS: Ticket {issue_key} moved to DONE.")
            else:
                print(f"[-] Move Failed: {move_req.text}")
        else:
            print("[-] Error: Could not find a 'Done' transition step in Jira.")

    except Exception as e:
        print(f"[-] Auto-Close Error: {e}")

def create_issue(source_ip, alert_name, is_fp):
    url = f"{JIRA_URL}/rest/api/3/issue"
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    # Dynamic Title & Severity
    if is_fp:
        summary = f"[FP] Authorized Scan Detected - {source_ip}"
        priority = "Low"
        decision_text = "FALSE POSITIVE (Authorized)"
    else:
        summary = f"🚨 [TP] THREAT DETECTED: {alert_name} - {source_ip}"
        priority = "High"
        decision_text = "TRUE POSITIVE (Escalate)"

    description_body = (
        f"**SOC Automation Report**\n"
        f"-----------------------\n"
        f"**Alert:** {alert_name}\n"
        f"**Source:** {source_ip}\n"
        f"**Analysis:** {decision_text}\n"
        f"**Action Taken:** {'Auto-Closing Ticket' if is_fp else 'Analyst Assigned'}\n"
        f"-----------------------\n"
        f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    payload = json.dumps({
        "fields": {
            "project": {"key": PROJECT_KEY},
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [{
                    "type": "paragraph",
                    "content": [{"type": "text", "text": description_body}]
                }]
            },
            "issuetype": {"name": "Task"},
            # "priority": {"name": priority} # Keep commented unless you configured Priorities in Jira
        }
    })

    try:
        r = requests.post(url, headers=headers, data=payload, auth=auth)
        if r.status_code == 201:
            key = r.json().get("key")
            print(f"[+] Ticket Created: {key} ({decision_text})")
            return key
        else:
            print(f"[-] Create Error: {r.text}")
            return None
    except Exception as e:
        print(f"[-] Connection Error: {e}")

@app.route('/webhook', methods=['POST'])
def receive_alert():
    data = request.json
    
    # 1. Safe IP Extraction (Regex)
    result = data.get("result", {})
    raw_log = result.get("_raw", "") or str(result)
    # This Regex finds standard IP addresses
    ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', raw_log)
    
    if ip_match:
        ip = ip_match.group(1)
    else:
        ip = "Unknown IP"
    
    # 2. Logic: False Positive?
    is_false_positive = False
    if ip in WHITELIST_IPS:
        is_false_positive = True
        
    # 3. Execution
    ticket_key = create_issue(ip, "Brute Force", is_false_positive)
    
    # 4. Auto-Close if FP
    if ticket_key and is_false_positive:
        close_ticket(ticket_key)
        
    return jsonify({"status": "received"}), 200

if __name__ == '__main__':
    print("🚀 SOAR ENGINE V3: AUTO-CLOSE ENABLED")
    app.run(host='0.0.0.0', port=5000)
