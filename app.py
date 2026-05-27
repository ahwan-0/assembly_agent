import streamlit as st
import base64
import sys
import os
from pipeline import run_research_pipeline

# ==========================================
# 1. PAGE CONFIGURATION & SESSION STATE
# ==========================================
st.set_page_config(
    page_title="Assembly Research AI",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "research_state" not in st.session_state:
    st.session_state.research_state = "idle" # idle, running, completed
if "final_results" not in st.session_state:
    st.session_state.final_results = None

# ==========================================
# 2. LOCAL BACKGROUND IMAGE HANDLER
# ==========================================
BACKGROUND_IMAGE_PATH = "imagei.jpg" # Make sure this matches your file

def get_base64_image(image_path):
    if not os.path.exists(image_path):
        print(f"\n[WARNING] Could not find background image at: {os.path.abspath(image_path)}")
        return None
        
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

bg_base64 = get_base64_image(BACKGROUND_IMAGE_PATH)

# ==========================================
# 3. GLOBAL CSS STYLING
# ==========================================
if bg_base64:
    bg_css = f'background-image: url("data:image/jpeg;base64,{bg_base64}");'
else:
    bg_css = 'background: linear-gradient(135deg, #1a1a1a, #000000);'

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

    /* Global App Background */
    .stApp {{
        {bg_css}
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        font-family: 'Inter', sans-serif;
    }}

    /* Hide standard Streamlit header and footer */
    header, footer {{ visibility: hidden; }}
    
    .block-container {{ 
        padding-top: 3rem !important; 
        max-width: 95% !important; 
    }}

    /* Top Navigation Typography */
    .nav-container {{
        display: flex;
        justify-content: space-between;
        color: white;
        margin-bottom: 120px; 
    }}
    .nav-left h1 {{ margin: 0; font-size: 28px; font-weight: 800; letter-spacing: 1px; line-height: 1.1; }}
    .nav-left p {{ margin: 0; font-size: 14px; font-weight: 600; letter-spacing: 0.5px; opacity: 0.9; }}
    .nav-right {{ display: flex; gap: 30px; font-weight: 600; font-size: 15px; align-items: flex-start; margin-top: 10px; }}
    .nav-right a {{ color: white; text-decoration: none; transition: opacity 0.3s; cursor: pointer; }}
    .nav-right a:hover {{ opacity: 0.7; }}

    /* Left Design Element (0 degrees) */
    .design-element-0 {{ font-size: 120px; font-weight: 300; color: white; line-height: 1; margin: 0; padding: 0; letter-spacing: -5px; }}
    .design-element-sub {{ display: flex; gap: 15px; color: rgba(255,255,255,0.7); font-size: 10px; font-weight: 800; letter-spacing: 2px; margin-top: -10px; align-items: center; }}
    .box-search {{ border: 1px solid white; padding: 2px 6px; color: white; }}

    /* Right Interactive Area Typography */
    .topic-heading {{ color: white; font-size: 26px; font-weight: 800; margin-bottom: 10px; text-shadow: 0px 2px 10px rgba(0,0,0,0.5); }}

    /* Override Streamlit Text Input */
    div[data-testid="stTextInput"] input {{
        background-color: white !important;
        color: black !important;
        border-radius: 50px !important;
        padding: 15px 25px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        border: none !important;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.2) !important;
    }}
    div[data-testid="stTextInput"] input::placeholder {{ color: #555 !important; font-weight: 400 !important; }}
    div[data-testid="stTextInput"] label {{ display: none !important; }}

    /* Override Streamlit Button */
    div[data-testid="stButton"] button {{
        background-color: white !important;
        color: black !important;
        border-radius: 0px !important;
        padding: 10px 30px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        border: none !important;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.2) !important;
        transition: all 0.3s ease !important;
        white-space: nowrap !important; /* Fixes the text wrapping issue */
        min-width: 140px !important; /* Ensures the button has enough width */
    }}
    div[data-testid="stButton"] button:hover {{ background-color: #e0e0e0 !important; transform: scale(1.02); }}

    /* Console Area Styling */
    .console-header {{ 
        color: white; 
        font-size: 20px; 
        font-weight: 800; 
        display: flex; 
        align-items: center; 
        gap: 10px; 
        margin-top: 180px; 
        margin-bottom: 15px; 
    }}
    .console-header::before {{ content: "•"; font-size: 24px; line-height: 0; }}
    .console-box {{
        background: rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(10px);
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        padding: 25px;
        color: #ddd;
        font-family: 'Courier New', monospace;
        min-height: 200px;
        border-radius: 5px;
        font-size: 14px;
        line-height: 1.6;
    }}
    
    /* Result Cards */
    .result-section {{ background: rgba(0, 0, 0, 0.7); backdrop-filter: blur(15px); padding: 30px; border-radius: 10px; color: white; margin-top: 20px; border: 1px solid rgba(255, 255, 255, 0.15); }}
    .result-section h2 {{ border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 10px; margin-bottom: 20px; }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 4. LIVE CONSOLE INTERCEPTOR
# ==========================================
class LiveConsoleLogger:
    def __init__(self, st_placeholder):
        self.st_placeholder = st_placeholder
        self.log_text = "getting your query from web ..\n\n"
        self._update_ui()
        self.original_stdout = sys.stdout

    def write(self, text):
        self.log_text += text
        self._update_ui()
        self.original_stdout.write(text)

    def _update_ui(self):
        html_content = f'<div class="console-box">{self.log_text.replace(chr(10), "<br>")}</div>'
        self.st_placeholder.markdown(html_content, unsafe_allow_html=True)

    def flush(self):
        self.original_stdout.flush()

# ==========================================
# 5. UI LAYOUT BUILDER
# ==========================================
st.markdown("""
    <div class="nav-container">
        <div class="nav-left">
            <h1>ASSEMBLY</h1>
            <p>Multi Agent Research AI</p>
        </div>
        <div class="nav-right">
            <a>Github</a>
            <a>Docs</a>
        </div>
    </div>
""", unsafe_allow_html=True)

col_left, col_space, col_right = st.columns([1, 2.2, 1])

with col_left:
    st.markdown("""
        <h1 class="design-element-0">0°</h1>
        <div class="design-element-sub">
            <span class="box-search">SEARCH</span>
            <span>CAUTION</span>
            <span>EXPLAIN</span>
        </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="topic-heading">Enter your research topic</div>', unsafe_allow_html=True)
    topic = st.text_input("Hidden label", placeholder="i.e Quantium basic concepts")
    
    # Adjusted column ratio here to give the button more room
    col_btn, _ = st.columns([1.5, 1.5])
    with col_btn:
        run_btn = st.button("Run Research")

# ==========================================
# 6. EXECUTION & CONSOLE LOGIC
# ==========================================
st.markdown('<div class="console-header">Research Console</div>', unsafe_allow_html=True)
console_placeholder = st.empty()

if st.session_state.research_state == "idle":
    console_placeholder.markdown('<div class="console-box">System idle. Waiting for query...</div>', unsafe_allow_html=True)

if run_btn and topic:
    st.session_state.research_state = "running"
    logger = LiveConsoleLogger(console_placeholder)
    sys.stdout = logger
    
    try:
        results = run_research_pipeline(topic)
        st.session_state.final_results = results
        st.session_state.research_state = "completed"
        
    except Exception as e:
        print(f"\n[ERROR] Pipeline failed to execute: {str(e)}")
        st.session_state.research_state = "idle"
        
    finally:
        sys.stdout = logger.original_stdout
        st.rerun()

# ==========================================
# 7. STATE B: FINAL RESULTS RENDER
# ==========================================
if st.session_state.research_state == "completed" and st.session_state.final_results:
    console_placeholder.empty() 
    
    report_data = st.session_state.final_results.get("report", "No report drafted.")
    feedback_data = st.session_state.final_results.get("feedback", "No critique available.")
    
    _, content_col, _ = st.columns([0.5, 3, 0.5])
    
    with content_col:
        st.markdown(f"""
            <div class="result-section">
                <h2>Generated Research Report</h2>
                <div>{report_data}</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
            <div class="result-section" style="margin-top: 20px;">
                <h2>Agent Critic Feedback</h2>
                <div style="color: #bbb;">{feedback_data}</div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Start New Research"):
            st.session_state.research_state = "idle"
            st.session_state.final_results = None
            st.rerun()
















