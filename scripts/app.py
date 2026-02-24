import streamlit as st
import re
import time
import os
import aegis_detect  # Import your logic

# --- UI CONFIGURATION ---
st.set_page_config(page_title="Aegis AI Red-Team", page_icon="🛡️", layout="wide")

# --- CUSTOM CSS FOR TERMINAL LOOK ---
st.markdown("""
    <style>
    .terminal {
        background-color: #0e1117;
        color: #00ff00;
        font-family: 'Courier New', Courier, monospace;
        padding: 10px;
        border-radius: 5px;
        height: 300px;
        overflow-y: scroll;
        border: 1px solid #444;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ Aegis: Autonomous Red-Team Dashboard")
st.markdown("Automated Adversarial Intelligence powered by Azure AI Foundry.")

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.header("Settings")
    target_url = st.text_input("Target URL", value=os.environ.get("TARGET_URL"))
    start_btn = st.button("🚀 Start Attack Loop", use_container_width=True)

    st.divider()
    st.subheader("🕵️ Live Agent Logs")
    log_container = st.empty() # Placeholder for streaming logs
    log_history = []

# --- DASHBOARD LAYOUT ---
col1, col2 = st.columns([1, 1])

if start_btn:
    # Function to update logs in the UI
    def update_logs(message, type="info"):
        timestamp = time.strftime("%H:%M:%S")
        color = "#00ff00" if type == "info" else "#ff4b4b"
        log_entry = f"[{timestamp}] {message}"
        log_history.append(log_entry)
        # Display the last 10 logs in a terminal-like box
        log_container.markdown(f"```text\n" + "\n".join(log_history[-15:]) + "\n```")

    with st.status("Running Security Audit...", expanded=True) as status:
        update_logs("Initializing Azure AI Project Client...")
        update_logs(f"Targeting: {target_url}")
        # Placeholder for your actual logic call
        report_md, score = aegis_detect.main(log_callback=update_logs) 
        status.update(label="Audit Complete!", state="complete", expanded=False)

    with col1:
        st.subheader("Security Risk Score")
        # Display large metric
        color = "red" if score >= 7 else "orange" if score >= 4 else "green"
        st.markdown(f"<h1 style='text-align: center; color: {color}; font-size: 80px;'>{score}/10</h1>", unsafe_allow_html=True)
        st.progress(score / 10)
        
        st.subheader("Attack Flow Visualization")
        # Mermaid Diagram in Streamlit
        st.markdown(f"""
        ```mermaid
        graph TD
            A[Recon Agent] -->|Maps| B[Attacker Agent]
            B -->|Exploits| C[Target API]
            C -->|Evidence| D[Reporter Agent]
            D -->|Grades| E[Score: {score}]
        ```
        """)

    with col2:
        st.subheader("Detailed Vulnerability Report")
        st.markdown(report_md)

else:
    st.info("Enter a Target URL in the sidebar and click 'Start' to begin the audit.")