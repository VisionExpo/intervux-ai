import streamlit as st
import os
import sys
import asyncio
from dotenv import load_dotenv

load_dotenv()

# --- 1. SETUP PATHS ---
# Add project root to path se we can import from backend
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from backend.core.audio_stack import AudioEngine
from backend.core.agent_ocr import ResumeParser
from backend.core.llm_brain import InterviewerAI
from code_editor import code_editor
from backend.core.code_engine import CodeExecutor






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
if "audio_engine" not in st.session_state:
    st.session_state.audio_engine = AudioEngine()


# --- 4. MAIN LAYOUT ---
st.markdown('<div class="main-header">👨‍🎓 PrepMaster: 3D AI Interviewer</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1.5], gap="medium")

# === LEFT COLOMN: The Interviewer ===
with col1:
    st.markdown("### 🤖 Interviewer")
    # Placeholder for Avatar
    st.image("https://img.freepik.com/free-vector/cyborg-face-concept-illustration_114360-1768.jpg",
             caption="AI Interviewer (Active)", use_column_width=True)
    
    st.divider()

    # Status Board
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

            # Invisible div to auto-scroll to bottom
            st.markdown('<div id="end-of-chat"></div>', unsafe_allow_html=True)


        # Chat Input (Only active if interview started)
        if st.session_state.interview_active:
            col_mic, col_text = st.columns([1, 4])

            user_input = None

            # 1. AUDIO INPUT (Microphone)
            with col_mic:
                audio_val = st.audio_input("🎙️ Record")
                if audio_val:
                    # Save audio to temp file
                    with st.spinner("🔊 Transcribing..."):
                        temp_audio_path = "temp_input.wav"
                        with open(temp_audio_path, "wb") as f:
                            f.write(audio_val.getbuffer())

                        # Transcribe using Whisper (GPU)
                        text_from_audio = st.session_state.audio_engine.speech_to_text(temp_audio_path)
                        if text_from_audio:
                            user_input = text_from_audio

                        # Cleanup
                        os.remove(temp_audio_path)

            # 2. TEXT INPUT (Fallback)
            with col_text:
                text_val = st.chat_input("Type your answer...")
                if text_val:
                    user_input = text_val

            # --- PROCESS INOUT ---
            if user_input:
                # 1. Append User Message
                st.session_state.chat_history.append({"role": "user", "content": user_input})

                # 2. Get AI Response
                with st.spinner("Thinking..."):
                    ai_response = st.session_state.interviewer.get_response(user_input)

                # 3. Generate Audio Response (TTS)
                audio_file = f"frontend/assets/ai_reply.mp3"
                    
                # async function in sync Streamlit
                asyncio.run(st.session_state.audio_engine.text_to_speech(ai_response, audio_file))

                # 4. Append AI Message & Play Audio
                st.session_state.chat_history.append({"role": "assistant", "content": ai_response})

                # Auto-play Audio (Hidden Player)
                with col_text:
                    st.audio(audio_file, format="audio/mp3", autoplay=True)
                    
                st.experimental_rerun()
            else:
                st.warning("⚠️ Please upload your resume in the 'Resume' tab to start.")

    
    # --- TAB 2: CODING SANDBOX (Placeholder) ---
    # --- TAB 2: CODING SANDBOX ---
    with tab2:
        st.markdown("### 💻 Technical Assessment")
        
        # 1. Editor Configuration
        default_code = """# Question: Write a Python function to reverse a string.
def solve(text):
    return text[::-1]

print(solve("Hello World"))"""

        # 2. Render Editor
        response_dict = code_editor(default_code, lang="python", height=300, key="code_editor")
        
        # 3. Execution & AI Review Logic
        if response_dict['type'] == "submit" or st.button("🚀 Run & Review"):
            code_to_run = response_dict['text']
            
            # A. Execute Code
            with st.spinner("⚡ Compiling..."):
                output, error = CodeExecutor.run_code(code_to_run)
            
            # Show Execution Results
            st.markdown("---")
            if error:
                st.error("❌ Compilation Failed")
                st.code(error, language="text")
            else:
                st.success("✅ Execution Successful")
                st.code(output, language="text")
                
                # B. AI Code Review (Only if compile success)
                if st.session_state.interview_active:
                    with st.spinner("🧠 AI is reviewing your logic..."):
                        # We assume the 'problem' is implied in the code for now
                        # In Phase 3, we will make the problem dynamic
                        feedback = st.session_state.interviewer.review_code(
                            problem_desc="Reverse a string (General)", 
                            code_snippet=code_to_run,
                            execution_output=output
                        )
                    
                    # C. Display Feedback
                    with st.expander("🧐 AI Code Review", expanded=True):
                        st.markdown(feedback)
                        
                    # D. Speak the feedback!
                    audio_file = "frontend/assets/review_audio.mp3"
                    asyncio.run(st.session_state.audio_engine.text_to_speech("Code review complete. Check the feedback panel.", audio_file))
                    st.audio(audio_file, format="audio/mp3", autoplay=True)
                else:
                    st.info("ℹ️ Start the interview (Tab 3) to enable AI Grading.")
    

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