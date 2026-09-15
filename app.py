import os
import tempfile
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

# Load .env before importing project modules
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

from main import run_pipeline
from core.rag_engine import ask_question


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="InsightMedia",
    page_icon="🎙️",
    layout="wide"
)


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------
# NOTE: This block only changes visual styling (fonts, colors, spacing,
# borders, chat layout). No backend / pipeline / RAG logic is touched.

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

:root {
    --im-bg: #eaf6ff;
    --im-navy: #10233f;
    --im-blue: #1a4c8b;
    --im-blue-light: #2f6fb8;
    --im-border: #10233f;
    --im-card: #ffffff;
    --im-accent: #ffb703;
    --im-text: #1c2b3a;
    --im-muted: #4c5c6c;
    --pixel-font: 'Press Start 2P', monospace;
    --body-font: 'Eras Demi ITC', 'Century Gothic', 'Trebuchet MS', sans-serif;
}

/* -------------------------------------------------- */
/* Base app + typography                              */
/* -------------------------------------------------- */

.stApp {
    background-color: var(--im-bg) !important;
    /* subtle pixel-dot texture, kept light so it never fights the content */
    background-image:
        radial-gradient(rgba(16,35,63,0.055) 1.2px, transparent 1.2px) !important;
    background-size: 24px 24px !important;
    background-attachment: fixed !important;
}

html, body {
    font-family: var(--body-font);
    color: var(--im-text);
}

/* Body font applied ONLY to real text-bearing elements — deliberately
   scoped so it never touches Streamlit's own icon glyphs (those rely on
   ligature text rendered through the Material Symbols font; overriding
   font-family on them is what breaks the sidebar arrow / uploader icon). */
.stMarkdown p, .stMarkdown li, .stMarkdown span, .stMarkdown strong, .stMarkdown em,
.stText, label, .stCaption, div[data-testid="stCaptionContainer"],
.stTextInput input, .stSelectbox div[data-baseweb="select"] *,
.stRadio label p, .stFileUploaderFileName, .stAlert p {
    font-family: var(--body-font) !important;
}

/* Defensive reset: force any Material icon glyph (sidebar collapse arrow,
   uploader icon, expander chevron, etc.) to keep using its icon font,
   regardless of other font-family rules above. */
span[data-testid="stIconMaterial"],
[data-testid="stSidebarCollapseButton"] span,
[data-testid="stSidebarCollapsedControl"] span,
[data-testid="stExpanderToggleIcon"],
[data-testid="stFileUploaderDropzone"] span[data-testid="stIconMaterial"] {
    font-family: "Material Symbols Rounded", "Material Icons", sans-serif !important;
    font-weight: normal !important;
    font-size: inherit !important;
}

/* Keep Streamlit's own top header + sidebar collapse arrow untouched/visible */
header[data-testid="stHeader"] {
    background-color: transparent;
}

/* -------------------------------------------------- */
/* Block container spacing                            */
/* -------------------------------------------------- */

.block-container {
    padding-top: 1.5rem;
    padding-left: 2.5rem;
    padding-right: 2.5rem;
    padding-bottom: 3rem;
    max-width: 1150px;
}

/* -------------------------------------------------- */
/* App header banner                                  */
/* -------------------------------------------------- */

.im-header {
    padding: 26px 30px;
    border-radius: 10px;
    background: var(--im-navy);
    border: 3px solid var(--im-border);
    box-shadow: 6px 6px 0 rgba(16,35,63,0.18);
    color: #ffffff;
    margin-bottom: 32px;
}

.im-header-title {
    font-family: var(--pixel-font);
    font-size: 22px;
    line-height: 1.6;
    letter-spacing: 1px;
    color: #ffffff;
}

.im-header-subtitle {
    font-family: var(--body-font);
    font-size: 15px;
    margin-top: 14px;
    opacity: 0.9;
}

/* -------------------------------------------------- */
/* Sidebar                                            */
/* -------------------------------------------------- */

section[data-testid="stSidebar"] {
    background-color: #dcefff;
    border-right: 3px solid var(--im-border);
}

.im-brand {
    font-family: var(--pixel-font);
    font-size: 13px;
    line-height: 1.8;
    color: var(--im-navy);
    margin-bottom: 4px;
    padding-top: 6px;
}

.im-brand-sub {
    font-family: var(--body-font);
    font-size: 12.5px;
    color: var(--im-muted);
    margin-bottom: 18px;
}

.im-nav-label {
    font-family: var(--pixel-font);
    font-size: 10px;
    color: var(--im-navy);
    margin: 18px 0 10px 0;
}

/* Sidebar navigation buttons -> Press Start 2P, clear active state */
section[data-testid="stSidebar"] .stButton > button {
    font-family: var(--pixel-font) !important;
    font-size: 10px !important;
    text-align: left;
    justify-content: flex-start;
    padding: 12px 14px;
    border-radius: 6px;
    border: 2px solid var(--im-border);
    margin-bottom: 8px;
    width: 100%;
}

section[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
    background-color: #ffffff;
    color: var(--im-navy);
    box-shadow: 3px 3px 0 rgba(16,35,63,0.15);
}

section[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
    background-color: #f2f9ff;
    border-color: var(--im-blue);
}

section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background-color: var(--im-navy) !important;
    color: #ffffff !important;
    box-shadow: 3px 3px 0 var(--im-accent);
    border-color: var(--im-navy) !important;
}

.im-feature-list {
    list-style: none;
    padding-left: 0;
    margin: 0;
}

.im-feature-list li {
    font-family: var(--body-font);
    font-size: 13.5px;
    color: var(--im-text);
    background: #ffffff;
    border: 1.5px solid var(--im-border);
    border-radius: 6px;
    padding: 8px 10px;
    margin-bottom: 8px;
}

.im-sidebar-footer {
    font-family: var(--body-font);
    font-size: 11.5px;
    color: var(--im-muted);
    margin-top: 20px;
}

/* -------------------------------------------------- */
/* Section headings                                   */
/* -------------------------------------------------- */

.im-section-title {
    font-family: var(--body-font);
    font-weight: 700;
    font-size: 26px;
    color: var(--im-navy);
    margin-top: 6px;
    margin-bottom: 4px;
}

.im-section-subtitle {
    font-family: var(--body-font);
    font-size: 14.5px;
    color: var(--im-muted);
    margin-bottom: 22px;
}

.im-card-title {
    font-family: var(--body-font);
    font-weight: 700;
    font-size: 17px;
    color: var(--im-navy);
    margin-bottom: 10px;
    padding-bottom: 8px;
    border-bottom: 2px solid #dbe9f6;
}

/* -------------------------------------------------- */
/* Cards / containers                                 */
/* -------------------------------------------------- */

div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 10px !important;
}

div[data-testid="stVerticalBlockBorderWrapper"]:has(div.im-card-marker) {
    background: var(--im-card);
    border: 2px solid var(--im-border) !important;
    box-shadow: 4px 4px 0 rgba(16,35,63,0.10);
    padding: 4px 4px;
}

/* Home feature tiles */
.im-tile {
    background: #ffffff;
    border: 2px solid var(--im-border);
    border-radius: 10px;
    box-shadow: 4px 4px 0 rgba(16,35,63,0.10);
    padding: 20px;
    height: 100%;
}

.im-tile-icon {
    font-size: 26px;
    margin-bottom: 8px;
}

.im-tile-title {
    font-family: var(--body-font);
    font-weight: 700;
    font-size: 16px;
    color: var(--im-navy);
    margin-bottom: 6px;
}

.im-tile-text {
    font-family: var(--body-font);
    font-size: 13.5px;
    color: var(--im-muted);
}

.im-flow-card {
    background: #ffffff;
    border: 2px dashed var(--im-blue);
    border-radius: 10px;
    padding: 18px 20px;
    font-family: var(--body-font);
    font-size: 14.5px;
    color: var(--im-navy);
    text-align: center;
    margin-top: 8px;
}

/* -------------------------------------------------- */
/* Processing / status block (no chevrons, no arrows) */
/* -------------------------------------------------- */

.im-processing {
    background: #ffffff;
    border: 2px solid var(--im-border);
    border-radius: 10px;
    box-shadow: 4px 4px 0 rgba(16,35,63,0.10);
    padding: 20px 22px;
    margin-top: 10px;
    margin-bottom: 24px;
}

.im-processing-title {
    font-family: var(--body-font);
    font-weight: 700;
    font-size: 15.5px;
    color: var(--im-navy);
    margin-bottom: 12px;
}

.im-step {
    font-family: var(--body-font);
    font-size: 13.5px;
    color: var(--im-text);
    padding: 6px 0;
    border-bottom: 1px solid #eef4fa;
}

.im-step:last-child {
    border-bottom: none;
}

.im-step-done {
    color: var(--im-blue);
}

/* -------------------------------------------------- */
/* Streamlit native widgets restyled to match theme   */
/* -------------------------------------------------- */

.stButton > button, .stDownloadButton > button {
    font-family: var(--body-font);
    border-radius: 6px;
    border: 2px solid var(--im-border);
}

.stTextInput input, .stSelectbox div[data-baseweb="select"], .stFileUploader {
    border-radius: 6px !important;
}

/* Expander (used only for the Transcript viewer, not processing states) */
.streamlit-expanderHeader, div[data-testid="stExpander"] summary {
    font-family: var(--body-font) !important;
    font-weight: 700;
    color: var(--im-navy);
}

div[data-testid="stExpander"] {
    border: 2px solid var(--im-border) !important;
    border-radius: 10px !important;
    background: #ffffff;
}

/* Chat */

div[data-testid="stChatMessage"] {
    background: #ffffff;
    border: 2px solid var(--im-border);
    border-radius: 10px;
    box-shadow: 3px 3px 0 rgba(16,35,63,0.08);
    margin-bottom: 10px;
    font-family: var(--body-font);
}

div[data-testid="stChatInput"] {
    border: 2px solid var(--im-border);
    border-radius: 10px;
    background: #ffffff;
}

.im-chat-caption {
    font-family: var(--body-font);
    font-size: 13.5px;
    color: var(--im-muted);
    margin-bottom: 18px;
}

/* -------------------------------------------------- */
/* Footer                                             */
/* -------------------------------------------------- */

.im-footer {
    text-align: center;
    font-family: var(--body-font);
    font-size: 12px;
    color: #9fb3c4;
    margin-top: 50px;
    padding-top: 16px;
    border-top: 1px solid #d7e8f5;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "result" not in st.session_state:
    st.session_state.result = None

if "source_name" not in st.session_state:
    st.session_state.source_name = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

if "page" not in st.session_state:
    st.session_state.page = "HOME"


# --------------------------------------------------
# SIDEBAR (navigation + features)
# --------------------------------------------------

NAV_ITEMS = [
    ("HOME", "🏠"),
    ("NEW ANALYSIS", "🆕"),
    ("RAG CHAT", "💬"),
]

with st.sidebar:

    st.markdown('<div class="im-brand">INSIGHTMEDIA</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="im-brand-sub">AI Video &amp; Meeting Intelligence</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="im-nav-label">NAVIGATION</div>', unsafe_allow_html=True)

    for label, icon in NAV_ITEMS:
        is_active = st.session_state.page == label
        clicked = st.button(
            f"{icon}  {label}",
            key=f"nav_{label}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        )
        if clicked and not is_active:
            st.session_state.page = label
            st.rerun()

    st.markdown('<div class="im-nav-label">FEATURES</div>', unsafe_allow_html=True)

    st.markdown("""
    <ul class="im-feature-list">
        <li>🎬 YouTube / Video Input</li>
        <li>🎙️ Whisper Transcription</li>
        <li>🤖 AI Summary</li>
        <li>✅ Action Items</li>
        <li>🔑 Key Decisions</li>
        <li>❓ Open Questions</li>
        <li>🧠 RAG Q&amp;A</li>
    </ul>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="im-sidebar-footer">InsightMedia • AI Video Assistant</div>',
        unsafe_allow_html=True
    )

page = st.session_state.page


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown("""
<div class="im-header">
    <div class="im-header-title">INSIGHTMEDIA</div>
    <div class="im-header-subtitle">
        Get smart insights from YouTube videos or your local files
    </div>
</div>
""", unsafe_allow_html=True)


# ==================================================
# HOME
# ==================================================

if page == "HOME":

    st.markdown('<div class="im-section-title">Welcome to InsightMedia</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="im-section-subtitle">Convert videos and meetings into transcripts, '
        'summaries, action items, decisions and searchable AI insights.</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="im-tile">
            <div class="im-tile-icon">🎬</div>
            <div class="im-tile-title">Video Processing</div>
            <div class="im-tile-text">YouTube URL or local video/audio file</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="im-tile">
            <div class="im-tile-icon">🤖</div>
            <div class="im-tile-title">AI Insights</div>
            <div class="im-tile-text">Summary and structured information</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="im-tile">
            <div class="im-tile-icon">💬</div>
            <div class="im-tile-title">RAG Chat</div>
            <div class="im-tile-text">Ask questions about your video</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="im-card-title" style="margin-top:32px;">How it works</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="im-flow-card">
        Video → Audio → Whisper → Transcript → Groq AI → ChromaDB → RAG → Insights
    </div>
    """, unsafe_allow_html=True)


# ==================================================
# NEW ANALYSIS
# ==================================================

elif page == "NEW ANALYSIS":

    st.markdown('<div class="im-section-title">New Analysis</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="im-section-subtitle">Upload a video/audio file or provide a YouTube URL.</div>',
        unsafe_allow_html=True
    )

    input_type = st.radio(
        "Choose input type",
        ["YouTube URL", "Local File"],
        horizontal=True
    )

    source = None

    if input_type == "YouTube URL":

        source = st.text_input(
            "YouTube URL",
            placeholder="https://www.youtube.com/watch?v=..."
        )

    else:

        uploaded_file = st.file_uploader(
            "Upload video/audio",
            type=[
                "mp4",
                "mkv",
                "mov",
                "avi",
                "mp3",
                "wav",
                "m4a"
            ]
        )

        if uploaded_file:

            temp_dir = tempfile.gettempdir()

            file_path = os.path.join(
                temp_dir,
                uploaded_file.name
            )

            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            source = file_path

    language = st.selectbox(
        "Language",
        ["english", "hinglish"]
    )

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    analyze = st.button(
        "🚀 Analyze Video",
        type="primary",
        use_container_width=True
    )

    if analyze:

        if not source:

            st.warning(
                "Please provide a YouTube URL or upload a file."
            )

        else:

            st.session_state.result = None
            st.session_state.messages = []

            # Clean, consistent processing card (no expander arrow / chevrons)
            status_box = st.empty()

            def render_processing(current_index):
                steps = [
                    "🎬  Processing video / audio...",
                    "🎙️  Transcribing with Whisper...",
                    "🤖  Generating AI insights...",
                    "🧠  Building RAG vector store...",
                ]
                rows = ""
                for i, step in enumerate(steps):
                    css_class = "im-step im-step-done" if i <= current_index else "im-step"
                    rows += f'<div class="{css_class}">{step}</div>'

                status_box.markdown(f"""
                <div class="im-processing">
                    <div class="im-processing-title">Processing your video...</div>
                    {rows}
                </div>
                """, unsafe_allow_html=True)

            try:
                render_processing(-1)

                with st.spinner(" "):
                    render_processing(3)
                    result = run_pipeline(
                        source,
                        language
                    )

                status_box.empty()

                st.session_state.result = result

                if input_type == "YouTube URL":
                    st.session_state.source_name = source
                else:
                    st.session_state.source_name = uploaded_file.name

                st.success(
                    "Analysis completed successfully!"
                )

            except Exception as e:

                status_box.empty()

                st.error(
                    "Something went wrong while processing the video."
                )

                st.caption(
                    f"Error details: {e}"
                )


# ==================================================
# DISPLAY RESULTS
# ==================================================

if page == "NEW ANALYSIS" and st.session_state.result is not None:

    result = st.session_state.result

    st.markdown('<div class="im-section-title" style="margin-top:36px;">Analysis Results</div>', unsafe_allow_html=True)
    st.markdown('<div class="im-section-subtitle">Everything InsightMedia pulled out of your video.</div>', unsafe_allow_html=True)

    # ----------------------------------------------
    # Title
    # ----------------------------------------------

    with st.container(border=True):
        st.markdown('<div class="im-card-marker"></div>', unsafe_allow_html=True)
        st.markdown('<div class="im-card-title">📌 Title</div>', unsafe_allow_html=True)
        st.markdown(f"#### {result['title']}")

    # ----------------------------------------------
    # Summary
    # ----------------------------------------------

    with st.container(border=True):
        st.markdown('<div class="im-card-marker"></div>', unsafe_allow_html=True)
        st.markdown('<div class="im-card-title">📋 Summary</div>', unsafe_allow_html=True)
        st.markdown(result["summary"])

    # ----------------------------------------------
    # Action Items + Key Decisions
    # ----------------------------------------------

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown('<div class="im-card-marker"></div>', unsafe_allow_html=True)
            st.markdown('<div class="im-card-title">✅ Action Items</div>', unsafe_allow_html=True)
            st.markdown(result["action_items"])

    with col2:
        with st.container(border=True):
            st.markdown('<div class="im-card-marker"></div>', unsafe_allow_html=True)
            st.markdown('<div class="im-card-title">🔑 Key Decisions</div>', unsafe_allow_html=True)
            st.markdown(result["key_decisions"])

    # ----------------------------------------------
    # Open Questions
    # ----------------------------------------------

    with st.container(border=True):
        st.markdown('<div class="im-card-marker"></div>', unsafe_allow_html=True)
        st.markdown('<div class="im-card-title">❓ Open Questions</div>', unsafe_allow_html=True)
        st.markdown(result["open_questions"])

    # ----------------------------------------------
    # Transcript
    # ----------------------------------------------

    with st.expander("📄 View Full Transcript"):
        st.write(result["transcript"])


# ==================================================
# CHAT (RAG)
# ==================================================

if page == "RAG CHAT" and st.session_state.result is not None:

    st.markdown('<div class="im-section-title">Chat with your video</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="im-chat-caption">Ask questions based only on the processed video transcript.</div>',
        unsafe_allow_html=True
    )

    rag_chain = st.session_state.result["rag_chain"]

    # Render full chat history every run, so the conversation reads
    # Question -> Answer -> Question -> Answer, top to bottom.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input is rendered unconditionally on every run (not nested
    # inside the "if question" block), so it is always available again
    # immediately after an answer — no refresh or manual action needed.
    question = st.chat_input("Ask something about your video...")

    if question:

        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = ask_question(rag_chain, question)
            st.markdown(answer)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

        # Rerun so the widget tree resets cleanly and the chat input
        # reappears immediately, ready for the next question.
        st.rerun()

elif page == "RAG CHAT":

    st.info("Please analyze a video first, then you can chat with it.")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown('<div class="im-footer">Made by Shabana</div>', unsafe_allow_html=True)