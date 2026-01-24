import streamlit as st
import os
import sys

# --- 1. SETUP PATHS ---
# Add project root to path se we can import from backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.agent_ocr import ResumeParser
from backend.core.llm_brain import InterviewerAI
from code_editor import code_editor

# --- 2. PAGE CONFIG & STYLES ---
st.set_page_config(
    page_title="PrepMaster AI",
    page_icon="👨‍🎓",
    layout="wide",
    initial_sidebar_state="expanded"
    )

# Load Custom CSS
def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("⚠ CSS file not found. Running in default mode.")

load_css("frontend/assets/styles/styles.css")

# --- 3. SESSION STATE ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "resume_data" not in st.session_state:
    st.session_state.resume_data = None
if "interviewer" not in st.session_state:
    st.session_state.interviewer = InterviewerAI()
if "interview_active" not in st.session_state:
    st.session_state.interview_active = False

# --- 4. MAIN LAYOUT ---
st.markdown('<div class="main-header">👨‍🎓 PrepMaster: 3D AI Interviewer</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1.5], gap="medium")

# === LEFT COLOMN: The Interviewer ===
with col1:
    st.markdown("### 🤖 Interviewer")
    # Placeholder for Avatar
    st.image("https://img.freepik.com/free-vector/cyborg-face-concept-illustration_114360-1768.jpg",
             caption="AI Interviewer (Active)", use_container_width=True)
    
    st.divider()

    # Statys Board
    if st.session_state.interview_active:
        st.success("🟢 Interview in Progress")
        st.markdown(f"**Candidate:** {st.session_state.resume_data.get('name', 'Unknown')}")
    else:
        st.info("🟡 Waiting for Resume...")


# === RIGHT COLUMN: Interaction ===
with col2:
    tab1, tab2, tab3 = st.tabs(["💬 Chat Transcript", "💻 Coding Sandbox", "📄 Resume"])

    # --- TAB 1: CHAT INTERFACE ---
    with tab1:
        st.markdown("### Conversation")

        # Display Chat History
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.chat_history:
                role_class = "chat-user" if msg["role"] == "user" else "chat-ai"
                st.markdown(f"""
                <div class="{role_class}">
                    <b>{'👤 You' if msg['role'] == 'user' else '🤖 PrepMaster'}</b><br>
                    {msg['content']}
                </div>
                """, unsafe_allow_html=True)

        # Chat Input (Only active if interview started)
        if st.session_state.interview_active:
            user_input = st.chat_input("Type your answer...")
            if user_input:
                # 1. Append User Message
                st.session_state.chat_history.append({"role": "user", "content": user_input})

                # 2. Get AI Response
                with st.spinner("Thinking..."):
                    ai_response = st.session_state.interviewer.get_response(user_input)

                # 3. Append AI Message
                st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                st.rerun()
        else:
            st.warning("⚠️ Please upload your resume in the 'Resume' tab to start.")

    
    # --- TAB 2: CODING SANDBOX (Placeholder) ---
    with tab2:
        st.markdown("### Coding Sandbox")
        st.info("This section will host the coding environment during technical rounds.")
        # code_editor("# Write your Python code here...", lang="python", height=200)

    # --- TAB 3: RESUME UPLOAD ---
    with tab3:
        st.markdown("### Upload Resume")
        uploaded_file = st.file_uploader("Upload PDF", type=["pdf"], key="resume_uploader")

        if uploaded_file is not None and not st.session_state.interview_active:
            # Save temp file
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            with st.spinner("🔍 Agent OCR is analyzing your resume..."):
                try:
                    # 1. Parse Resume
                    parser = ResumeParser()
                    data = parser.parse(temp_path)
                    st.session_state.resume_data = data

                    # 2. Start AI Session
                    first_question = st.session_state.interviewer.start_session(data)
                    st.session_state.chat_history.append({"role": "assistant", "content": first_question})

                    # 3. Activate State
                    st.session_state.interview_active = True
                    st.success("✅ Analysis Complete! Switching to Chat...")

                    # Cleanup
                    os.remove(temp_path)
                    st.rerun()

                except Exception as e:
                    st.error(f"Error: {str(e)}")