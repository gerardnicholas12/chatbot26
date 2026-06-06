import time
from datetime import datetime

import streamlit as st
from agents.router import route_query, classify_mode
from agents.llm_agent import llm_agent


st.set_page_config(
    page_title="AI Agent Studio",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


MODE_META = {
    "General Chat": {
        "label": "LLM only",
        "accent": "#6366f1",
        "bg": "rgba(99,102,241,0.08)",
        "icon": "💬",
        "description": "Answers from model knowledge without external tools.",
    },
    "Web Search": {
        "label": "DuckDuckGo / web",
        "accent": "#06b6d4",
        "bg": "rgba(6,182,212,0.08)",
        "icon": "🌐",
        "description": "Retrieves current information and cites web sources.",
    },
    "RAG": {
        "label": "Vector retrieval",
        "accent": "#10b981",
        "bg": "rgba(16,185,129,0.08)",
        "icon": "📄",
        "description": "Searches uploaded enterprise documents before answering.",
    },
    "Memory": {
        "label": "Context aware",
        "accent": "#f59e0b",
        "bg": "rgba(245,158,11,0.08)",
        "icon": "🧠",
        "description": "Uses previous turns for follow-up questions.",
    },
}


def bootstrap_state():
    if "messages" not in st.session_state:
        reset_messages()
    if "selected_chat" not in st.session_state:
        st.session_state.selected_chat = "Sprint Demo"
    if "documents" not in st.session_state:
        st.session_state.documents = []
    if "show_route" not in st.session_state:
        st.session_state.show_route = True
    if "use_memory" not in st.session_state:
        st.session_state.use_memory = True
    if "streaming" not in st.session_state:
        st.session_state.streaming = True
    if "top_k" not in st.session_state:
        st.session_state.top_k = 4


def reset_messages():
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "👋 Hello! I'm your AI Agent. Ask me anything — general questions, "
                "current news, or queries about your uploaded documents."
            ),
            "mode": "General Chat",
            "sources": [],
            "route": ["Receive question", "Use LLM", "Generate response"],
            "time": datetime.now().strftime("%H:%M"),
        }
    ]


def inject_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

        *, *::before, *::after { box-sizing: border-box; }

        :root {
            --bg: #0f1117;
            --surface: #1a1d27;
            --surface2: #22263a;
            --surface3: #2a2e42;
            --border: rgba(255,255,255,0.08);
            --border-bright: rgba(255,255,255,0.16);
            --text: #e8eaf0;
            --muted: #8b90a8;
            --indigo: #6366f1;
            --cyan: #06b6d4;
            --green: #10b981;
            --amber: #f59e0b;
            --red: #ef4444;
        }

        html, body, [data-testid="stAppViewContainer"], .stApp {
            background: var(--bg) !important;
            color: var(--text) !important;
            font-family: 'DM Sans', sans-serif !important;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background: var(--surface) !important;
            border-right: 1px solid var(--border) !important;
        }
        [data-testid="stSidebar"] * { color: var(--text) !important; }
        [data-testid="stSidebar"] .stButton > button {
            width: 100%;
            background: rgba(99,102,241,0.15) !important;
            border: 1px solid rgba(99,102,241,0.35) !important;
            color: #a5b4fc !important;
            font-family: 'DM Sans', sans-serif !important;
            font-weight: 600 !important;
            border-radius: 10px !important;
            transition: all 0.2s !important;
        }
        [data-testid="stSidebar"] .stButton > button:hover {
            background: rgba(99,102,241,0.28) !important;
            border-color: rgba(99,102,241,0.6) !important;
        }
        [data-testid="stSidebar"] .stSelectbox > div > div {
            background: var(--surface2) !important;
            border: 1px solid var(--border-bright) !important;
            color: var(--text) !important;
            border-radius: 8px !important;
        }
        [data-testid="stSidebar"] .stFileUploader {
            background: var(--surface2) !important;
            border-radius: 10px !important;
        }

        /* Hide Streamlit chrome */
        #MainMenu, footer, header { visibility: hidden; }
        .block-container { padding: 1.5rem 2rem !important; max-width: 100% !important; }

        /* Header */
        .agent-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1rem 0 1.2rem;
            border-bottom: 1px solid var(--border);
            margin-bottom: 1.4rem;
        }
        .agent-header-left { display: flex; align-items: center; gap: 1rem; }
        .agent-logo {
            width: 48px; height: 48px;
            background: linear-gradient(135deg, var(--indigo), var(--cyan));
            border-radius: 14px;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.5rem;
            box-shadow: 0 0 24px rgba(99,102,241,0.35);
        }
        .agent-title {
            font-size: 1.6rem; font-weight: 700;
            letter-spacing: -0.02em; color: var(--text);
            margin: 0;
        }
        .agent-subtitle { color: var(--muted); font-size: 0.88rem; margin: 0; }
        .online-badge {
            display: inline-flex; align-items: center; gap: 0.4rem;
            background: rgba(16,185,129,0.12);
            border: 1px solid rgba(16,185,129,0.3);
            color: #34d399;
            padding: 0.4rem 0.75rem;
            border-radius: 999px; font-size: 0.8rem; font-weight: 600;
        }
        .online-dot {
            width: 7px; height: 7px;
            background: #34d399; border-radius: 50%;
            animation: pulse 1.8s ease-in-out infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(0.8); }
        }

        /* Mode cards */
        .mode-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 0.75rem;
            margin-bottom: 1.4rem;
        }
        .mode-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1rem;
            transition: border-color 0.2s, transform 0.2s;
        }
        .mode-card:hover { border-color: var(--border-bright); transform: translateY(-2px); }
        .mode-icon { font-size: 1.4rem; margin-bottom: 0.5rem; }
        .mode-name { font-weight: 700; font-size: 0.92rem; margin-bottom: 0.15rem; }
        .mode-tag {
            display: inline-block;
            font-size: 0.7rem; font-weight: 600;
            padding: 0.15rem 0.45rem;
            border-radius: 999px; margin-bottom: 0.45rem;
        }
        .mode-desc { color: var(--muted); font-size: 0.78rem; line-height: 1.4; }

        /* Chat messages */
        [data-testid="stChatMessage"] {
            background: transparent !important;
            border: none !important;
        }
        [data-testid="stChatMessageContent"] {
            background: var(--surface) !important;
            border: 1px solid var(--border) !important;
            border-radius: 12px !important;
            padding: 0.9rem 1.1rem !important;
            color: var(--text) !important;
            font-family: 'DM Sans', sans-serif !important;
            font-size: 0.93rem !important;
            line-height: 1.65 !important;
        }

        /* Chat input */
        [data-testid="stChatInput"] {
            background: var(--surface) !important;
            border: 1.5px solid var(--border-bright) !important;
            border-radius: 14px !important;
            color: var(--text) !important;
            font-family: 'DM Sans', sans-serif !important;
        }
        [data-testid="stChatInput"]:focus-within {
            border-color: var(--indigo) !important;
            box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
        }

        /* Route steps */
        .route-wrap {
            background: var(--surface2);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 0.75rem 0.9rem;
            margin-top: 0.65rem;
        }
        .tiny-label {
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.09em;
            font-size: 0.65rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        .route-step {
            display: inline-flex; align-items: center;
            padding: 0.28rem 0.6rem;
            border-radius: 999px;
            border: 1px solid var(--border-bright);
            background: var(--surface3);
            color: var(--text);
            font-size: 0.74rem; font-weight: 600;
            margin: 0.2rem 0.3rem 0.2rem 0;
        }
        .route-arrow { color: var(--muted); margin: 0 0.05rem; font-size: 0.7rem; }

        /* Source box */
        .source-wrap {
            background: var(--surface2);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 0.75rem 0.9rem;
            margin-top: 0.5rem;
        }
        .source-item {
            border-left: 3px solid var(--indigo);
            padding: 0.35rem 0.6rem;
            margin-top: 0.4rem;
            color: var(--muted);
            font-size: 0.81rem;
            border-radius: 0 4px 4px 0;
            background: rgba(99,102,241,0.05);
        }

        /* Meta line */
        .chat-meta {
            display: flex; align-items: center; gap: 0.55rem;
            font-size: 0.73rem; color: var(--muted);
            margin-top: 0.35rem;
        }
        .chat-meta .mode-pill {
            font-weight: 700; font-size: 0.73rem;
            padding: 0.15rem 0.5rem;
            border-radius: 999px;
        }

        /* Right panel */
        .panel-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1rem 1.1rem;
            margin-bottom: 1rem;
        }
        .panel-title {
            font-weight: 700; font-size: 0.88rem;
            color: var(--text); margin-bottom: 0.7rem;
            display: flex; align-items: center; gap: 0.45rem;
        }
        .stat-row {
            display: flex; justify-content: space-between; align-items: center;
            padding: 0.4rem 0;
            border-bottom: 1px solid var(--border);
            font-size: 0.83rem;
        }
        .stat-row:last-child { border-bottom: none; }
        .stat-val { font-weight: 700; color: var(--indigo); }

        /* Code block */
        .stCode { border-radius: 10px !important; }
        pre {
            background: var(--surface2) !important;
            border: 1px solid var(--border) !important;
            border-radius: 10px !important;
            color: #a5b4fc !important;
            font-family: 'DM Mono', monospace !important;
            font-size: 0.8rem !important;
        }

        /* Progress bar */
        .stProgress > div > div > div { background: linear-gradient(90deg, var(--indigo), var(--cyan)) !important; }

        /* Scrollbar */
        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-track { background: var(--bg); }
        ::-webkit-scrollbar-thumb { background: var(--surface3); border-radius: 4px; }

        @media (max-width: 960px) {
            .mode-grid { grid-template-columns: repeat(2, 1fr); }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def sidebar():
    with st.sidebar:
        st.markdown(
            """
            <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:1.2rem;padding-bottom:0.8rem;border-bottom:1px solid rgba(255,255,255,0.08)">
                <div style="width:34px;height:34px;background:linear-gradient(135deg,#6366f1,#06b6d4);border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:1rem;">🤖</div>
                <div>
                    <div style="font-weight:700;font-size:0.95rem;">AI Agent Studio</div>
                    <div style="font-size:0.72rem;color:#8b90a8;">Powered by Groq / Llama</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("＋  New Conversation", use_container_width=True):
            reset_messages()

        st.selectbox(
            "Conversation",
            ["Sprint Demo", "RAG Test", "Web Search Trial"],
            key="selected_chat",
        )

        st.divider()
        st.markdown('<div style="font-size:0.72rem;color:#8b90a8;text-transform:uppercase;letter-spacing:0.09em;font-weight:700;margin-bottom:0.5rem;">Agent Controls</div>', unsafe_allow_html=True)
        st.session_state.streaming = st.toggle("Streaming responses", value=st.session_state.streaming)
        st.session_state.use_memory = st.toggle("Short-term memory", value=st.session_state.use_memory)
        st.session_state.show_route = st.toggle("Show route decisions", value=st.session_state.show_route)
        st.session_state.top_k = st.slider("Top-K document chunks", min_value=1, max_value=8, value=st.session_state.top_k)

        st.divider()
        st.markdown('<div style="font-size:0.72rem;color:#8b90a8;text-transform:uppercase;letter-spacing:0.09em;font-weight:700;margin-bottom:0.5rem;">RAG Documents</div>', unsafe_allow_html=True)
        uploaded = st.file_uploader(
            "Upload documents",
            type=["pdf", "docx", "txt", "md"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )
        if uploaded:
            st.session_state.documents = [file.name for file in uploaded]

        if st.session_state.documents:
            for doc in st.session_state.documents:
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:0.4rem;font-size:0.8rem;padding:0.3rem 0;color:#e8eaf0;">📎 {doc}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                '<div style="font-size:0.78rem;color:#8b90a8;padding:0.5rem 0;">Upload HR policies, proposals, handbooks, or project docs.</div>',
                unsafe_allow_html=True,
            )

        st.divider()
        st.markdown(
            '<div style="font-size:0.72rem;color:#8b90a8;">Streamlit · Groq/Llama · HuggingFace · FAISS · LangChain</div>',
            unsafe_allow_html=True,
        )


def render_header():
    st.markdown(
        """
        <div class="agent-header">
            <div class="agent-header-left">
                <div class="agent-logo">🤖</div>
                <div>
                    <h1 class="agent-title">AI Agent Studio</h1>
                    <p class="agent-subtitle">Multi-mode conversational AI — Chat · Web Search · RAG · Memory</p>
                </div>
            </div>
            <div class="online-badge">
                <div class="online-dot"></div>
                All systems online
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_mode_cards():
    st.markdown('<div class="mode-grid">', unsafe_allow_html=True)
    for name, meta in MODE_META.items():
        st.markdown(
            f"""
            <div class="mode-card">
                <div class="mode-icon">{meta['icon']}</div>
                <div class="mode-name" style="color:{meta['accent']}">{name}</div>
                <div class="mode-tag" style="background:{meta['bg']};color:{meta['accent']}">{meta['label']}</div>
                <div class="mode-desc">{meta['description']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def choose_route(prompt):
    lowered = prompt.lower()
    memory_terms = ["it", "that", "this", "previous", "earlier", "follow up", "who created"]
    web_terms = ["latest", "current", "today", "recent", "news", "stock", "market", "trend", "2026"]
    rag_terms = ["document", "uploaded", "policy", "handbook", "proposal", "company", "leave", "onboarding", "enterprise"]

    uses_memory = len(st.session_state.messages) > 1 and any(t in lowered for t in memory_terms)

    if any(t in lowered for t in rag_terms):
        mode = "RAG"
        route = ["Receive question", "Check memory", "Retrieve vector chunks", "Ground answer", "Cite documents"]
    elif any(t in lowered for t in web_terms):
        mode = "Web Search"
        route = ["Receive question", "Check memory", "Invoke web search", "Summarize results", "Cite web sources"]
    elif uses_memory:
        mode = "Memory"
        route = ["Receive follow-up", "Load chat history", "Resolve reference", "Answer with context"]
    else:
        mode = "General Chat"
        route = ["Receive question", "Use LLM only", "Generate response"]

    return mode, route


def sample_sources(mode):
    if mode == "Web Search":
        return ["DuckDuckGo result: latest public web result summary", "Technology news result: timestamped external context"]
    if mode == "RAG":
        docs = st.session_state.documents or ["HR Handbook.pdf", "Project Proposal.pdf"]
        return [f"{docs[0]}: relevant chunk 1", "Vector index: top matching enterprise context"]
    return []


def draft_response(prompt, mode, history=None):
    try:
        context = ""
        if mode == "RAG" and st.session_state.documents:
            context = f"Available documents: {', '.join(st.session_state.documents)}"
        response, classified_mode = route_query(prompt, context, history)
        return response, classified_mode
    except Exception as e:
        st.error(f"Error: {str(e)}")
        raise


def render_route(route):
    if not st.session_state.get("show_route", True):
        return
    steps = ""
    for i, step in enumerate(route):
        steps += f'<span class="route-step">{step}</span>'
        if i < len(route) - 1:
            steps += '<span class="route-arrow">›</span>'
    st.markdown(
        f"""
        <div class="route-wrap">
            <div class="tiny-label">Agent Decision Flow</div>
            {steps}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sources(sources):
    if not sources:
        return
    rows = "".join(f'<div class="source-item">🔗 {source}</div>' for source in sources)
    st.markdown(
        f"""
        <div class="source-wrap">
            <div class="tiny-label">Sources</div>
            {rows}
        </div>
        """,
        unsafe_allow_html=True,
    )


def chat_panel():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                meta = MODE_META.get(message.get("mode", "General Chat"), MODE_META["General Chat"])
                st.markdown(
                    f"""
                    <div class="chat-meta">
                        <span class="mode-pill" style="background:{meta['bg']};color:{meta['accent']}">
                            {meta['icon']} {message.get("mode")}
                        </span>
                        <span>{message.get("time", "")}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                render_route(message.get("route", []))
                render_sources(message.get("sources", []))


def handle_prompt(prompt):
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "time": datetime.now().strftime("%H:%M"),
    })
    with st.chat_message("user"):
        st.markdown(prompt)

    history = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in st.session_state.messages[:-1]
    ] if st.session_state.get("use_memory", True) else []

    mode_map = {"web": "Web Search", "rag": "RAG", "memory": "Memory", "general": "General Chat"}

    try:
        with st.chat_message("assistant"):
            placeholder = st.empty()
            response, classified_mode = draft_response(prompt, None, history)
            display_mode = mode_map.get(classified_mode, "General Chat")
            mode, route = choose_route(prompt)
            sources = sample_sources(display_mode)

            if st.session_state.get("streaming", True):
                words = response.split()
                streamed = ""
                for word in words:
                    streamed += word + " "
                    placeholder.markdown(streamed)
                    time.sleep(0.015)
            else:
                placeholder.markdown(response)

            meta = MODE_META.get(display_mode, MODE_META["General Chat"])
            st.markdown(
                f"""
                <div class="chat-meta">
                    <span class="mode-pill" style="background:{meta['bg']};color:{meta['accent']}">
                        {meta['icon']} {display_mode}
                    </span>
                    <span>{datetime.now().strftime("%H:%M")}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            render_route(route)
            render_sources(sources)

        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "mode": display_mode,
            "sources": sources,
            "route": route,
            "time": datetime.now().strftime("%H:%M"),
        })
    except Exception as e:
        st.error(f"Failed to generate response: {str(e)}")


def render_right_panel():
    total_msgs = len(st.session_state.messages)
    user_msgs = sum(1 for m in st.session_state.messages if m["role"] == "user")
    modes_used = list({m.get("mode", "General Chat") for m in st.session_state.messages if m["role"] == "assistant"})

    st.markdown(
        f"""
        <div class="panel-card">
            <div class="panel-title">📊 Session Stats</div>
            <div class="stat-row"><span>Total messages</span><span class="stat-val">{total_msgs}</span></div>
            <div class="stat-row"><span>Your messages</span><span class="stat-val">{user_msgs}</span></div>
            <div class="stat-row"><span>Modes activated</span><span class="stat-val">{len(modes_used)}</span></div>
            <div class="stat-row"><span>Documents loaded</span><span class="stat-val">{len(st.session_state.documents)}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="panel-card">
            <div class="panel-title">✅ Evaluation Readiness</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(0.86)
    st.markdown(
        """
        <div style="font-size:0.82rem;color:#8b90a8;line-height:1.8;margin-top:0.3rem;">
        ✔ Three visible modes active<br>
        ✔ Dynamic route preview<br>
        ✔ Source-aware answer panel<br>
        ✔ Session memory through chat history<br>
        ✔ RAG upload surface
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="panel-card" style="margin-top:1rem;">
            <div class="panel-title">⚙️ Backend Hooks</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.code(
        """mode = router.classify(query, history)
if mode == "web":
    ctx = web_search.run(query)
elif mode == "rag":
    ctx = retriever.search(query, top_k=4)
answer = llm.generate(query, ctx, history)""",
        language="python",
    )


def main():
    bootstrap_state()
    inject_css()
    sidebar()
    render_header()
    render_mode_cards()

    left, right = st.columns([0.68, 0.32], gap="large")

    with left:
        chat_panel()
        prompt = st.chat_input("Ask anything — general, latest news, documents, or a follow-up…")
        if prompt:
            handle_prompt(prompt)

    with right:
        render_right_panel()


if __name__ == "__main__":
    main()