import streamlit as st
import os
import json
import asyncio
import threading
from pypdf import PdfReader
from dotenv import load_dotenv

# Load environment variables (such as GEMINI_API_KEY)
load_dotenv()

# Set up Streamlit Page Configuration with rich, premium aesthetics
st.set_page_config(
    page_title="EduAssist AI - Multi-Agent Study Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)
if "quiz" not in st.session_state:
    st.session_state.quiz = None

# Custom Premium CSS Injection for sleek theme, glassmorphism card styling, and dynamic hover buttons
st.markdown("""
<style>
    /* Import Font */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

    :root {
        --primary: #2563eb;
        --primary-dark: #1d4ed8;
        --primary-light: #60a5fa;
        --text-main: #1e293b;
        --text-soft: #475569;
        --surface: #ffffff;
        --bg: #f1f5f9;
        --border: #cbd5e1;
        --sidebar-bg-top: #0f172a;
        --sidebar-bg-bottom: #1e293b;
        --sidebar-text: #e2e8f0;
        --sidebar-text-muted: #94a3b8;
        --sidebar-active-bg: rgba(59, 130, 246, 0.18);
    }

    /* ===================== GLOBAL / MAIN AREA ===================== */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Outfit', sans-serif;
    }

    [data-testid="stMain"], .main {
        background: var(--bg);
        color: var(--text-main);
    }

    [data-testid="stMain"] p,
    [data-testid="stMain"] li,
    [data-testid="stMain"] label,
    .main p, .main li, .main label {
        color: var(--text-main);
    }

    [data-testid="stMain"] h1, [data-testid="stMain"] h2,
    [data-testid="stMain"] h3, [data-testid="stMain"] h4 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        color: var(--text-main);
    }

    [data-testid="stMain"] .block-container {
        padding-top: 2.2rem;
        max-width: 1200px;
    }

    /* Only recolor the header to blend with the page — no visibility/display
       rules here. The sidebar collapse/expand toggle lives somewhere inside
       this header, and its internal data-testid has changed between
       Streamlit versions, so hiding any part of the header risks hiding
       that control too. Background-color alone never hides anything. */
    [data-testid="stHeader"] {
        background: var(--bg);
    }

    /* ===================== HEADINGS / CARDS ===================== */
    .agent-header {
        font-size: 2.1rem;
        font-weight: 800;
        color: var(--text-main);
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .agent-subtitle {
        color: var(--text-soft);
        font-size: 1rem;
        margin-bottom: 22px;
        padding-bottom: 18px;
        border-bottom: 1px solid var(--border);
    }

    .premium-card {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border: 1px solid #334155;
        border-left: 5px solid var(--primary);
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 18px;
        box-shadow: 0 10px 28px rgba(15, 23, 42, 0.18);
    }

    .premium-card h4 {
        color: #f8fafc !important;
        margin: 0;
        font-weight: 700;
        font-size: 1.15rem;
        letter-spacing: 0.2px;
    }

    /* Result text rendered via st.markdown right after a premium-card */
    [data-testid="stMain"] .stMarkdown {
        line-height: 1.65;
    }

    /* ===================== BUTTONS ===================== */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, var(--primary), var(--primary-dark));
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 28px;
        font-size: 0.98rem;
        font-weight: 600;
        letter-spacing: 0.2px;
        transition: all 0.2s ease;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3);
    }

    div.stButton > button:first-child:hover {
        background: linear-gradient(135deg, var(--primary-dark), #1e40af);
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.4);
    }

    div.stButton > button:first-child:active {
        transform: translateY(0px);
    }

    div.stDownloadButton > button:first-child {
        background: var(--surface);
        color: var(--primary);
        border: 1.5px solid var(--primary);
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    div.stDownloadButton > button:first-child:hover {
        background: var(--primary);
        color: white;
    }

    /* ===================== INPUTS ===================== */
    .stTextInput input,
    .stTextArea textarea {
        background-color: var(--surface) !important;
        color: var(--text-main) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: 10px;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }

    .stTextInput input:focus,
    .stTextArea textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
    }

    .stSelectbox div[data-baseweb="select"] {
        background-color: var(--surface) !important;
        color: var(--text-main) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: 10px;
    }

    .stFileUploader {
        background: var(--surface);
        border: 1.5px dashed var(--primary);
        border-radius: 12px;
        padding: 14px;
    }

    /* Radio rendered inside the main area (Quiz Agent) */
    [data-testid="stMain"] div[role="radiogroup"] label {
        background: var(--surface);
        border: 1.5px solid var(--border);
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 6px;
        transition: border-color 0.15s ease, background 0.15s ease;
    }
    [data-testid="stMain"] div[role="radiogroup"] label:hover {
        border-color: var(--primary-light);
        background: #eff6ff;
    }

    /* ===================== ALERTS (main area) ===================== */
    [data-testid="stMain"] .stAlert {
        border-radius: 10px;
        border: 1px solid var(--border);
    }

    /* ===================== SIDEBAR ===================== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--sidebar-bg-top), var(--sidebar-bg-bottom));
        border-right: 1px solid #1e293b;
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
        padding-top: 1.2rem;
    }

    /* Force readable, light text on every text element inside the dark sidebar */
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] li,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div {
        color: var(--sidebar-text) !important;
    }

    .sidebar-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #f8fafc !important;
        text-align: center;
        margin-bottom: 4px;
        letter-spacing: 0.3px;
    }

    .sidebar-tagline {
        text-align: center;
        font-size: 0.78rem;
        color: var(--sidebar-text-muted) !important;
        margin-bottom: 18px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .sidebar-section-label {
        font-size: 0.72rem;
        font-weight: 700;
        color: var(--sidebar-text-muted) !important;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin: 18px 0 8px 4px;
    }

    section[data-testid="stSidebar"] hr {
        border-color: #334155;
        margin: 14px 0;
    }

    /* Sidebar navigation radio styled as nav items */
    section[data-testid="stSidebar"] div[role="radiogroup"] {
        gap: 2px;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        border-radius: 8px;
        padding: 9px 10px;
        margin-bottom: 2px;
        width: 100%;
        transition: background 0.15s ease;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background: rgba(148, 163, 184, 0.12);
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] {
        background: var(--sidebar-active-bg);
        border-left: 3px solid var(--primary-light);
    }

    /* Sidebar alert boxes (success / warning / info) — readable on dark bg */
    section[data-testid="stSidebar"] .stAlert {
        border-radius: 10px;
        background: rgba(148, 163, 184, 0.10) !important;
        border: 1px solid rgba(148, 163, 184, 0.25);
    }
    section[data-testid="stSidebar"] .stAlert p {
        color: var(--sidebar-text) !important;
        font-size: 0.86rem;
    }
    section[data-testid="stSidebar"] [data-testid="stAlertContentSuccess"] {
        border-left: 3px solid #22c55e;
    }
    section[data-testid="stSidebar"] [data-testid="stAlertContentInfo"] {
        border-left: 3px solid var(--primary-light);
    }
    section[data-testid="stSidebar"] [data-testid="stAlertContentWarning"] {
        border-left: 3px solid #f59e0b;
    }

    /* Scrollbar polish */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-thumb { background: #94a3b8; border-radius: 8px; }
    ::-webkit-scrollbar-track { background: transparent; }
</style>
""", unsafe_allow_html=True)

# Helper function to run Google ADK Agents synchronously inside Streamlit
def run_agent_sync(agent, prompt: str) -> str:
    async def _async_run():
        from google.adk.runners import InMemoryRunner
        from google.genai import types
        
        # Initialize Runner
        runner = InMemoryRunner(agent=agent, app_name="eduassist")
        # Create session
        session = await runner.session_service.create_session(app_name="eduassist", user_id="user_default")
        
        user_message = types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)]
        )
        
        final_text = ""
        # Process and collect output from the event stream
        async for event in runner.run_async(
            user_id="user_default",
            session_id=session.id,
            new_message=user_message
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    text_parts = [part.text for part in event.content.parts if part.text]
                    if text_parts:
                        final_text = "".join(text_parts)
                break
        return final_text

    # Thread-safe execution bridge to run async ADK in a separate thread
    result = [None]
    exception = [None]

    def thread_func():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result[0] = loop.run_until_complete(_async_run())
            loop.close()
        except Exception as e:
            exception[0] = e

    t = threading.Thread(target=thread_func)
    t.start()
    t.join()

    if exception[0] is not None:
        raise exception[0]
    return result[0]

# PDF text extractor
def extract_text_from_pdf(uploaded_file) -> str:
    try:
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

# Verify API key configuration
api_key_configured = "GEMINI_API_KEY" in os.environ or "GOOGLE_API_KEY" in os.environ

# Sidebar Navigation Layout
st.sidebar.markdown(
    "<div class='sidebar-title'>🎓 EduAssist AI</div>"
    "<div class='sidebar-tagline'>Multi-Agent Study Assistant</div>",
    unsafe_allow_html=True
)

if not api_key_configured:
    st.sidebar.warning("⚠️ Gemini API Key not found. Please create a `.env` file in the project folder and add your key.")
else:
    st.sidebar.success("✅ API Authentication Active")

st.sidebar.markdown("<div class='sidebar-section-label'>Navigation</div>", unsafe_allow_html=True)

if "module" not in st.session_state:
    st.session_state.module = "Dashboard"

# Apply any pending navigation request (set by the Dashboard quick-access
# buttons) before the radio widget below is instantiated. Streamlit forbids
# writing to a widget-bound session_state key *after* that widget has been
# created in the same run, so this swap must happen here, first.
if "pending_module" in st.session_state:
    st.session_state.module = st.session_state.pop("pending_module")

module = st.sidebar.radio(
    "Select Agent Module",
    [
        "Dashboard",
        "Planner Agent",
        "Research Agent",
        "Summary Agent",
        "Quiz Agent",
        "Resource Agent"
    ],
    key="module",
    label_visibility="collapsed"
)

st.sidebar.markdown("<hr/>", unsafe_allow_html=True)

st.sidebar.info(
    "**EduAssist AI** is a multi-agent application powered by Google ADK. Each tool represents a specialized LLM agent designed for particular study tasks."
)

# Import Agents safely
if api_key_configured:
    try:
        from agents import (
            planner_agent,
            researcher_agent,
            summarizer_agent,
            quizzer_agent,
            resourcer_agent
        )
    except Exception as e:
        st.error(f"Failed to load agents: {e}")

# ==================== MODULE 1: DASHBOARD ====================
if module == "Dashboard":
    st.markdown("<div class='agent-header'>🎓 EduAssist AI</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='agent-subtitle'>Welcome to <b>EduAssist AI</b>! This application demonstrates a multi-agent "
        "architecture built using Google's <b>Agent Development Kit (ADK)</b> and the Gemini model framework. "
        "Select an agent module from the sidebar to start experimenting.</div>",
        unsafe_allow_html=True
    )

    st.markdown("<div class='sidebar-section-label'>Quick Access</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📅 Planner Agent", use_container_width=True):
            st.session_state.pending_module = "Planner Agent"
            st.rerun()

        if st.button("📚 Research Agent", use_container_width=True):
            st.session_state.pending_module = "Research Agent"
            st.rerun()

        if st.button("📝 Summary Agent", use_container_width=True):
            st.session_state.pending_module = "Summary Agent"
            st.rerun()

    with col2:
        if st.button("❓ Quiz Agent", use_container_width=True):
            st.session_state.pending_module = "Quiz Agent"
            st.rerun()

        if st.button("🔗 Resource Agent", use_container_width=True):
            st.session_state.pending_module = "Resource Agent"
            st.rerun()

# ==================== MODULE 2: PLANNER AGENT ====================
elif module == "Planner Agent":
    st.markdown("<div class='agent-header'>Planner Agent 📅</div>", unsafe_allow_html=True)
    st.markdown("<div class='agent-subtitle'>Construct a customized, realistic study plan complete with daily/weekly tasks and checkpoints.</div>", unsafe_allow_html=True)
    
    if not api_key_configured:
        st.error("Please configure your API key to run this agent.")
    else:
        # User input fields
        col1, col2 = st.columns(2)
        with col1:
            subject = st.text_input("What subject or topic do you want to learn?", placeholder="e.g., Data Structures & Algorithms, Spanish grammar")
            duration = st.text_input("Target Duration / Timeframe", placeholder="e.g., 2 weeks, 1 month, 20 hours total")
        with col2:
            skill_level = st.selectbox("Current Knowledge Level", ["Beginner", "Intermediate", "Advanced"])
        
        if st.button("Generate Study Plan"):
            if not subject or not duration:
                st.warning("Please fill in both the Subject and Duration fields.")
            else:
                with st.spinner("Our Study Planner Agent is designing your curriculum..."):
                    try:
                        prompt = f"Subject: {subject}\nSkill Level: {skill_level}\nTarget Duration: {duration}"
                        result = run_agent_sync(planner_agent, prompt)
                        
                        st.markdown("<div class='premium-card'><h4>Personalized Curriculum</h4></div>", unsafe_allow_html=True)
                        st.markdown(result)
                        
                        # Add download button for study plan
                        st.download_button(
                            label="📥 Download Study Plan",
                            data=result,
                            file_name=f"Study_Plan_{subject.replace(' ', '_')}.md",
                            mime="text/markdown"
                        )
                    except Exception as e:
                        st.error(f"Execution Error: {e}")

# ==================== MODULE 3: RESEARCH AGENT ====================
elif module == "Research Agent":
    st.markdown("<div class='agent-header'>Research Agent 📚</div>", unsafe_allow_html=True)
    st.markdown("<div class='agent-subtitle'>Upload a PDF study document and ask the agent questions about it. The agent will fetch context from the PDF using tools.</div>", unsafe_allow_html=True)

    if not api_key_configured:
        st.error("Please configure your API key to run this agent.")
    else:
        uploaded_file = st.file_uploader("Upload your study PDF", type=["pdf"])
        
        if uploaded_file is not None:
            # Extract PDF content once and save to global variable in researcher
            with st.spinner("Extracting text from PDF document..."):
                pdf_text = extract_text_from_pdf(uploaded_file)
                
                # Import module dynamically to modify its global content
                import agents.researcher as res_mod
                res_mod.pdf_content = pdf_text
                
            st.success(f"Successfully processed: {uploaded_file.name} ({len(pdf_text)} characters loaded)")
            
            question = st.text_input("Ask a question about the document:", placeholder="e.g., What is the main thesis of Chapter 3?")
            
            if st.button("Ask Research Agent"):
                if not question:
                    st.warning("Please write a question first.")
                else:
                    with st.spinner("Research Agent is reading document contents..."):
                        try:
                            # Prompt the agent to answer the question using the tool
                            prompt = f"Question: {question}"
                            result = run_agent_sync(researcher_agent, prompt)
                            st.markdown("<div class='premium-card'><h4>Agent Answer</h4></div>", unsafe_allow_html=True)
                            st.markdown(result)
                        except Exception as e:
                            st.error(f"Execution Error: {e}")

# ==================== MODULE 4: SUMMARY AGENT ====================
elif module == "Summary Agent":
    st.markdown("<div class='agent-header'>Summary Agent 📝</div>", unsafe_allow_html=True)
    st.markdown("<div class='agent-subtitle'>Paste lecture transcripts, textbook chapters, or raw notes, and get structured, easy-to-read revision summaries.</div>", unsafe_allow_html=True)

    if not api_key_configured:
        st.error("Please configure your API key to run this agent.")
    else:
        raw_material = st.text_area("Paste your study material here:", height=250, placeholder="Paste study guides, notes, transcripts, or articles...")
        
        if st.button("Generate Summary"):
            if not raw_material.strip():
                st.warning("Please paste some content first.")
            else:
                with st.spinner("Summary Agent is formatting study notes..."):
                    try:
                        result = run_agent_sync(summarizer_agent, raw_material)
                        st.markdown("<div class='premium-card'><h4>Structured Study Notes</h4></div>", unsafe_allow_html=True)
                        st.markdown(result)
                        
                        st.download_button(
                            label="📥 Download Study Notes",
                            data=result,
                            file_name="Study_Summary.md",
                            mime="text/markdown"
                        )
                    except Exception as e:
                        st.error(f"Execution Error: {e}")

# ==================== MODULE 5: QUIZ AGENT ====================
elif module == "Quiz Agent":
    st.markdown("<div class='agent-header'>Quiz Agent ❓</div>", unsafe_allow_html=True)
    st.markdown("<div class='agent-subtitle'>Generate interactive multiple-choice quizzes from study notes or topics to test your comprehension.</div>", unsafe_allow_html=True)

    if not api_key_configured:
        st.error("Please configure your API key to run this agent.")
    else:
        quiz_source = st.text_area(
            "Paste your study notes or type a topic to generate a quiz from:",
            height=150,
            placeholder="e.g. Paste notes on photosynthesis, or type 'Machine Learning Basics'"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Generate Interactive Quiz"):
                if not quiz_source.strip():
                    st.warning("Please enter study notes or a topic first.")
                else:
                    with st.spinner("Quiz Agent is drafting questions..."):
                        try:
                            # Generate quiz (the agent is instructed to return raw JSON list)
                            raw_json = run_agent_sync(quizzer_agent, quiz_source)
                            
                            # Parse JSON output
                            quiz_data = json.loads(raw_json.strip())
                            
                            # Save to session state so interactive elements persist
                            st.session_state.quiz = quiz_data
                            st.session_state.answers = {}
                            st.session_state.score = None
                        except Exception as e:
                            st.error(f"Failed to generate quiz. Please try again. Detail: {e}")
                            st.write("Raw response:", raw_json if 'raw_json' in locals() else "None")
        
        with col2:
            if st.button("Clear Quiz"):
                st.session_state.quiz = None
                st.session_state.answers = {}
                st.session_state.score = None
                st.rerun()

        # Render the Quiz interactively if it has been generated
        if st.session_state.get("quiz"):
            st.write("---")
            st.markdown("### Interactive Assessment")
            
            # Show questions
            for idx, q_item in enumerate(st.session_state.quiz):
                st.markdown(f"**Q{idx+1}: {q_item['question']}**")
                
                # Retrieve previously chosen index if it exists
                current_selection = st.session_state.answers.get(idx, None)
                
                # Radio group for options
                selected_opt = st.radio(
                    f"Choose an option for Q{idx+1}",
                    q_item['options'],
                    key=f"q_{idx}",
                    index=None if current_selection is None else q_item['options'].index(current_selection)
                )
                
                if selected_opt:
                    st.session_state.answers[idx] = selected_opt
                st.write("")

            # Evaluate submission
            if st.button("Submit Quiz"):
                if len(st.session_state.answers) < len(st.session_state.quiz):
                    st.warning("Please answer all questions before submitting.")
                else:
                    correct_count = 0
                    st.markdown("### Quiz Results & Explanations")
                    
                    for idx, q_item in enumerate(st.session_state.quiz):
                        user_ans = st.session_state.answers[idx]
                        correct_ans = q_item['correct_answer']
                        
                        st.markdown(f"**Question {idx+1}:** {q_item['question']}")
                        
                        if user_ans == correct_ans:
                            st.success(f"🎯 **Your Answer:** {user_ans} (Correct!)")
                            correct_count += 1
                        else:
                            st.error(f"❌ **Your Answer:** {user_ans} | **Correct Answer:** {correct_ans}")
                        
                        st.info(f"💡 **Explanation:** {q_item['explanation']}")
                        st.write("---")
                    
                    total_q = len(st.session_state.quiz)
                    st.session_state.score = (correct_count, total_q)
                    percentage = (correct_count / total_q) * 100 if total_q else 0
                    st.balloons()
                    st.success(f"### 🎉 Quiz Finished! Final Score: **{correct_count}/{len(st.session_state.quiz)}** ({percentage:.1f}%)")

# ==================== MODULE 6: RESOURCE AGENT ====================
elif module == "Resource Agent":
    st.markdown("<div class='agent-header'>Resource Agent 🔗</div>", unsafe_allow_html=True)
    st.markdown("<div class='agent-subtitle'>Submit a learning topic to receive curated external study recommendations, courses, tutorials, and books.</div>", unsafe_allow_html=True)

    if not api_key_configured:
        st.error("Please configure your API key to run this agent.")
    else:
        topic = st.text_input("Enter the topic or field of study:", placeholder="e.g., Deep Learning, Organic Chemistry basics")
        
        if st.button("Fetch Learning Resources"):
            if not topic.strip():
                st.warning("Please type a topic first.")
            else:
                with st.spinner("Resource Agent is curating external links and materials..."):
                    try:
                        result = run_agent_sync(resourcer_agent, topic)
                        st.markdown("<div class='premium-card'><h4>Curated Resources</h4></div>", unsafe_allow_html=True)
                        st.markdown(result)
                    except Exception as e:
                        st.error(f"Execution Error: {e}")
