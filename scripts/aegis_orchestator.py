import os
import time
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
import re
from dotenv import load_dotenv

load_dotenv()

RECON_AGENT_ID = os.environ.get("RECON_AGENT_ID")
ATTACK_AGENT_ID = os.environ.get("ATTACK_AGENT_ID")
REPORT_AGENT_ID = os.environ.get("REPORT_AGENT_ID")

# The NGROK target url to scan - set this in your .env file before running the script
TARGET_URL = os.environ.get("TARGET_URL")

# Initialize Project Client
project_client = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint=os.environ.get("ENDPOINT")
)

def run_agent_step(thread_id, agent_id, agent_name, user_request):
    """Helper to send a message and wait for the agent to finish."""
    project_client.agents.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_request
    )
    print(f"🚀 Running Agent {agent_name}...")
    run = project_client.agents.runs.create_and_process(thread_id=thread_id, agent_id=agent_id)
    
    # Return the latest message from this agent
    messages = project_client.agents.messages.get_last_message_text_by_role(thread_id=thread_id, role="assistant")
    return messages.text.value

def extract_score(report_text):
    """Simple regex to find the numeric score in the agent's markdown."""
    scores = re.findall(r"OVERALL SECURITY RISK:[^\d]*([\d\.]+)",report_text, flags=re.IGNORECASE | re.DOTALL)

    if scores:
        # Convert to float and take the highest (worst) score
        return max([float(s) for s in scores])
    return 0.0

def main(log_callback=None):
    # 1. Create a shared Thread for the entire loop
    thread = project_client.agents.threads.create()
    print(f"🧵 Created Thread: {thread.id}")
    # 1. Start Recon
    if log_callback:
        log_callback(f"Phase 1: Starting Recon on {TARGET_URL}")
    # --- PHASE 1: RECONNAISSANCE ---
    recon_output = run_agent_step(
        thread.id, 
        RECON_AGENT_ID, 
        "Recon Agent",
        f"Perform a deep recon on {TARGET_URL}. Use Bing to find OpenAPI specs and list all endpoints."
    )
    print(f"\n📡 [RECON COMPLETED]\n{recon_output}\n...")
    if log_callback:
        log_callback(f"📡 [RECON COMPLETED]\n{recon_output}\n...")

    # 2. Simulate Attack
    if log_callback:
        log_callback("Phase 2: Adversarial Agent engaged.")
        log_callback("CALLING: TargetApiTool.get_user_by_id(user_id='99')")

    # --- PHASE 2: ATTACK LOOP ---
    attack_output = run_agent_step(
        thread.id,
        ATTACK_AGENT_ID,
        "Attack Agent",
        "Based on the recon, start the attack loop. Try IDOR on user IDs and test for debug headers."
    )
    print(f"\n💥 [ATTACK COMPLETED]\n{attack_output}\n...")
    time.sleep(1) # For dramatic effect in the UI
    if log_callback:
        log_callback(f"\n💥 [ATTACK COMPLETED]\n{attack_output}\n...")

    # --- PHASE 3: REPORTING ---
    # We ask the Reporter to look at the WHOLE thread and summarize
    final_report = run_agent_step(
        thread.id,
        REPORT_AGENT_ID,
        "Report Agent",
        "Review the entire conversation. Identify any successful breaches and generate a formal Vulnerability Report in Markdown."
    )
    # Extract the score for a "Grand Finale" display
    numeric_risk = extract_score(final_report)

    if log_callback:
        log_callback("Phase 3: Generating final risk assessment...")
    
    # Determine the "Grade"
    if numeric_risk >= 7:
        status = "🔴 CRITICAL"
    elif numeric_risk >= 4:
        status = "🟠 WARNING"
    else:
        status = "🟢 SECURE"

    # --- FINAL OUTPUT ---
    print("\n" + "="*60)
    print("🛡️  AEGIS FINAL SECURITY AUDIT REPORT")
    print("="*60)
    print(final_report)
    print(f"\nOverall Security Status: {status}")
    # Save to file for the hackathon submission
    with open("./reports/security_report.md", "w",  encoding="utf-8") as f:
        f.write(final_report)
    print("\n✅ Report saved to security_report.md")
    return final_report, numeric_risk

if __name__ == "__main__":
    main()