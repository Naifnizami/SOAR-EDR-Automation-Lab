from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.duckduckgo import DuckDuckGoTools
import os

# ==========================================
# 🔑 CONFIGURATION
# ==========================================
# Fetch key from environment variable for security
os.environ["GROQ_API_KEY"] = os.environ.get("GROQ_API_KEY") 
# ==========================================

# 1. Define the AI Agent (Using Llama 3 via Groq)
soc_agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile"), 
    tools=[DuckDuckGoTools()],
    description="You are an expert SOC Analyst. Your job is to enrich alert data.",
    instructions=[
        "You will be given a Source IP and an Alert Type.",
        "1. Identify if the IP is Public or Private (Local).",
        "2. If Public, use DuckDuckGo to search for recent threat intelligence or reputation.",
        "3. Decide: Is this a False Positive (Safe) or True Positive (Threat)?",
        "4. Output your finding as a concise paragraph.",
    ],
    markdown=True
    # The 'show_tool_calls' line is removed
)

# 2. Function to be called by your main script
def investigate_ip(ip, alert_name):
    query = f"Investigate this IP: {ip}. The alert is: {alert_name}"
    try:
        # Ask the AI
        print(f"    🤖 AI is thinking about {ip}...")
        response = soc_agent.run(query)
        return response.content
    except Exception as e:
        return f"AI Error: {str(e)}"

# 3. Quick Test (Only runs if you run this file directly)
if __name__ == "__main__":
    print("\n--- TEST MODE ---")
    # We test with a known Google DNS IP just to see if it speaks
    print(investigate_ip("8.8.8.8", "DNS Modification"))
