import streamlit as st
import requests
import uuid
import yaml
from PIL import Image
from io import BytesIO

# ---------------------------------------------------------
# 1. Page & Custom CSS Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Circor Document AI Workbench",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

    /* ── Global Reset & Base ── */
    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
    }

    .stApp {
        background-color: #0d0f14;
        color: #c8cdd8;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background-color: #111318 !important;
        border-right: 1px solid #1f2430;
    }

    [data-testid="stSidebar"] .stTextInput > div > div > input {
        background-color: #1a1d26 !important;
        border: 1px solid #2a2f3e !important;
        border-radius: 6px !important;
        color: #c8cdd8 !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 12px !important;
    }

    [data-testid="stSidebar"] .stSelectbox > div > div {
        background-color: #1a1d26 !important;
        border: 1px solid #2a2f3e !important;
        border-radius: 6px !important;
        color: #c8cdd8 !important;
    }

    /* ── Hide default Streamlit elements ── */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1.5rem !important; padding-bottom: 2rem; }

    /* ── Chat message customization ── */
    [data-testid="stChatMessage"] {
        background-color: #13161f !important;
        border: 1px solid #1e2234 !important;
        border-radius: 10px !important;
        margin-bottom: 10px !important;
        padding: 12px !important;
    }

    [data-testid="stChatMessage"][data-testid*="user"] {
        border-left: 3px solid #3d7eff !important;
    }

    [data-testid="stChatMessage"][data-testid*="assistant"] {
        border-left: 3px solid #00c49a !important;
    }

    /* ── Chat Input ── */
    [data-testid="stChatInput"] > div {
        background-color: #13161f !important;
        border: 1px solid #2a2f3e !important;
        border-radius: 10px !important;
    }

    [data-testid="stChatInput"] textarea {
        color: #c8cdd8 !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
    }

    /* ── Filter Pills ── */
    .filter-bar {
        display: flex;
        gap: 8px;
        align-items: center;
        margin-bottom: 16px;
        flex-wrap: wrap;
    }

    .filter-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        color: #555e75;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-right: 4px;
    }

    .pill {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 500;
        border: 1px solid #2a2f3e;
        color: #6a7490;
        background: #13161f;
        cursor: pointer;
        transition: all 0.18s ease;
        letter-spacing: 0.04em;
    }

    .pill:hover {
        border-color: #3d7eff;
        color: #a0b0ff;
    }

    .pill-active-text {
        background: linear-gradient(135deg, #1a2a4a, #162040);
        border-color: #3d7eff;
        color: #6ba3ff;
        box-shadow: 0 0 12px rgba(61,126,255,0.15);
    }

    .pill-active-table {
        background: linear-gradient(135deg, #0f2e28, #0a2420);
        border-color: #00c49a;
        color: #00c49a;
        box-shadow: 0 0 12px rgba(0,196,154,0.15);
    }

    /* ── Reference Buttons ── */
    .ref-button-container {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-top: 10px;
    }

    /* ── Right Panel ── */
    .context-panel-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 16px;
    }

    .context-title {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 13px;
        color: #8892a8;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #00c49a;
        box-shadow: 0 0 6px #00c49a;
        display: inline-block;
    }

    .status-dot-idle {
        background: #3a3f52;
        box-shadow: none;
    }

    .meta-badge {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 3px 10px;
        border-radius: 4px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        background: #1a1d26;
        border: 1px solid #2a2f3e;
        color: #6a7490;
        margin-bottom: 12px;
    }

    .meta-badge-image {
        border-color: #00c49a44;
        color: #00c49a;
        background: #0f2e28;
    }

    .meta-badge-text {
        border-color: #3d7eff44;
        color: #6ba3ff;
        background: #162040;
    }

    .empty-panel {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 400px;
        opacity: 0.35;
        text-align: center;
    }

    .empty-panel-icon {
        font-size: 48px;
        margin-bottom: 12px;
        filter: grayscale(1);
    }

    .empty-panel-text {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 12px;
        color: #555e75;
        letter-spacing: 0.06em;
    }

    /* ── Page title ── */
    .workbench-title {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 6px;
    }

    .workbench-title h1 {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 22px;
        font-weight: 600;
        color: #d0d8e8;
        letter-spacing: -0.02em;
        margin: 0;
    }

    .workbench-badge {
        background: linear-gradient(135deg, #1a2a4a, #162040);
        border: 1px solid #3d7eff44;
        padding: 2px 10px;
        border-radius: 4px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 10px;
        color: #3d7eff;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }

    .divider {
        border: none;
        border-top: 1px solid #1e2234;
        margin: 12px 0;
    }

    /* ── Sidebar labels ── */
    .sidebar-section-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 10px;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #444c62;
        margin-bottom: 6px;
    }

    /* ── Stbutton override for reference pages ── */
    .stButton > button {
        background-color: #1a1d26 !important;
        border: 1px solid #2a2f3e !important;
        border-radius: 6px !important;
        color: #8892a8 !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 11px !important;
        padding: 4px 10px !important;
        transition: all 0.15s ease !important;
        font-weight: 500 !important;
    }

    .stButton > button:hover {
        background-color: #1e2234 !important;
        border-color: #3d7eff !important;
        color: #6ba3ff !important;
    }

    .stButton > button:active {
        border-color: #00c49a !important;
        color: #00c49a !important;
    }

    /* Close button special style */
    .close-btn > button {
        background: transparent !important;
        border-color: #c94040 !important;
        color: #c94040 !important;
        font-size: 10px !important;
    }

    .close-btn > button:hover {
        background: #2e1515 !important;
        border-color: #ff6060 !important;
        color: #ff6060 !important;
    }

    /* Clear session button */
    .clear-btn > button {
        border-color: #c94040 !important;
        color: #c94040 !important;
        margin-top: 8px;
    }

    /* Filter toggle buttons */
    .filter-toggle > button {
        border-radius: 20px !important;
        font-size: 11px !important;
        padding: 4px 12px !important;
    }

    .filter-toggle-active > button {
        background: linear-gradient(135deg, #162040, #0f2038) !important;
        border-color: #3d7eff !important;
        color: #6ba3ff !important;
    }

    .filter-toggle-active-table > button {
        background: linear-gradient(135deg, #0a2420, #071c18) !important;
        border-color: #00c49a !important;
        color: #00c49a !important;
    }

    /* ── Text area for source ── */
    .stTextArea textarea {
        background-color: #0d0f14 !important;
        border: 1px solid #1e2234 !important;
        border-radius: 8px !important;
        color: #8892a8 !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 12px !important;
        line-height: 1.6 !important;
    }

    /* Column separator */
    [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"] > div:nth-child(2) {
        border-left: 1px solid #1e2234;
        padding-left: 24px;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# 2. Constants & State
# ---------------------------------------------------------
API_URL = "http://localhost:8001/prod/chatbot"

TOOL_MAPPING = {
    "filter_paragraph": {"name": "Paragraph", "icon": "¶", "api_filter": None},
    "filter_table": {"name": "Table", "icon": "⊞", "api_filter": "table"},
}


def extract_clean_url(raw: str) -> str:
    """
    Robustly extract the first valid https URL from any string format:
      - plain URL:        https://...
      - markdown link:   [text](https://...)
      - double-wrapped:  [https://...](https://...)
    Returns the cleaned URL or the original string if no URL found.
    """
    import re
    if not raw:
        return raw
    raw = raw.strip()
    # Markdown / double-wrapped: pick URL inside last (...)
    match = re.search(r'\((https?://[^)]+)\)', raw)
    if match:
        return match.group(1).strip()
    # Plain URL anywhere in string
    match = re.search(r'https?://\S+', raw)
    if match:
        url = match.group(0).strip()
        url = re.sub(r'[)\]>"\',;.]+$', '', url)
        return url
    return raw


def is_image_source(raw: str) -> bool:
    """Return True if source contains an HTTP image URL."""
    import re
    return bool(re.search(r'https?://', raw or ""))

defaults = {
    "messages": [],
    "current_active_filter": "filter_paragraph",
    "context_panel_content": None,
    "s3_link": "",
    "doc_type": "pdf",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ---------------------------------------------------------
# 3. Sidebar
# ---------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-section-label">Document Source</div>', unsafe_allow_html=True)

    s3_link = st.text_input(
        "S3 / HTTPS URL",
        value=st.session_state.s3_link,
        placeholder="s3://bucket/file.pdf or https://...",
        label_visibility="collapsed"
    )
    st.session_state.s3_link = s3_link

    if s3_link:
        st.markdown(f"""
        <div style="margin-top:6px; padding:8px 10px; background:#0f2e28; border:1px solid #00c49a33;
                    border-radius:6px; font-family:'IBM Plex Mono',monospace; font-size:10px; color:#00c49a;
                    word-break:break-all; letter-spacing:0.02em;">
            ✓ {s3_link[:60]}{'...' if len(s3_link) > 60 else ''}
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-label">Document Type</div>', unsafe_allow_html=True)

    doc_type = st.selectbox(
        "Doc Type",
        ["pdf", "docx", "txt", "csv"],
        index=["pdf", "docx", "txt", "csv"].index(st.session_state.doc_type),
        label_visibility="collapsed"
    )
    st.session_state.doc_type = doc_type

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-label">Session</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
        if st.button("⊘  Clear Session", use_container_width=True):
            st.session_state.messages = []
            st.session_state.context_panel_content = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-label">Active Filter</div>', unsafe_allow_html=True)

    current_filter = TOOL_MAPPING[st.session_state.current_active_filter]
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; padding:8px 10px;
                background:#1a1d26; border-radius:6px; border:1px solid #2a2f3e;">
        <span style="font-size:14px">{current_filter['icon']}</span>
        <span style="font-family:'IBM Plex Mono',monospace; font-size:11px; color:#8892a8;">
            {current_filter['name']}
        </span>
        <span style="margin-left:auto; width:6px; height:6px; border-radius:50%; 
                     background:{'#3d7eff' if st.session_state.current_active_filter == 'filter_paragraph' else '#00c49a'};"></span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'IBM Plex Mono',monospace; font-size:10px; color:#333b50; text-align:center; line-height:1.8em;">
        CIRCOR AI WORKBENCH<br>v2.0 · Document Intelligence
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------
# 4. Main Layout
# ---------------------------------------------------------
col_chat, col_context = st.columns([62, 38], gap="large")

# ── Left: Chat ──
with col_chat:
    # Header
    st.markdown("""
    <div class="workbench-title">
        <h1>Document AI Workbench</h1>
        <span class="workbench-badge">Beta</span>
    </div>
    <p style="font-size:12px; color:#444c62; font-family:'IBM Plex Mono',monospace; margin-bottom:16px; letter-spacing:0.04em;">
        RAG-powered document intelligence · Paragraph & Table extraction
    </p>
    """, unsafe_allow_html=True)

    # ── Filter Row ──
    st.markdown('<div class="sidebar-section-label">Response Filter</div>', unsafe_allow_html=True)

    fc1, fc2, fc3 = st.columns([1, 1, 5])
    with fc1:
        is_para = st.session_state.current_active_filter == "filter_paragraph"
        css_class = "filter-toggle filter-toggle-active" if is_para else "filter-toggle"
        st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
        if st.button("¶  Paragraph", use_container_width=True, key="btn_para"):
            st.session_state.current_active_filter = "filter_paragraph"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with fc2:
        is_table = st.session_state.current_active_filter == "filter_table"
        css_class = "filter-toggle filter-toggle-active-table" if is_table else "filter-toggle"
        st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
        if st.button("⊞  Table", use_container_width=True, key="btn_table"):
            st.session_state.current_active_filter = "filter_table"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Validation warning ──
    if not st.session_state.s3_link:
        st.markdown("""
        <div style="padding:10px 14px; background:#1e1510; border:1px solid #c9440033; border-radius:8px;
                    font-family:'IBM Plex Mono',monospace; font-size:11px; color:#c94040; margin-bottom:14px;">
            ⚠  No document URL provided. Add one in the sidebar to start querying.
        </div>
        """, unsafe_allow_html=True)

    # ── Chat History ──
    for msg_idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message["role"] == "assistant" and "results" in message:
                results = message["results"]
                if results:
                    st.markdown(
                        '<div style="font-family:\'IBM Plex Mono\',monospace; font-size:10px; '
                        'color:#444c62; letter-spacing:0.08em; text-transform:uppercase; margin-top:10px;">'
                        '↳ Source References</div>',
                        unsafe_allow_html=True
                    )
                    ref_cols = st.columns(min(len(results), 5))
                    for i, res in enumerate(results):
                        with ref_cols[i % 5]:
                            raw_src = res.get("source", "")
                            is_image = is_image_source(raw_src)
                            clean_url = extract_clean_url(raw_src) if is_image else raw_src
                            icon = "⊞" if is_image else "¶"
                            label = f"{icon} pg.{res['page']}"
                            if st.button(label, key=f"ref_{msg_idx}_{i}"):
                                st.session_state.context_panel_content = {
                                    "type": "image" if is_image else "text",
                                    "data": clean_url,
                                    "page": res["page"],
                                    "status": res.get("status", ""),
                                    "question": res.get("question", message["content"])[:80],
                                    "answer": res.get("answer", "")[:120],
                                }
                                st.rerun()

    # ── Chat Input ──
    if prompt := st.chat_input("Ask about your document…"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        active_filter = TOOL_MAPPING[st.session_state.current_active_filter]["api_filter"]
        payload = {
            "id": str(uuid.uuid4()),
            "query": prompt,
            "document": st.session_state.s3_link,
            "doc_type": st.session_state.doc_type,
            "filter": active_filter,
        }

        with st.chat_message("assistant"):
            if not st.session_state.s3_link:
                st.error("Please provide a document URL in the sidebar.")
            else:
                with st.spinner("Analyzing document…"):
                    try:
                        response = requests.post(API_URL, json=payload, timeout=360)
                        response.raise_for_status()
                        ai_items = response.json().get("ai_response", [])

                        if ai_items:
                            ans = ai_items[0].get("answer", "No answer found.")
                            st.markdown(ans)

                            # Show inline page references immediately
                            if len(ai_items) > 0:
                                st.markdown(
                                    '<div style="font-family:\'IBM Plex Mono\',monospace; font-size:10px; '
                                    'color:#444c62; letter-spacing:0.08em; text-transform:uppercase; margin-top:10px;">'
                                    '↳ Source References</div>',
                                    unsafe_allow_html=True
                                )
                                ref_cols2 = st.columns(min(len(ai_items), 5))
                                msg_idx_new = len(st.session_state.messages)
                                for i, res in enumerate(ai_items):
                                    with ref_cols2[i % 5]:
                                        raw_src = res.get("source", "")
                                        is_image = is_image_source(raw_src)
                                        clean_url = extract_clean_url(raw_src) if is_image else raw_src
                                        icon = "⊞" if is_image else "¶"
                                        if st.button(f"{icon} pg.{res['page']}", key=f"newref_{i}_{uuid.uuid4().hex[:6]}"):
                                            st.session_state.context_panel_content = {
                                                "type": "image" if is_image else "text",
                                                "data": clean_url,
                                                "page": res["page"],
                                                "status": res.get("status", ""),
                                                "question": res.get("question", prompt)[:80],
                                                "answer": res.get("answer", "")[:120],
                                            }
                                            st.rerun()

                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": ans,
                                "results": ai_items,
                            })
                        else:
                            st.warning("No results returned from the API.")
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": "No results returned.",
                                "results": [],
                            })
                    except requests.exceptions.ConnectionError:
                        err = "Cannot connect to the API. Ensure the backend is running at `localhost:8001`."
                        st.error(err)
                        st.session_state.messages.append({"role": "assistant", "content": err, "results": []})
                    except Exception as e:
                        err = f"Error: {e}"
                        st.error(err)
                        st.session_state.messages.append({"role": "assistant", "content": err, "results": []})


# ── Right: Context Panel ──
with col_context:
    content = st.session_state.context_panel_content

    # Panel header
    has_content = content is not None
    dot_class = "status-dot" if has_content else "status-dot-idle"
    st.markdown(f"""
    <div class="context-panel-header">
        <span class="{dot_class}"></span>
        <span class="context-title">Context Viewer</span>
    </div>
    """, unsafe_allow_html=True)

    if not has_content:
        st.markdown("""
        <div class="empty-panel">
            <div class="empty-panel-icon">⬡</div>
            <div class="empty-panel-text">
                Select a page reference<br>from a response to view source
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        # Meta info
        is_img = content["type"] == "image"
        badge_class = "meta-badge meta-badge-image" if is_img else "meta-badge meta-badge-text"
        badge_icon = "⊞ TABLE EXTRACT" if is_img else "¶ PARAGRAPH TEXT"

        st.markdown(f"""
        <div class="{badge_class}">{badge_icon}</div>
        <div style="font-family:'IBM Plex Mono',monospace; font-size:10px; color:#3a3f52; margin-bottom:8px;">
            PAGE {content['page']}
            {' · ' + content['status'] if content.get('status') else ''}
        </div>
        """, unsafe_allow_html=True)

        # Query summary
        if content.get("question"):
            st.markdown(f"""
            <div style="padding:8px 12px; background:#13161f; border-left:3px solid #2a2f3e;
                        border-radius:0 6px 6px 0; margin-bottom:12px;">
                <div style="font-family:'IBM Plex Mono',monospace; font-size:9px; color:#444c62;
                            text-transform:uppercase; letter-spacing:0.1em; margin-bottom:4px;">Query</div>
                <div style="font-size:12px; color:#8892a8; line-height:1.5;">{content['question']}</div>
            </div>
            """, unsafe_allow_html=True)

        # Close button
        st.markdown('<div class="close-btn">', unsafe_allow_html=True)
        if st.button("✕  Close", use_container_width=False):
            st.session_state.context_panel_content = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        # Content display
        if is_img:
            # URL was already cleaned at capture time — just use it
            img_url = content["data"]

            # Debug expander so devs can inspect the URL if needed
            with st.expander("🔗 Image URL", expanded=False):
                st.code(img_url, language=None)

            with st.spinner("Loading image…"):
                img_loaded = False
                err_msg = ""

                # Strategy 1: standard GET with browser-like headers
                if not img_loaded:
                    try:
                        headers = {
                            "User-Agent": "Mozilla/5.0 (compatible; CircorWorkbench/2.0)",
                            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
                        }
                        session = requests.Session()
                        resp = session.get(img_url, headers=headers, timeout=20, allow_redirects=True)
                        resp.raise_for_status()

                        # Validate content is actually an image
                        content_type = resp.headers.get("Content-Type", "")
                        if "image" in content_type or len(resp.content) > 1000:
                            img = Image.open(BytesIO(resp.content))
                            st.image(img, caption=f"Page {content['page']} · Table Extract", use_container_width=True)
                            img_loaded = True
                        else:
                            err_msg = f"Unexpected content-type: {content_type}"
                    except Exception as e:
                        err_msg = str(e)

                # Strategy 2: st.image with direct URL (let browser fetch it — works if URL is public)
                if not img_loaded:
                    try:
                        st.image(img_url, caption=f"Page {content['page']} · Table Extract", use_container_width=True)
                        img_loaded = True
                    except Exception as e2:
                        err_msg = f"{err_msg} | direct: {str(e2)}"

                if not img_loaded:
                    st.markdown(f"""
                    <div style="padding:14px; background:#1e1510; border:1px solid #c9440033;
                                border-radius:8px; font-family:'IBM Plex Mono',monospace; font-size:11px; color:#c94040;">
                        ✗ Image could not be loaded<br>
                        <span style="color:#555e75; font-size:10px;">{err_msg[:180]}</span>
                    </div>
                    <div style="margin-top:8px; padding:6px 10px; background:#13161f; border-radius:6px;
                                font-family:'IBM Plex Mono',monospace; font-size:9px; color:#444c62; line-height:1.6em;">
                        This may be a presigned S3 URL that has expired.<br>
                        Re-query the document to get a fresh signed URL.
                    </div>
                    """, unsafe_allow_html=True)

            # Answer summary below image — always show if available
            if content.get("answer"):
                st.markdown(f"""
                <div style="margin-top:12px; padding:10px 12px; background:#13161f;
                            border:1px solid #1e2234; border-radius:8px;">
                    <div style="font-family:'IBM Plex Mono',monospace; font-size:9px; color:#444c62;
                                text-transform:uppercase; letter-spacing:0.1em; margin-bottom:6px;">AI Summary</div>
                    <div style="font-size:12px; color:#8892a8; line-height:1.6;">{content['answer']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.text_area(
                "Source Text",
                value=content["data"],
                height=480,
                label_visibility="collapsed"
            )

            if content.get("answer"):
                st.markdown(f"""
                <div style="margin-top:12px; padding:10px 12px; background:#13161f;
                            border:1px solid #1e2234; border-radius:8px;">
                    <div style="font-family:'IBM Plex Mono',monospace; font-size:9px; color:#444c62;
                                text-transform:uppercase; letter-spacing:0.1em; margin-bottom:6px;">AI Summary</div>
                    <div style="font-size:12px; color:#8892a8; line-height:1.6;">{content['answer']}</div>
                </div>
                """, unsafe_allow_html=True)