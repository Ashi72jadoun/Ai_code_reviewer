import streamlit as st
import os
import base64
from llm_reviewer import generate_code_review

# Page Configuration
st.set_page_config(
    page_title="Aura AI - Code Reviewer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State for Theme toggle if not already present
if "theme" not in st.session_state:
    st.session_state.theme = "Dark Mode"

# Helper function to load image safely as base64 string
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

# Convert our transparency logo image to inline visual string
logo_base64 = get_base64_image("assets/aj_watermark.png")

# Sidebar Info (Without theme switch since it's now on main UI)
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/bot.png", width=70)
    st.title("Aura AI")
    st.markdown("---")
    st.markdown("### ⚡ Aura Features")
    st.markdown("- 🔍 **Git Diff Extraction**")
    st.markdown("- 🛡️ **Bandit Security Audit**")
    st.markdown("- 🎨 **Ruff Linter Checks**")
    st.markdown("- 🤖 **Context-Aware AI Review**")
    st.markdown("---")
    st.success("System Status: Ready 🟢")

# Dynamic CSS Theme Selector based on session state
if st.session_state.theme == "Dark Mode":
    bg_style = """
        background: 
            radial-gradient(circle at 80% 20%, rgba(255, 87, 34, 0.08) 0%, transparent 40%),
            radial-gradient(circle at 20% 80%, rgba(99, 102, 241, 0.08) 0%, transparent 40%),
            linear-gradient(135deg, #0b0f19 0%, #111827 50%, #0b0f19 100%);
        color: #f3f4f6;
    """
    card_bg = "rgba(31, 41, 55, 0.6)"
    text_color = "#f9fafb"
    subtext_color = "#9ca3af"
    input_bg = "rgba(17, 24, 39, 0.8)"
    watermark_opacity = "0.03"
else:
    # Light Mode Styling
    bg_style = """
        background: 
            radial-gradient(circle at 80% 20%, rgba(255, 112, 67, 0.1) 0%, transparent 40%),
            radial-gradient(circle at 20% 80%, rgba(99, 102, 241, 0.08) 0%, transparent 40%),
            linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%);
        color: #0f172a;
    """
    card_bg = "rgba(255, 255, 255, 0.8)"
    text_color = "#0f172a"
    subtext_color = "#475569"
    input_bg = "#ffffff"
    watermark_opacity = "0.05"

st.markdown(f"""
<style>
    /* Main Background with Dynamic Theme Gradient */
    .stApp {{
        {bg_style}
    }}

    /* Top-Right Container for Watermark & Theme Switcher */
    .top-right-bar {{
        position: absolute;
        top: 20px;
        right: 30px;
        z-index: 1000;
        display: flex;
        align-items: center;
        gap: 15px;
    }}

    /* Top-Right Custom 'AJ' Image Overlay Watermark */
    .aj-watermark img {{
        height: 35px;
        width: auto;
        object-fit: contain;
        opacity: 0.7;
        transition: opacity 0.3s ease;
    }}
    .aj-watermark img:hover {{
        opacity: 0.95;
    }}

    /* Watermark AI Mascot Background Overlay */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 600px;
        height: 600px;
        background-image: url('https://img.icons8.com/isometric/500/bot.png');
        background-repeat: no-repeat;
        background-position: center;
        background-size: contain;
        opacity: {watermark_opacity};
        pointer-events: none;
        z-index: 0;
    }}

    /* Hero Header Section */
    .hero-container {{
        text-align: center;
        padding: 2.5rem 1rem 1rem 1rem;
    }}
    
    .hero-title {{
        font-size: 3.2rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(90deg, #ff5722 0%, #ff8c00 50%, #ff3d00 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }}

    .hero-subtitle {{
        font-size: 1.2rem;
        color: {subtext_color};
        max-width: 750px;
        margin: 0 auto 1.8rem auto;
        line-height: 1.6;
    }}

    /* Input Box Customization */
    .stTextInput > div > div > input {{
        background-color: {input_bg} !important;
        color: {text_color} !important;
        border: 1px solid rgba(255, 87, 34, 0.3) !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
        font-size: 1rem !important;
    }}
    
    .stTextInput > div > div > input:focus {{
        border-color: #ff5722 !important;
        box-shadow: 0 0 0 2px rgba(255, 87, 34, 0.25) !important;
    }}

    /* Premium Orange Action Button */
    .stButton > button {{
        background: linear-gradient(90deg, #ff5722 0%, #ff7043 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        box-shadow: 0 4px 20px rgba(255, 87, 34, 0.35) !important;
        transition: all 0.3s ease-in-out !important;
        width: 100%;
        margin-top: 10px;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(255, 87, 34, 0.5) !important;
        background: linear-gradient(90deg, #f4511e 0%, #ff5722 100%) !important;
    }}

    /* Metric Cards Styling */
    .metric-card {{
        background: {card_bg};
        border: 1px solid rgba(255, 87, 34, 0.2);
        border-radius: 12px;
        padding: 1.2rem;
        backdrop-filter: blur(12px);
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }}
    
    .metric-value {{
        font-size: 1.8rem;
        font-weight: 700;
        color: #ff5722;
    }}
    
    .metric-label {{
        font-size: 0.9rem;
        color: {subtext_color};
    }}
</style>
""", unsafe_allow_html=True)

# Top-Right Floating Controls (Theme Toggle Button + AJ Watermark)
col_dummy, col_btn = st.columns([10, 1])
with col_btn:
    # Small sleek toggle button on top right header area
    toggle_label = "🌙" if st.session_state.theme == "Dark Mode" else "☀️"
    if st.button(toggle_label, help="Toggle Dark/Light Mode"):
        if st.session_state.theme == "Dark Mode":
            st.session_state.theme = "Light Mode"
        else:
            st.session_state.theme = "Dark Mode"
        st.rerun()

# Render AJ Watermark beside/near the header right
if logo_base64:
    st.markdown(f"""
        <div class="top-right-bar">
            <div class="aj-watermark">
                <img src="data:image/png;base64,{logo_base64}" alt="AJ Brand Logo Watermark">
            </div>
        </div>
    """, unsafe_allow_html=True)

# Hero Title & Subtitle Section
st.markdown("""
<div class="hero-container">
    <div class="hero-title">Aura Code Reviewer</div>
    <div class="hero-subtitle">Cut Code Review Time & Bugs in Half. Supercharge your entire team with AI-driven contextual feedback, security scans, and automated refactoring.</div>
</div>
""", unsafe_allow_html=True)

# Layout Columns for Metrics Overview
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="metric-card"><div class="metric-value">100%</div><div class="metric-label">Context-Aware Analysis</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="metric-card"><div class="metric-value">Real-Time</div><div class="metric-label">Security & Bug Detection</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="metric-card"><div class="metric-value">Zero</div><div class="metric-label">Manual Setup Required</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Main Input Form Section
repo_path = st.text_input("📂 Enter Local Repository Path", value="../sample-target-repo", help="Provide the relative or absolute path of your local Git project.")

if st.button("🚀 Analyze with Aura AI"):
    if not os.path.exists(repo_path):
        st.error(f"❌ Error: Path '{repo_path}' not found. Please check the directory path.")
    else:
        with st.spinner("🔍 Aura is analyzing diffs, running Bandit/Ruff scans, and generating insights..."):
            review_output = generate_code_review(repo_path)
            
            if not review_output or "No uncommitted changes found." in review_output:
                st.info("ℹ️ No uncommitted changes detected in this repository. Modify some code to trigger a review.")
            else:
                st.balloons()
                st.success("✅ Aura Code Review Completed!")
                
                # Display Output
                st.markdown("### 📋 Aura Review Findings & Refactoring Plan")
                st.markdown(review_output)

st.markdown("<br><hr>", unsafe_allow_html=True)
st.caption("Aura Code Reviewer • Autonomous AI Software Engineering Agent")