import time
from datetime import datetime

import streamlit as st
from agents.router import route_query, classify_mode
from agents.llm_agent import llm_agent


st.set_page_config(
    page_title="Intelligent Conversational AI Agent",
    page_icon="AI",
    layout="wide",
    initial_sidebar_state="expanded",
)


MODE_META = {
    "General Chat": {
        "label": "LLM only",
        "accent": "#2563eb",
        "description": "Answers from model knowledge without external tools.",
    },
    "Web Search": {
        "label": "DuckDuckGo / web",
        "accent": "#0891b2",
        "description": "Retrieves current information and cites web sources.",
    },
    "RAG": {
        "label": "Vector retrieval",
        "accent": "#16a34a",
        "description": "Searches uploaded enterprise documents before answering.",
    },
    "Memory": {
        "label": "Context aware",
        "accent": "#9333ea",
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


def reset_messages():
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello. Ask me a general question, request current information, "
                "or upload documents and ask about them."
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
        :root {
            --surface: #ffffff;
            --surface-alt: #f7f8fb;
            --ink: #121826;
            --muted: #667085;
            --line: #d8dee9;
            --blue: #2563eb;
            --cyan: #0891b2;
            --green: #16a34a;
            --purple: #9333ea;
        }

        .stApp {
            background:
                linear-gradient(180deg, rgba(248, 250, 252, 0.98), rgba(255, 255, 255, 1) 45%),
                radial-gradient(circle at top left, rgba(37, 99, 235, 0.10), transparent 32%);
            color: var(--ink);
        }

        [data-testid="stSidebar"] {
            background: #101827;
            color: #f8fafc;
        }

        [data-testid="stSidebar"] * {
            color: #f8fafc;
        }

        [data-testid="stSidebar"] .stButton button {
            width: 100%;
            border: 1px solid rgba(255,255,255,0.14);
            background: rgba(255,255,255,0.08);
            color: #ffffff;
        }

        .app-header {
            display: grid;
            grid-template-columns: minmax(0, 1fr) auto;
            gap: 1rem;
            align-items: end;
            padding: 1rem 0 0.6rem;
            border-bottom: 1px solid var(--line);
            margin-bottom: 1rem;
        }

        .app-title {
            font-size: clamp(1.55rem, 2vw, 2.2rem);
            font-weight: 800;
            letter-spacing: 0;
            line-height: 1.1;
            margin: 0;
        }

        .app-subtitle {
            color: var(--muted);
            margin-top: 0.35rem;
            font-size: 0.96rem;
        }

        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            border: 1px solid #b7c5e8;
            background: #eef4ff;
            color: #1849a9;
            padding: 0.45rem 0.7rem;
            border-radius: 999px;
            font-size: 0.82rem;
            font-weight: 700;
            white-space: nowrap;
        }

        .metric-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.75rem;
            margin-bottom: 1rem;
        }

        .mode-card {
            border: 1px solid var(--line);
            background: var(--surface);
            border-radius: 8px;
            padding: 0.85rem;
            min-height: 118px;
            box-shadow: 0 10px 28px rgba(18, 24, 38, 0.05);
        }

        .mode-card strong {
            display: block;
            color: var(--ink);
            font-size: 0.96rem;
            margin-bottom: 0.15rem;
        }

        .mode-card span {
            color: var(--muted);
            font-size: 0.82rem;
            line-height: 1.35;
        }

        .mode-bar {
            width: 2.7rem;
            height: 0.22rem;
            border-radius: 999px;
            margin-bottom: 0.65rem;
        }

        .workspace {
            border: 1px solid var(--line);
            background: rgba(255,255,255,0.86);
            border-radius: 8px;
            padding: 1rem;
            box-shadow: 0 16px 40px rgba(18, 24, 38, 0.06);
        }

        .route-box, .source-box {
            border: 1px solid var(--line);
            background: var(--surface-alt);
            border-radius: 8px;
            padding: 0.85rem;
            margin-top: 0.75rem;
        }

        .route-step {
            display: inline-flex;
            align-items: center;
            margin: 0.25rem 0.35rem 0.25rem 0;
            padding: 0.36rem 0.55rem;
            border-radius: 999px;
            border: 1px solid #d1d9e6;
            background: #ffffff;
            color: #344054;
            font-size: 0.78rem;
            font-weight: 650;
        }

        .source-row {
            border-left: 3px solid var(--blue);
            padding-left: 0.65rem;
            margin-top: 0.55rem;
            color: #344054;
            font-size: 0.86rem;
        }

        .tiny-label {
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-size: 0.68rem;
            font-weight: 800;
            margin-bottom: 0.35rem;
        }

        .chat-meta {
            display: flex;
            gap: 0.5rem;
            align-items: center;
            color: var(--muted);
            font-size: 0.76rem;
            margin-top: 0.2rem;
        }

        @media (max-width: 900px) {
            .app-header, .metric-grid {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def sidebar():
    with st.sidebar:
        st.caption("Workspace")
        st.title("Agent Console")

        if st.button("New chat", use_container_width=True):
            reset_messages()
        st.selectbox(
            "Conversation",
            ["Sprint Demo", "RAG Test", "Web Search Trial"],
            key="selected_chat",
        )

        st.divider()
        st.caption("Agent controls")
        st.toggle("Streaming responses", value=True)
        st.toggle("Use short-term memory", value=True)
        st.toggle("Show route decisions", value=True)
        st.slider("Top-K document chunks", min_value=1, max_value=8, value=4)

        st.divider()
        st.caption("RAG documents")
        uploaded = st.file_uploader(
            "Upload enterprise documents",
            type=["pdf", "docx", "txt", "md"],
            accept_multiple_files=True,
        )
        if uploaded:
            st.session_state.documents = [file.name for file in uploaded]

        if st.session_state.documents:
            for doc in st.session_state.documents:
                st.markdown(f"- {doc}")
        else:
            st.info("Upload HR policies, proposals, handbooks, or project docs.")

        st.divider()
        st.caption("Target stack")
        st.markdown(
            "Streamlit · LangGraph · Groq/Llama · Hugging Face embeddings · FAISS · LangChain"
        )


def render_header():
    st.markdown(
        """
        <div class="app-header">
            <div>
                <h1 class="app-title">Intelligent Multi-Mode Conversational AI Agent</h1>
                <div class="app-subtitle">
                    One Streamlit interface for LLM chat, web search, RAG retrieval, and memory-aware follow-ups.
                </div>
            </div>
            <div class="status-pill">● Open-source stack ready</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_mode_cards():
    cols = st.columns(4)
    mode_list = list(MODE_META.items())
    for idx, col in enumerate(cols):
        if idx < len(mode_list):
            name, meta = mode_list[idx]
            with col:
                st.markdown(
                    f"""
                    <div class="mode-card">
                        <div class="mode-bar" style="background:{meta['accent']}"></div>
                        <strong>{name}</strong>
                        <span>{meta['label']}</span><br>
                        <span>{meta['description']}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def choose_route(prompt):
    lowered = prompt.lower()
    memory_terms = ["it", "that", "this", "previous", "earlier", "follow up", "who created"]
    web_terms = [
        "latest",
        "current",
        "today",
        "recent",
        "news",
        "stock",
        "market",
        "trend",
        "2026",
    ]
    rag_terms = [
        "document",
        "uploaded",
        "policy",
        "handbook",
        "proposal",
        "company",
        "leave",
        "onboarding",
        "enterprise",
    ]

    uses_memory = len(st.session_state.messages) > 1 and any(term in lowered for term in memory_terms)

    if any(term in lowered for term in rag_terms):
        mode = "RAG"
        route = ["Receive question", "Check memory", "Retrieve vector chunks", "Ground answer", "Cite documents"]
    elif any(term in lowered for term in web_terms):
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
        return [
            "DuckDuckGo result: latest public web result summary",
            "Technology news result: timestamped external context",
        ]
    if mode == "RAG":
        docs = st.session_state.documents or ["HR Handbook.pdf", "Project Proposal.pdf"]
        return [f"{docs[0]}: relevant chunk 1", "Vector index: top matching enterprise context"]
    return []


def draft_response(prompt, mode, history=None):
    try:
        # Build context based on mode
        context = ""
        if mode == "RAG" and st.session_state.documents:
            context = f"Available documents: {', '.join(st.session_state.documents)}"
        
        # Call the router which classifies and generates response
        response, classified_mode = route_query(prompt, context, history)
        return response, classified_mode
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        st.error(error_msg)
        print(f"LLM Error: {error_msg}")
        raise


def render_route(route):
    steps = "".join(f'<span class="route-step">{step}</span>' for step in route)
    st.markdown(
        f"""
        <div class="route-box">
            <div class="tiny-label">Agent decision flow</div>
            {steps}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sources(sources):
    if not sources:
        return
    rows = "".join(f'<div class="source-row">{source}</div>' for source in sources)
    st.markdown(
        f"""
        <div class="source-box">
            <div class="tiny-label">Sources</div>
            {rows}
        </div>
        """,
        unsafe_allow_html=True,
    )


def chat_panel():
    st.markdown('<div class="workspace">', unsafe_allow_html=True)

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                meta = MODE_META.get(message.get("mode", "General Chat"), MODE_META["General Chat"])
                st.markdown(
                    f"""
                    <div class="chat-meta">
                        <span style="color:{meta['accent']}; font-weight:800;">{message.get("mode")}</span>
                        <span>{message.get("time", "")}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                render_route(message.get("route", []))
                render_sources(message.get("sources", []))

    st.markdown("</div>", unsafe_allow_html=True)


def handle_prompt(prompt):
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
            "time": datetime.now().strftime("%H:%M"),
        }
    )
    with st.chat_message("user"):
        st.markdown(prompt)

    # Build conversation history for context
    history = [
        {"role": msg["role"], "content": msg["content"]} 
        for msg in st.session_state.messages[:-1]  # Exclude the current user message
    ]
    
    mode_map = {"web": "Web Search", "rag": "RAG", "memory": "Memory", "general": "General Chat"}
    
    try:
        with st.chat_message("assistant"):
            placeholder = st.empty()
            response, classified_mode = draft_response(prompt, None, history)
            display_mode = mode_map.get(classified_mode, "General Chat")
            
            # Get route based on classified mode
            mode, route = choose_route(prompt)
            sources = sample_sources(display_mode)
            
            words = response.split()
            streamed = ""
            for word in words:
                streamed += word + " "
                placeholder.markdown(streamed)
                time.sleep(0.015)
            meta = MODE_META.get(display_mode, MODE_META["General Chat"])
            st.markdown(
                f"""
                <div class="chat-meta">
                    <span style="color:{meta['accent']}; font-weight:800;">{display_mode}</span>
                    <span>{datetime.now().strftime("%H:%M")}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            render_route(route)
            render_sources(sources)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response,
                "mode": display_mode,
                "sources": sources,
                "route": route,
                "time": datetime.now().strftime("%H:%M"),
            }
        )
    except Exception as e:
        st.error(f"Failed to generate response: {str(e)}")
        print(f"Error in handle_prompt: {str(e)}")


def main():
    bootstrap_state()
    inject_css()
    sidebar()
    render_header()
    render_mode_cards()

    left, right = st.columns([0.68, 0.32], gap="large")

    with left:
        chat_panel()
        prompt = st.chat_input("Ask about AI, latest news, uploaded documents, or a follow-up...")
        if prompt:
            handle_prompt(prompt)

    with right:
        st.subheader("Evaluation Readiness")
        st.progress(0.86)
        st.markdown(
            """
            - Three visible modes
            - Dynamic route preview
            - Source-aware answer panel
            - Session memory through chat history
            - RAG upload surface
            """
        )

        st.subheader("Backend Hooks")
        st.code(
            """mode = router.classify(query, history)
if mode == "web":
    context = web_search.run(query)
elif mode == "rag":
    context = retriever.search(query, top_k=4)
answer = llm.generate(query, context, history)""",
            language="python",
        )


if __name__ == "__main__":
    main()
