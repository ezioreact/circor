import streamlit as st
import requests
import uuid

# Configuration
API_URL = "http://localhost:8001/prod/chatbot"

st.set_page_config(page_title="AI Chatbot", page_icon="🤖")
st.title("Document AI Explorer")

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar for metadata
with st.sidebar:
    st.header("Document Settings")
    s3_link = st.text_input("S3 Bucket Link", placeholder="s3://bucket-name/file.pdf")
    doc_type = st.selectbox("Doc Type", ["pdf", "docx", "txt", "csv"])
    st.divider()
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("pages"):
            st.caption(f"Sources: Page(s) {', '.join(message['pages'])}")

# User Input
if prompt := st.chat_input("What is the document about?"):
    # 1. Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Build Request Payload (Matches your chat_ai_Request model)
    payload = {
        "id": str(uuid.uuid4()),
        "query": prompt,
        "document": s3_link,
        "doc_type": doc_type
    }

    # 3. Call API
    with st.chat_message("assistant"):
        if not s3_link:
            st.error("Please provide an S3 link in the sidebar.")
        else:
            with st.spinner("Processing document..."):
                try:
                    response = requests.post(API_URL, json=payload)
                    response.raise_for_status()
                    result = response.json()

                    # Extract data based on your chat_ai_Response model
                    answer = result.get("ai_response", "")
                    pages = result.get("page", [])

                    # Display UI
                    st.markdown(answer)
                    if pages:
                        st.caption(f"Sources: Page(s) {', '.join(pages)}")

                    # Save to History
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "pages": pages
                    })
                except Exception as e:
                    st.error(f"Connection Error: {str(e)}")