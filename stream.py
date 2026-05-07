import streamlit as st
import requests
import uuid

# Configuration
API_URL = "https://circor-backend-ai.eziosolutions.com/prod/chatbot"

st.set_page_config(page_title="Document AI Explorer", page_icon="🤖", layout="wide")
st.title("Document AI Explorer")

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar for metadata
with st.sidebar:
    st.header("Document Settings")
    s3_link = st.text_input("S3 Bucket Link", placeholder="s3://bucket-name/file.pdf")
    doc_type = st.selectbox("Doc Type", ["pdf", "docx", "txt", "csv"])
    
    # Updated Filter as a selectable dropdown
    filter_option = st.selectbox(
        "Response Filter", 
        [None, "table"],
        help="Select a specific lens for the AI response"
    )
    
    st.divider()
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "results" in message:
            for res in message["results"]:
                with st.expander(f"Source: Page {res['page']} ({res['status']})"):
                    st.write(res['answer'])
                    if "http" in res['source']:
                        st.image(res['source'], caption=f"Extracted Table - Page {res['page']}")
                    else:
                        st.caption(res['source'])

# User Input
if prompt := st.chat_input("What is the document about?"):
    # 1. Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Build Request Payload matching your new schema
    payload = {
        "id": str(uuid.uuid4()),
        "query": prompt,
        "document": s3_link,
        "doc_type": doc_type,
        "filter": filter_option
    }

    # 3. Call API
    with st.chat_message("assistant"):
        if not s3_link:
            st.error("Please provide an S3 link in the sidebar.")
        else:
            with st.spinner("Analyzing document..."):
                try:
                    response = requests.post(API_URL, json=payload)
                    response.raise_for_status()
                    result = response.json()

                    # result["ai_response"] is now a list of dictionaries
                    ai_items = result.get("ai_response", [])

                    if not ai_items:
                        st.warning("No data found for this query.")
                    else:
                        # Display primary answer first
                        main_answer = ai_items[0]["answer"]
                        st.markdown(main_answer)
                        
                        # Display detailed breakdown in Expanders
                        for item in ai_items:
                            with st.expander(f"🔍 Detail - Page {item['page']} (Status: {item['status']})"):
                                st.markdown(item["answer"])
                                
                                # Handle Source (could be text or an S3 Image URL)
                                if "http" in item["source"]:
                                    st.image(item["source"], caption=f"Reference Image from Page {item['page']}")
                                else:
                                    st.info(f"Note: {item['source']}")

                        # Save to History
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": main_answer,
                            "results": ai_items # Store full objects for re-rendering
                        })
                except Exception as e:
                    st.error(f"Connection Error: {str(e)}")