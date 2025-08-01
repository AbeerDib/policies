from flask import Flask, request, send_file
import streamlit as st
import requests
import uuid

st.set_page_config(page_title="Policy Document Assistant", page_icon="📄")

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "uploaded_files" not in st.session_state:
    st.session_state["uploaded_files"] = []

st.title("📄 Policy Document Chatbot")
st.caption("Ask me to generate, review, or edit policy documents — privacy, refund, GDPR, ToS, etc.")

# Upload area (shown above chat)
uploaded_files = st.file_uploader("📁 Upload related documents (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"], accept_multiple_files=True)
if uploaded_files:
    st.session_state["uploaded_files"] = uploaded_files

# Show chat history
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Get user input
if prompt := st.chat_input("What policy do you want to generate?"):
    # Show user's message
    st.chat_message("user").markdown(prompt)
    st.session_state["messages"].append({"role": "user", "content": prompt})

    # Prepare webhook payload
    payload = {
        "message": prompt,
        "session_id": st.session_state["session_id"],
        "source": "policy-chatbot"
    }

    files = []
    for file in st.session_state["uploaded_files"]:
        files.append(("files", (file.name, file.getvalue())))

    try:
        #webhook_url = "https://5665bc9c4901.ngrok-free.app/webhook/94e66a1d-abd1-48ca-a081-02f952c79d47 "
        #webhook_url ="http://localhost:5678/webhook/94e66a1d-abd1-48ca-a081-02f952c79d47"  # 🔁 Replace with your n8n webhook
        webhook_url ="https://dib-99.app.n8n.cloud/webhook/94e66a1d-abd1-48ca-a081-02f952c79d47"
        if files:
            response = requests.post(webhook_url, data=payload, files=files)
        else:
            response = requests.post(webhook_url, json=payload)

        response.raise_for_status()
        
        response_json = response.json()
        if isinstance(response_json, list):
            response_json = response_json[0]  # Take the first item if it's a list

        reply = response_json.get("reply", "⚠️ No reply received from n8n.")


        st.chat_message("assistant").markdown(reply)
        st.session_state["messages"].append({"role": "assistant", "content": reply})

    except Exception as e:
        error_msg = f"⚠️ Error: {e}"
        st.chat_message("assistant").markdown(error_msg)
        st.session_state["messages"].append({"role": "assistant", "content": error_msg})
