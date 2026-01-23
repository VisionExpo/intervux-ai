# Function to load external CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<styles>{f.read()}</styles>', unsafe_allow_html=True)
    

# Load the CSS file
load_css("frontend/assets/styles/styles.css")

# --- MAIN LAYOUT ---
st.markdown('<div class="main-header"> PrepMaster: 3D AI Interviewer</div>',unsafe_allow_html=True)