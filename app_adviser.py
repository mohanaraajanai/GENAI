
from __future__ import annotations

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from rag.indexer import FAISSIndexer
from rag.llm import create_llm
from rag.self_rag import RAGServiceError, SelfRAG
from rag.web_search import WebSearchService

load_dotenv(override=True)

# ================================================================
# Paths / configuration
# ================================================================
BASE_DIR = Path(__file__).parent
DOWNLOAD_DIR = BASE_DIR / "downloads"
INDEX_DIR = BASE_DIR / "data" / "faiss_index"
ASSETS_DIR = BASE_DIR / "assets"

DEFAULT_MODEL = os.getenv("AGRI_DEFAULT_MODEL", "gpt-4.1-mini")

MODEL_OPTIONS = [
    "gpt-4.1-mini",
    "gpt-4.1",
    "gpt-5-mini",
    "gpt-5.6-luna",
    "gpt-5.6-terra",
    "gpt-5.6-sol",
]

QUICK_QUESTIONS = [
    "What is PM Kisan Samman Nidhi?",
    "What is Pradhan Mantri Fasal Bima Yojana?",
    "What is Agriculture Infrastructure Fund?",
    "What is Kisan Credit Card and how can I apply?",
    "What benefits are available for organic farming?",
    "What schemes are available for farmers?",
]

st.set_page_config(
    page_title="Agri Farmer Adviser",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ================================================================
# CSS - dashboard closely follows the supplied reference image
# ================================================================
st.markdown(
    """
<style>
:root {
    --green-dark: #075c42;
    --green: #078552;
    --green-light: #e9f8ef;
    --green-pale: #f4fbf7;
    --border: #d9e8df;
    --text: #17382c;
    --muted: #668077;
}

.stApp {
    background:
        radial-gradient(circle at 90% 15%, rgba(215,245,226,.75), transparent 26%),
        linear-gradient(180deg, #f8fbf9 0%, #f0f7f3 100%);
}

.block-container {
    max-width: 1580px;
    padding-top: .35rem !important;
    padding-bottom: 1.2rem !important;
}

/* Keep Streamlit's top bar transparent so the scenic hero remains visible. */
header[data-testid="stHeader"] {
    background: transparent !important;
}
[data-testid="stToolbar"] {
    background: transparent !important;
}

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {
    background:
        linear-gradient(180deg, rgba(2,91,64,.98), rgba(3,68,49,.98));
    border-right: 0;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: .7rem;
}

[data-testid="stSidebar"] * {
    font-family: Arial, sans-serif;
}

.sidebar-logo {
    color: white;
    font-size: 1.05rem;
    font-weight: 800;
    margin: .2rem .15rem .2rem;
}

.sidebar-subtitle {
    color: rgba(255,255,255,.72);
    font-size: .72rem;
    margin: 0 .15rem .9rem;
}

.sidebar-image {
    border-radius: 0 0 12px 12px;
    overflow: hidden;
    margin: 0 -.2rem .8rem;
}

.sidebar-section {
    color: white;
    font-size: .85rem;
    font-weight: 700;
    margin: .75rem .15rem .35rem;
}

[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    min-height: 43px;
    margin: .16rem 0;
    border: 0 !important;
    border-radius: 9px !important;
    background: transparent !important;
    color: white !important;
    text-align: left !important;
    font-weight: 700 !important;
    font-size: .88rem !important;
    box-shadow: none !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,.12) !important;
    color: white !important;
}

/* Sidebar radio navigation */
[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: .2rem;
}

[data-testid="stSidebar"] div[role="radiogroup"] > label {
    background: transparent !important;
    border-radius: 10px !important;
    padding: .48rem .55rem !important;
    color: white !important;
    border: 0 !important;
    min-height: 42px;
}

[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    background: rgba(255,255,255,.10) !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
    background: rgba(31,170,105,.60) !important;
    color: white !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] > label p {
    color: white !important;
    font-weight: 750 !important;
    font-size: .88rem !important;
}

.sidebar-selected {
    background: rgba(31,170,105,.55);
    border-radius: 10px;
    padding: .7rem .8rem;
    color: white;
    font-weight: 800;
    margin: .15rem 0;
}

.sidebar-tagline {
    margin-top: .85rem;
    padding: .9rem .7rem;
    border: 1px solid rgba(255,255,255,.27);
    border-radius: 13px;
    background: rgba(255,255,255,.06);
    color: white;
    text-align: center;
    font-size: .78rem;
    line-height: 1.4;
}

/* ---------- Hero ---------- */
.hero {
    height: 150px;
    border-radius: 0 0 18px 18px;
    overflow: hidden;
    position: relative;
    margin: 0 0 1rem;
    background:
        linear-gradient(90deg, rgba(251,255,252,.98) 0%, rgba(251,255,252,.94) 34%, rgba(251,255,252,.22) 72%, rgba(251,255,252,.05) 100%),
        url("assets/tamilnadu_hero.png") center / cover no-repeat;
    border-bottom: 2px solid #c9e9d6;
}

.hero-content {
    padding: 1.15rem 1.25rem;
    max-width: 750px;
}

.hero-title {
    color: var(--green-dark);
    font-size: 2rem;
    line-height: 1;
    font-weight: 850;
    margin: 0;
}

.hero-subtitle {
    color: #426456;
    font-size: .92rem;
    margin-top: .35rem;
}

.hero-tagline {
    color: var(--green);
    font-weight: 750;
    font-size: .76rem;
    margin-top: .3rem;
}

.hero-pills {
    position: absolute;
    right: 1rem;
    top: 1rem;
    display: flex;
    gap: .45rem;
}

.hero-pill {
    background: rgba(255,255,255,.94);
    border: 1px solid #d6e8df;
    border-radius: 999px;
    padding: .48rem .75rem;
    color: #145c44;
    font-size: .78rem;
    font-weight: 750;
    box-shadow: 0 4px 12px rgba(20,80,55,.07);
}

/* ---------- Main cards ---------- */
.panel {
    background: rgba(255,255,255,.96);
    border: 1px solid var(--border);
    border-radius: 15px;
    box-shadow: 0 5px 20px rgba(30,82,60,.055);
}

.welcome {
    padding: 1rem 1.1rem;
    background: linear-gradient(135deg, #f7fcf9, #eef9f2);
}

.welcome-title {
    color: var(--green-dark);
    font-size: 1.28rem;
    font-weight: 850;
    margin: 0;
}

.welcome-text {
    color: #5d756b;
    font-size: .86rem;
    line-height: 1.45;
    margin-top: .25rem;
}

.hint {
    margin-top: .65rem;
    padding: .52rem .7rem;
    border-radius: 9px;
    background: #e7f8ed;
    border: 1px solid #cce9d8;
    color: #26664e;
    font-size: .77rem;
}

.section-title {
    color: var(--green-dark);
    font-weight: 850;
    font-size: .96rem;
    margin: .8rem 0 .45rem;
}

.quick-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: .45rem;
}

.quick-item {
    border: 1px solid #cfe5d9;
    background: white;
    border-radius: 10px;
    padding: .58rem .65rem;
    color: #25614d;
    font-size: .72rem;
    min-height: 45px;
}

.right-card {
    background: white;
    border: 1px solid var(--border);
    border-radius: 15px;
    padding: .85rem;
    box-shadow: 0 5px 20px rgba(30,82,60,.055);
}

.right-title {
    color: var(--green-dark);
    font-size: 1.05rem;
    font-weight: 850;
    margin-bottom: .55rem;
}

.topic {
    border: 1px solid #dbe9e2;
    border-radius: 12px;
    padding: .68rem .72rem;
    margin-bottom: .48rem;
    background: linear-gradient(90deg, #fff, #f8fcfa);
}

.topic-title {
    color: #17634a;
    font-weight: 800;
    font-size: .78rem;
}

.topic-text {
    color: #6d8279;
    font-size: .68rem;
    margin-top: .16rem;
}

.feature-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: .35rem;
    margin-top: .55rem;
}

.feature {
    text-align: center;
    border: 1px solid #dceae4;
    border-radius: 10px;
    padding: .55rem .25rem;
    color: #17634a;
    font-size: .66rem;
    font-weight: 750;
}

/* ---------- Chat ---------- */
.chat-panel {
    background: white;
    border: 1px solid var(--border);
    border-radius: 15px;
    margin-top: .7rem;
    padding: .75rem;
    min-height: 400px;
}

[data-testid="stChatMessage"] {
    border-radius: 14px;
}

.customer-note {
    text-align: center;
    color: #70837a;
    font-size: .68rem;
    margin-top: .5rem;
}

.source-label {
    color: #146246;
    font-size: .76rem;
    font-weight: 800;
}

.footer {
    text-align: center;
    color: #70847b;
    font-size: .68rem;
    padding: .7rem 0 .15rem;
}

/* ---------- Streamlit controls ---------- */
.stTextInput input {
    border-radius: 10px !important;
    border: 1px solid #cfe2d9 !important;
}

.stButton > button {
    border-radius: 9px !important;
    border: 1px solid #d5e6de !important;
    color: #145c44 !important;
    font-weight: 700 !important;
}

div[data-testid="stFormSubmitButton"] button {
    background: #078552 !important;
    color: white !important;
    border: 0 !important;
}

div[data-testid="stFormSubmitButton"] button:hover {
    background: #066d44 !important;
    color: white !important;
}

[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,.18);
}

@media (max-width: 1000px) {
    .hero-title { font-size: 1.45rem; }
    .hero-pills { display: none; }
    .quick-grid { grid-template-columns: 1fr 1fr; }
}
</style>
""",
    unsafe_allow_html=True,
)

# ================================================================
# Backend helpers
# ================================================================
def index_exists() -> bool:
    return (INDEX_DIR / "index.faiss").exists() and (INDEX_DIR / "index.pkl").exists()


@st.cache_resource(show_spinner=False)
def load_vector_store():
    return FAISSIndexer(DOWNLOAD_DIR, INDEX_DIR).load()


def build_index(chunk_size: int, chunk_overlap: int):
    indexer = FAISSIndexer(DOWNLOAD_DIR, INDEX_DIR)
    result = indexer.build(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    load_vector_store.clear()
    return result


def make_rag(model: str, temperature: float, k: int, web_max_results: int = 5):
    vector_store = load_vector_store()
    llm = create_llm(model, temperature)
    return SelfRAG(
        vector_store,
        llm,
        WebSearchService(max_results=web_max_results),
        k=k,
    )


def init_state(prefix: str):
    key = f"{prefix}_messages"
    if key not in st.session_state:
        st.session_state[key] = []
    return st.session_state[key]


def source_lines_from_state(final_state: dict) -> list[str]:
    lines = []

    for item in final_state.get("sources", []):
        label = item.get("label")
        if label and label not in lines:
            lines.append(label)

    if not lines:
        for doc in final_state.get("documents", []):
            filename = doc.metadata.get("source_file", "unknown.pdf")
            page = doc.metadata.get("page")
            page_text = f" — page {page}" if isinstance(page, int) else ""
            label = f"PDF: {filename}{page_text}"
            if label not in lines:
                lines.append(label)

        for item in final_state.get("web_results", []):
            title = item.get("title", "Web source")
            url = item.get("url", "")
            label = f"WEB: {title}" + (f" — {url}" if url else "")
            if label not in lines:
                lines.append(label)

    return lines


# ================================================================
# Sidebar navigation
# ================================================================
def render_sidebar():
    current = st.session_state.get("customer_section", "home")

    with st.sidebar:
        st.markdown('<div class="sidebar-logo">🌾 Agri Farmer Adviser</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sidebar-subtitle">Better Information • Stronger Farmers</div>',
            unsafe_allow_html=True,
        )

        photo = ASSETS_DIR / "farmer_field.png"
        if photo.exists():
            st.image(str(photo), use_container_width=True)

        st.markdown('<div class="sidebar-section">🌱 Explore</div>', unsafe_allow_html=True)

        options = {
            "home": "⌂  Home",
            "ask": "💬  Ask a Question",
            "conversations": "▣  My Conversations",
            "developer": "</>  Developer Version",
        }

        # A real radio navigation control is used instead of replacing the
        # selected item with non-clickable HTML. This keeps every menu item
        # clickable on every page.
        selected = st.radio(
            "Navigation",
            options=list(options.keys()),
            format_func=lambda x: options[x],
            index=list(options.keys()).index(current),
            label_visibility="collapsed",
            key="sidebar_navigation",
        )

        if selected != current:
            st.session_state["customer_section"] = selected
            st.rerun()

        st.divider()

        st.markdown(
            """
            <div class="sidebar-tagline">
                🌿<br>
                <b>Empowering Farmers</b><br>
                with Reliable Information
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        if st.button(
            "🗑️  Clear My Conversation",
            key="clear_customer",
            use_container_width=True,
        ):
            st.session_state["customer_messages"] = []
            st.rerun()


# ================================================================
# Header
# ================================================================
def render_header():
    st.markdown(
        """
        <div class="hero">
            <div class="hero-content">
                <div class="hero-title">🌾 Agri Farmer Adviser</div>
                <div class="hero-subtitle">Your trusted guide for Government Schemes & Agricultural Support</div>
                <div class="hero-tagline">Better Information &nbsp; | &nbsp; Stronger Farmers &nbsp; | &nbsp; Prosperous Agriculture</div>
            </div>
            <div class="hero-pills">
                <div class="hero-pill">📍 Tamil Nadu ▾</div>
                <div class="hero-pill">👨‍🌾 Farmer ▾</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ================================================================
# Quick questions
# ================================================================
def render_quick_questions():
    st.markdown('<div class="section-title">💬 Try asking these questions</div>', unsafe_allow_html=True)

    cols = st.columns(3)
    for i, question in enumerate(QUICK_QUESTIONS):
        with cols[i % 3]:
            if st.button(question, key=f"quick_question_{i}", use_container_width=True):
                st.session_state["customer_pending_question"] = question
                st.session_state["customer_section"] = "ask"
                st.rerun()


# ================================================================
# Right panel
# ================================================================
def render_right_panel():
    card_image = ASSETS_DIR / "vivasayam_card.png"
    if card_image.exists():
        st.image(str(card_image), use_container_width=True)

    with st.container(border=True):
        st.markdown("### 🌾 Agriculture Topics")

        topics = [
            ("🌱", "Crop Insurance", "Protection against crop loss"),
            ("💰", "Farmer Loans", "Credit and financial support"),
            ("🌿", "Subsidies & Schemes", "Government support programmes"),
            ("🛡️", "Risk Coverage", "Insurance and farmer protection"),
        ]

        for icon, title, description in topics:
            with st.container(border=True):
                st.markdown(f"**{icon} {title}**")
                st.caption(description)

        feature_cols = st.columns(4)
        features = [
            ("🌱", "Crop", "Insurance"),
            ("💰", "Loan", "Support"),
            ("🌿", "Subsidies", "& Schemes"),
            ("🛡️", "Risk", "Coverage"),
        ]

        for col, (icon, line1, line2) in zip(feature_cols, features):
            with col:
                st.markdown(
                    f"<div style='text-align:center;font-size:.78rem;'>"
                    f"<div style='font-size:1.25rem'>{icon}</div>"
                    f"<b>{line1}</b><br>{line2}</div>",
                    unsafe_allow_html=True,
                )


# ================================================================
# Customer chat
# ================================================================
def run_customer_chat():
    messages = init_state("customer")

    for idx, item in enumerate(messages):
        with st.chat_message(item["role"]):
            st.markdown(item["content"])

            if item.get("sources"):
                with st.expander("📚 Sources"):
                    for source in item["sources"]:
                        st.write(source)

            if item["role"] == "assistant":
                st.caption("Was this answer helpful?")
                c1, c2, _ = st.columns([1, 1, 5])
                with c1:
                    st.button("👍 Yes", key=f"customer_yes_{idx}")
                with c2:
                    st.button("👎 No", key=f"customer_no_{idx}")

    with st.form("customer_question_form", clear_on_submit=True):
        c1, c2 = st.columns([6, 1])

        with c1:
            typed_question = st.text_input(
                "Ask your question",
                placeholder="Ask about farmer schemes, crops, insurance, loans, subsidies...",
                label_visibility="collapsed",
            )

        with c2:
            submitted = st.form_submit_button("➤ Send", use_container_width=True)

    pending = st.session_state.pop("customer_pending_question", None)
    prompt = pending or (typed_question.strip() if submitted and typed_question else "")

    if not prompt:
        return

    messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    history = [
        {"role": m["role"], "content": m["content"]}
        for m in messages[:-1]
    ]

    if not index_exists():
        messages.pop()
        st.error(
            "The agriculture knowledge base is not ready yet. "
            "Open Developer Version and build the FAISS index."
        )
        return

    try:
        rag = make_rag(DEFAULT_MODEL, 0.2, 4, 5)
    except Exception as exc:
        messages.pop()
        st.error(f"Unable to load the adviser: {exc}")
        return

    with st.chat_message("assistant"):
        placeholder = st.empty()
        answer_parts = []
        final_state = {}

        status = st.status("🌱 Checking agriculture information…", expanded=False)

        try:
            for event in rag.stream(prompt, history=history):
                if event["type"] == "messages":
                    token, metadata = event["data"]

                    # Customer UI displays ONLY answer-generation tokens.
                    if metadata.get("langgraph_node") != "generate":
                        continue

                    content = getattr(token, "content", "")
                    if content:
                        answer_parts.append(content)
                        placeholder.markdown("".join(answer_parts))

                elif event["type"] == "updates":
                    for _, update in event["data"].items():
                        final_state.update(update)

            answer = final_state.get("answer") or "".join(answer_parts)
            if not answer:
                answer = "I could not produce an answer from the available evidence."

            placeholder.markdown(answer)
            status.update(label="Answer ready", state="complete")

            sources = source_lines_from_state(final_state)

            messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                }
            )

            if sources:
                with st.expander("📚 Sources"):
                    for source in sources:
                        st.write(source)

        except RAGServiceError as exc:
            status.update(label="Request could not be completed", state="error")
            messages.pop()
            st.error(exc.user_message)
        except Exception:
            # Never expose raw backend/provider exceptions to farmers.
            status.update(label="Request could not be completed", state="error")
            messages.pop()
            st.error("The adviser could not complete the request right now. Please try again later.")


# ================================================================
# Home
# ================================================================
def home_page():
    st.markdown(
        """
        <div class="panel welcome">
            <div class="welcome-title">🌿 Welcome to Agri Farmer Adviser</div>
            <div class="welcome-text">
                Ask questions about farmer schemes, crop insurance, loans,
                subsidies and agricultural support. Get simple answers based
                on the available Vikaspedia agriculture information.
            </div>
            <div class="hint">
                💡 Type your question below or choose one of the suggested questions.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_quick_questions()

    st.markdown('<div class="chat-panel">', unsafe_allow_html=True)
    run_customer_chat()
    st.markdown('</div>', unsafe_allow_html=True)


# ================================================================
# Ask page
# ================================================================
def ask_page():
    st.markdown(
        """
        <div class="panel welcome">
            <div class="welcome-title">💬 Ask a Question</div>
            <div class="welcome-text">
                Ask about government schemes, crop insurance, farmer loans,
                subsidies, agriculture infrastructure and other farmer support.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_quick_questions()

    st.markdown('<div class="chat-panel">', unsafe_allow_html=True)
    run_customer_chat()
    st.markdown('</div>', unsafe_allow_html=True)


# ================================================================
# Conversation history
# ================================================================
def conversations_page():
    messages = init_state("customer")

    st.markdown(
        """
        <div class="panel welcome">
            <div class="welcome-title">▣ My Conversations</div>
            <div class="welcome-text">
                Review the questions and answers from this browser session.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not messages:
        st.info("No conversations yet. Ask your first agriculture question.")
        return

    for i, item in enumerate(messages, start=1):
        role = "You" if item["role"] == "user" else "Agri Farmer Adviser"
        st.markdown(f"**{role}**")
        st.write(item["content"])

        if item.get("sources"):
            with st.expander("📚 Sources"):
                for source in item["sources"]:
                    st.write(source)

        if i < len(messages):
            st.divider()


# ================================================================
# Developer page
# ================================================================
def developer_page():
    st.markdown(
        """
        <div class="panel welcome">
            <div class="welcome-title">🛠️ Developer Version</div>
            <div class="welcome-text">
                Technical controls are intentionally separated from the farmer dashboard.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1, 1.5], gap="large")

    with left:
        st.subheader("Runtime configuration")

        model = st.selectbox(
            "LLM model",
            MODEL_OPTIONS,
            index=MODEL_OPTIONS.index(DEFAULT_MODEL)
            if DEFAULT_MODEL in MODEL_OPTIONS
            else 0,
        )

        temperature = st.slider("Temperature", 0.0, 1.5, 0.2, 0.05)
        k = st.slider("Retriever k", 1, 10, 4)
        web_max_results = st.slider("Web search max results", 1, 10, 5)

        show_prompt = st.checkbox("Show adviser prompt", value=False)

        st.info(
            "Low-request Self-RAG: local scope → FAISS retrieval → "
            "answer generation → web fallback when local evidence is unavailable."
        )

        if show_prompt:
            skill_path = BASE_DIR / "prompts" / "agri_farmer_adviser.md"
            if skill_path.exists():
                st.code(skill_path.read_text(encoding="utf-8"), language="markdown")

    with right:
        st.subheader("Knowledge Base")

        c1, c2 = st.columns(2)

        with c1:
            chunk_size = st.number_input(
                "Chunk size",
                min_value=200,
                max_value=5000,
                value=1000,
                step=100,
            )

        with c2:
            chunk_overlap = st.number_input(
                "Chunk overlap",
                min_value=0,
                max_value=1500,
                value=150,
                step=50,
            )

        if chunk_overlap >= chunk_size:
            st.error("Chunk overlap must be smaller than chunk size.")

        if st.button(
            "🔨 Build / Rebuild FAISS index",
            type="primary",
            disabled=chunk_overlap >= chunk_size,
            use_container_width=True,
        ):
            with st.spinner("Extracting PDFs, splitting chunks and building FAISS…"):
                try:
                    result = build_index(int(chunk_size), int(chunk_overlap))
                    st.success("FAISS index built successfully.")
                    st.json(result)
                except Exception as exc:
                    st.error(str(exc))

        st.subheader("Diagnostics")

        pdf_count = (
            len(list(DOWNLOAD_DIR.glob("*.pdf")))
            if DOWNLOAD_DIR.exists()
            else 0
        )

        st.write(f"Downloaded PDFs: **{pdf_count}**")
        st.write(f"FAISS index exists: **{index_exists()}**")
        st.write(f"PDF folder: `{DOWNLOAD_DIR}`")
        st.write(f"FAISS folder: `{INDEX_DIR}`")
        st.write(
            f"Serper web search: **{'Enabled' if os.getenv('SERPER_API_KEY') else 'Not configured'}**"
        )

        if st.button("🧹 Clear developer conversation", use_container_width=True):
            st.session_state["developer_messages"] = []
            st.rerun()

    st.divider()

    if not index_exists():
        st.warning("Build the FAISS index before using Developer Chat.")
        return

    st.subheader("Developer Chat")

    messages = init_state("developer")

    for idx, item in enumerate(messages):
        with st.chat_message(item["role"]):
            st.markdown(item["content"])

    with st.form("developer_question_form", clear_on_submit=True):
        c1, c2 = st.columns([6, 1])

        with c1:
            question = st.text_input(
                "Developer question",
                placeholder="Ask a RAG testing question...",
                label_visibility="collapsed",
            )

        with c2:
            send = st.form_submit_button("➤ Send", use_container_width=True)

    if send and question.strip():
        prompt = question.strip()
        messages.append({"role": "user", "content": prompt})

        history = [
            {"role": m["role"], "content": m["content"]}
            for m in messages[:-1]
        ]

        try:
            rag = make_rag(model, temperature, k, web_max_results)

            with st.chat_message("assistant"):
                placeholder = st.empty()
                answer_parts = []
                final_state = {}

                status = st.status("Running RAG pipeline…", expanded=True)

                for event in rag.stream(prompt, history=history):
                    if event["type"] == "messages":
                        token, metadata = event["data"]

                        if metadata.get("langgraph_node") != "generate":
                            continue

                        content = getattr(token, "content", "")
                        if content:
                            answer_parts.append(content)
                            placeholder.markdown("".join(answer_parts))

                    elif event["type"] == "updates":
                        for node_name, update in event["data"].items():
                            final_state.update(update)

                            if "documents" in update:
                                status.write(
                                    f"{node_name}: {len(update['documents'])} PDF chunks"
                                )

                            if update.get("web_used"):
                                status.write("Web fallback used.")

                answer = final_state.get("answer") or "".join(answer_parts)
                placeholder.markdown(answer)

                status.update(label="Completed", state="complete")

                messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )

        except RAGServiceError as exc:
            messages.pop()
            st.error(exc.user_message)
            with st.expander("Developer error details"):
                st.write(f"Error type: {exc.kind}")
                st.code(exc.technical_message)
        except Exception as exc:
            messages.pop()
            st.error("The adviser could not complete the request right now.")
            with st.expander("Developer error details"):
                st.code(str(exc))


# ================================================================
# Application routing
# ================================================================
if "customer_section" not in st.session_state:
    st.session_state["customer_section"] = "home"

render_sidebar()

section = st.session_state["customer_section"]

if section == "developer":
    developer_page()
else:
    render_header()

    main_col, right_col = st.columns([2.3, 1], gap="large")

    with main_col:
        if section == "ask":
            ask_page()
        elif section == "conversations":
            conversations_page()
        else:
            home_page()

    with right_col:
        render_right_panel()

    st.markdown(
        """
        <div class="footer">
            🌾 Agri Farmer Adviser &nbsp; • &nbsp;
            Supporting Indian Farmers with Reliable Information
            <br>
            <b>Jai Kisan 🇮🇳 | Jai Hind</b>
        </div>
        """,
        unsafe_allow_html=True,
    )
