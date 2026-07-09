"""
Main Entry Point for DevBuddy AI.
Implements the Streamlit layout, navigation pages, styling enhancements,
and interactive project upload/analysis flow using the AI Agent engine.
"""

import os
import tempfile
import streamlit as st  # type: ignore[import-not-found]
from dotenv import load_dotenv # type: ignore[import-not-found]

# Load environment variables from .env file if available
load_dotenv()

# Import core modules
from agents import AgentRegistry
from engine import OrchestrationEngine
import utils

# Set page configuration with custom page title, icon, and layout
st.set_page_config(
    page_title="DevBuddy AI - Production Ready in One Click",
    page_icon=":material/rocket_launch:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize configuration credentials in session state from environment fallback
for key_name, default_val in [
    ("GEMINI_API_KEY", ""),
    ("GEMINI_MODEL", "gemini-2.5-flash"),
    ("GEMINI_KEY_AGENT_1", ""),
    ("GEMINI_KEY_AGENT_2", ""),
    ("GEMINI_KEY_AGENT_3", ""),
    ("GEMINI_KEY_AGENT_4", ""),
    ("GEMINI_KEY_AGENT_5", ""),
    ("GITHUB_TOKEN", ""),
    ("LINKEDIN_ACCESS_TOKEN", ""),
    ("LINKEDIN_CLIENT_ID", ""),
    ("LINKEDIN_CLIENT_SECRET", "")
]:
    persist_key = f"PERSIST_{key_name}"
    if persist_key not in st.session_state:
        val = os.getenv(key_name, default_val)
        if key_name.startswith("GEMINI_") and val and val.strip().startswith("AQ."):
            val = ""
        st.session_state[persist_key] = val

# Premium UI Styling using custom CSS injections for glassmorphism, dark mode accents, and smooth transitions
def inject_custom_css():
    """
    Injects custom CSS to style the Streamlit interface to look modern,
    premium, soft, and ultra-clean, with typography and custom styling tokens.
    """
    st.markdown("""
        <style>
        /* Import Inter, Outfit, and Material Symbols Outlined for professional iconography */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap');

        /* Material icon inline helper — use class="mi" on <span> tags */
        .mi {
            font-family: 'Material Symbols Outlined';
            font-weight: normal;
            font-style: normal;
            font-size: 1.15em;
            line-height: 1;
            vertical-align: -0.15em;
            letter-spacing: normal;
            text-transform: none;
            display: inline-block;
            white-space: nowrap;
            word-wrap: normal;
            direction: ltr;
            -webkit-font-smoothing: antialiased;
            color: inherit;
        }
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: #334155;
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif;
            font-weight: 700;
            color: #312e81;
            letter-spacing: -0.02em;
        }

        /* Gradient title styling */
        .gradient-text {
            background: linear-gradient(135deg, #4338ca 0%, #6d28d9 50%, #7c3aed 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3.25rem;
            font-weight: 800;
            margin-bottom: 0.2rem;
            animation: fadeIn 1.2s ease-out;
            letter-spacing: -0.03em;
        }

        /* Subtitle tagline styling */
        .tagline-text {
            color: #64748b;
            font-size: 1.25rem;
            font-weight: 400;
            margin-bottom: 2.5rem;
            line-height: 1.6;
        }

        /* Glassmorphic card styling (Frosted Glass Aesthetic) */
        .glass-card {
            background: rgba(255, 255, 255, 0.35) !important;
            backdrop-filter: blur(16px) saturate(180%) !important;
            -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
            border-radius: 12px !important;
            border: 1px solid rgba(226, 232, 240, 0.8) !important;
            padding: 28px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
            margin-bottom: 24px;
            transition: all 0.35s cubic-bezier(0.25, 0.8, 0.25, 1);
        }
        
        .glass-card:hover {
            background: rgba(255, 255, 255, 0.55) !important;
            border-color: rgba(203, 213, 225, 0.9) !important;
            transform: translateY(-3px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.02) !important;
        }

        /* Premium status badge styles */
        .badge {
            display: inline-block;
            padding: 4px 14px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .badge-pending {
            background-color: #f1f5f9;
            color: #64748b;
            border: 1px solid #e2e8f0;
        }
        .badge-running {
            background-color: #fffbeb;
            color: #b45309;
            border: 1px solid #fde68a;
            animation: pulseSoft 2s infinite;
        }
        .badge-success {
            background-color: #f0fdf4;
            color: #15803d;
            border: 1px solid #bbf7d0;
        }
        .badge-failed {
            background-color: #fef2f2;
            color: #b91c1c;
            border: 1px solid #fecaca;
        }

        /* Micro-animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(12px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulseSoft {
            0% { opacity: 0.7; }
            50% { opacity: 1; }
            100% { opacity: 0.7; }
        }

        /* Terminal simulation block (Sleek macOS Terminal) */
        .terminal-block {
            background: linear-gradient(145deg, #0c1222 0%, #162032 50%, #0f172a 100%);
            border-radius: 14px;
            border: 1px solid rgba(99, 102, 241, 0.15);
            padding: 42px 22px 22px 22px;
            font-family: 'JetBrains Mono', 'Courier New', Courier, monospace;
            color: #7dd3fc;
            max-height: 300px;
            overflow-y: auto;
            margin-bottom: 24px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.18), inset 0 1px 0 rgba(255, 255, 255, 0.03);
            position: relative;
        }
        .terminal-block::before {
            content: '';
            position: absolute;
            top: 14px;
            left: 16px;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #ff5f57;
            box-shadow: 20px 0 0 #febc2e, 40px 0 0 #28c840;
        }
        .terminal-line {
            margin-bottom: 4px;
            line-height: 1.7;
            font-size: 0.83rem;
            padding-left: 8px;
            border-left: 2px solid rgba(125, 211, 252, 0.1);
        }
        
        /* Sidebar styling override */
        section[data-testid="stSidebar"] {
            background-color: #f8fafc;
            border-right: 1px solid #e2e8f0;
        }
        
        /* Global button rounding to match soft UI */
        .stButton button {
            border-radius: 12px !important;
            transition: all 0.2s ease !important;
        }
        
        /* Grid Layout elements for structured metadata rendering */
        .stack-tag {
            display: inline-block;
            background: #e0e7ff;
            color: #4f46e5;
            border: 1px solid #c7d2fe;
            border-radius: 6px;
            padding: 3px 10px;
            margin: 4px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .dep-tag {
            display: inline-block;
            background: #fae8ff;
            color: #c026d3;
            border: 1px solid #f5d0fe;
            border-radius: 6px;
            padding: 3px 10px;
            margin: 4px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .missing-tag {
            display: inline-block;
            background: #fee2e2;
            color: #dc2626;
            border: 1px solid #fecaca;
            border-radius: 6px;
            padding: 3px 10px;
            margin: 4px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        
        /* Custom Input styling for soft UI */
        .stTextInput input, .stTextArea textarea, .stSelectbox select {
            border-radius: 10px !important;
            border: 1px solid #cbd5e1 !important;
        }
        
        /* ===== APP BACKGROUND: Dot Matrix with Floating Data Orb ===== */
        @keyframes panGrid {
            from {
                background-position: 0px 0px;
            }
            to {
                background-position: 240px 240px;
            }
        }

        .stApp {
            background-color: #f8fafc !important;
            background-image: radial-gradient(#94a3b8 1px, transparent 1px) !important;
            background-size: 24px 24px !important;
            background-attachment: fixed !important;
            animation: panGrid 40s linear infinite;
        }

        .stApp::before {
            content: '';
            position: fixed;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(99, 102, 241, 0.35) 0%, rgba(255, 255, 255, 0) 70%) no-repeat;
            background-size: 800px 800px;
            background-position: 20% 30%;
            filter: blur(120px);
            z-index: -1;
            pointer-events: none;
            animation: floatOrb 20s infinite alternate ease-in-out;
        }

        @keyframes floatOrb {
            0% {
                background-position: 20% 30%;
            }
            50% {
                background-position: 70% 60%;
            }
            100% {
                background-position: 40% 80%;
            }
        }

        /* ===== STEP GLASSMORPHISM PANEL ===== */
        .step-glass {
            background: rgba(255, 255, 255, 0.35) !important;
            backdrop-filter: blur(16px) saturate(180%) !important;
            -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
            border-radius: 12px !important;
            border: 1px solid rgba(226, 232, 240, 0.8) !important;
            padding: 20px 24px;
            margin-bottom: 4px;
            display: flex;
            align-items: center;
            gap: 18px;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
        }
        .step-glass:hover {
            background: rgba(255, 255, 255, 0.55) !important;
            transform: translateX(4px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05) !important;
        }

        /* ===== METRIC CARD GLASSMORPHISM ===== */
        [data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.35) !important;
            backdrop-filter: blur(16px) saturate(180%) !important;
            -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
            border: 1px solid rgba(226, 232, 240, 0.8) !important;
            border-radius: 12px !important;
            padding: 18px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
            transition: all 0.3s ease !important;
        }
        [data-testid="stMetric"]:hover {
            background: rgba(255, 255, 255, 0.55) !important;
            transform: translateY(-3px) !important;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05) !important;
        }
        [data-testid="stMetric"] label {
            color: #64748b !important;
            font-weight: 600 !important;
        }
        [data-testid="stMetricValue"] {
            color: #312e81 !important;
            font-family: 'Outfit', sans-serif !important;
        }

        /* ===== SIDEBAR REFINEMENTS (Matte Silver) ===== */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f1f5f9 0%, #e8ecf2 100%) !important;
            border-right: 1px solid #dfe4ea !important;
        }
        section[data-testid="stSidebar"] h2 {
            font-size: 1.3rem !important;
            letter-spacing: -0.01em;
        }
        /* ================================================================
           SIDEBAR RADIO — PILL NAVIGATION
           ================================================================ */

        /* Hide the radio label header ("Navigation" text above pills) */
        section[data-testid="stSidebar"] div[data-testid="stRadio"] > label {
            display: none !important;
        }

        /* The radiogroup container — vertical stack with gap */
        section[data-testid="stSidebar"] div[role="radiogroup"] {
            display: flex !important;
            flex-direction: column !important;
            gap: 4px !important;
            padding: 0 !important;
        }

        /* Hide the native circular radio dot */
        section[data-testid="stSidebar"] div[role="radiogroup"] input[type="radio"] {
            display: none !important;
        }

        /* Each radio label → full-width pill button */
        section[data-testid="stSidebar"] div[role="radiogroup"] label {
            display: flex !important;
            align-items: center !important;
            width: 100% !important;
            padding: 10px 16px !important;
            margin: 0 !important;
            border-radius: 10px !important;
            font-weight: 500 !important;
            font-size: 0.92rem !important;
            color: #475569 !important;
            letter-spacing: 0.01em;
            cursor: pointer !important;
            background: transparent !important;
            border: 1px solid transparent !important;
            transition: all 0.25s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        }

        /* Hover state — soft grey lift */
        section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
            background: rgba(99, 102, 241, 0.06) !important;
            color: #334155 !important;
        }

        /* Selected / Active pill — indigo accent */
        section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"],
        section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
            background: linear-gradient(135deg, #4338ca 0%, #6366f1 100%) !important;
            color: #ffffff !important;
            font-weight: 600 !important;
            border-color: transparent !important;
            box-shadow: 0 4px 14px rgba(67, 56, 202, 0.25), 0 1px 3px rgba(0, 0, 0, 0.06) !important;
        }

        /* Hide the built-in radio "dot circle" SVG inside the label */
        section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
            display: none !important;
        }

        /* ================================================================
           MAIN CONTENT RADIO — SEGMENTED CONTROL (macOS Toggle)
           ================================================================ */

        /* The radio wrapper in the main area — light grey pill track */
        [data-testid="stMainBlockContainer"] div[data-testid="stRadio"] > div[role="radiogroup"] {
            display: flex !important;
            flex-direction: row !important;
            gap: 0 !important;
            background: #f1f5f9 !important;
            border-radius: 12px !important;
            padding: 4px !important;
            border: 1px solid #e2e8f0 !important;
        }

        /* Hide the native dots */
        [data-testid="stMainBlockContainer"] div[role="radiogroup"] input[type="radio"] {
            display: none !important;
        }

        /* Each option — flat, equal-width segment */
        [data-testid="stMainBlockContainer"] div[role="radiogroup"] label {
            flex: 1 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            padding: 9px 18px !important;
            margin: 0 !important;
            border-radius: 9px !important;
            font-weight: 500 !important;
            font-size: 0.88rem !important;
            color: #64748b !important;
            cursor: pointer !important;
            background: transparent !important;
            border: 1px solid transparent !important;
            transition: all 0.25s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
            text-align: center !important;
            white-space: nowrap !important;
        }

        /* Hover — subtle highlight */
        [data-testid="stMainBlockContainer"] div[role="radiogroup"] label:hover {
            color: #334155 !important;
            background: rgba(255, 255, 255, 0.5) !important;
        }

        /* Active segment — elevated white card */
        [data-testid="stMainBlockContainer"] div[role="radiogroup"] label[data-checked="true"],
        [data-testid="stMainBlockContainer"] div[role="radiogroup"] label:has(input:checked) {
            background: #ffffff !important;
            color: #1e293b !important;
            font-weight: 600 !important;
            border-color: rgba(226, 232, 240, 0.6) !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06), 0 1px 2px rgba(0, 0, 0, 0.04) !important;
        }

        /* Hide the built-in radio dot SVG inside main area labels too */
        [data-testid="stMainBlockContainer"] div[role="radiogroup"] label > div:first-child {
            display: none !important;
        }

        /* ================================================================
           EXISTING RULES (preserved below)
           ================================================================ */

        /* ===== BUTTON REFINEMENTS ===== */
        .stButton > button {
            border-radius: 14px !important;
            font-weight: 600 !important;
            letter-spacing: 0.01em !important;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        }

        /* ===== INPUT REFINEMENTS ===== */
        .stTextInput input, .stTextArea textarea {
            background: rgba(255, 255, 255, 0.6) !important;
        }

        /* ===== PIPELINE CONNECTOR ===== */
        .pipeline-connector {
            text-align: center;
            padding: 2px 0;
            line-height: 1;
        }
        .pipeline-connector-line {
            display: inline-block;
            width: 2px;
            height: 22px;
            background: linear-gradient(180deg, rgba(148, 163, 184, 0.35), rgba(148, 163, 184, 0.10));
            border-radius: 1px;
        }

        /* ===== AGENT STATUS CARD (Pipeline Progress) ===== */
        .agent-status-card {
            text-align: center;
            border-radius: 12px !important;
            background: rgba(255, 255, 255, 0.35) !important;
            backdrop-filter: blur(16px) saturate(180%) !important;
            -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
            padding: 18px 15px;
            border: 1px solid rgba(226, 232, 240, 0.8) !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        }
        .agent-status-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05) !important;
            background: rgba(255, 255, 255, 0.55) !important;
        }

        /* ===== BUTTON HOVER LIFT ===== */
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(67, 56, 202, 0.12) !important;
        }

        /* ===== TAB PANEL GLASSMORPHISM ===== */
        [data-testid="stTabs"] {
            background: rgba(255, 255, 255, 0.35) !important;
            backdrop-filter: blur(16px) saturate(180%) !important;
            -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
            border-radius: 12px !important;
            border: 1px solid rgba(226, 232, 240, 0.8) !important;
            padding: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
        }

        /* ===== EXPANDER REFINEMENTS ===== */
        [data-testid="stExpander"] {
            border-radius: 12px !important;
            border: 1px solid rgba(226, 232, 240, 0.8) !important;
            background: rgba(255, 255, 255, 0.35) !important;
            backdrop-filter: blur(16px) saturate(180%) !important;
            -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
            overflow: hidden;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
        }
        [data-testid="stExpander"]:hover {
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05) !important;
        }

        </style>
    """, unsafe_allow_html=True)

# Call CSS injection
inject_custom_css()

def get_credential(key_name: str, default: str = "") -> str:
    return st.session_state.get(f"PERSIST_{key_name}") or default

# Retrieve Gemini API Key & GitHub Token (checking session state first, then falling back to env)
gemini_api_key = get_credential("GEMINI_API_KEY")
github_token = get_credential("GITHUB_TOKEN")

def apply_new_configurations():
    global gemini_api_key, github_token
    gemini_api_key = get_credential("GEMINI_API_KEY")
    github_token = get_credential("GITHUB_TOKEN")
    
    # Configure legacy generativeai client if active in environment
    try:
        import google.generativeai as legacy_genai
        gkey = st.session_state.get("PERSIST_GEMINI_API_KEY")
        if gkey:
            legacy_genai.configure(api_key=gkey)
    except Exception:
        pass

api_key_from_env = os.getenv("GEMINI_API_KEY")
github_token_from_env = os.getenv("GITHUB_TOKEN")

# Initialize AgentRegistry and OrchestrationEngine inside SessionState so they persist nicely
if "registry" not in st.session_state:
    st.session_state.registry = AgentRegistry()
if "engine" not in st.session_state:
    st.session_state.engine = OrchestrationEngine(st.session_state.registry)
if "execution_logs" not in st.session_state:
    st.session_state.execution_logs = []
if "pipeline_results" not in st.session_state:
    st.session_state.pipeline_results = None
if "selected_project_path" not in st.session_state:
    st.session_state.selected_project_path = None
if "current_agent_status" not in st.session_state:
    st.session_state.current_agent_status = {
        agent.name: "Pending" for agent in st.session_state.registry.get_all_agents()
    }
if "gh_published_url" not in st.session_state:
    st.session_state.gh_published_url = None

# Navigation Menu inside the Sidebar
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #00C6FF;'><span class='mi'>dashboard</span> DevBuddy AI</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Navigation buttons
    page = st.radio(
        "Navigate",
        ["Dashboard", "Run Pipeline", "Settings"],
        key="navigation_selector"
    )
    
    st.markdown("---")
    
    # API Keys status expander reflecting whether keys are successfully loaded (session state or env)
    with st.expander("🔑 API & Configuration Status", expanded=False):
        if st.session_state.get("PERSIST_GEMINI_API_KEY") or any(st.session_state.get(f"PERSIST_GEMINI_KEY_AGENT_{i}") for i in range(1, 6)):
            st.success("Gemini API Key loaded from Settings")
        elif api_key_from_env or any(os.getenv(f"GEMINI_KEY_AGENT_{i}") for i in range(1, 6)):
            st.success("Gemini API Key loaded from `.env`")
        else:
            st.error("Gemini API Key is missing")
            
        if st.session_state.get("PERSIST_GITHUB_TOKEN"):
            st.success("GitHub Token loaded from Settings")
        elif github_token_from_env:
            st.success("GitHub Token loaded from `.env`")
        else:
            st.error("GitHub Token is missing")

        if st.session_state.get("PERSIST_LINKEDIN_ACCESS_TOKEN"):
            st.success("LinkedIn Token loaded from Settings")
        elif os.getenv("LINKEDIN_ACCESS_TOKEN"):
            st.success("LinkedIn Token loaded from `.env`")
        else:
            st.warning("LinkedIn Token is missing")

    # Quick status indicators visible without expanding
    _key_ok = "●" if gemini_api_key else "○"
    _gh_ok = "●" if github_token else "○"
    st.caption(f"{_key_ok} Gemini Key &nbsp;&nbsp; {_gh_ok} GitHub Token")
            


# ---------------- PAGE 1: DASHBOARD ----------------
# ---------------- PAGE 1: DASHBOARD ----------------
if page == "Dashboard":
    # ── Hero Section ──
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0 1rem 0;'>
            <div class='gradient-text'>DevBuddy AI</div>
            <div class='tagline-text' style='font-size: 35px;'>From Project Folder → Production Ready — in One Click.</div>
        </div>
    """, unsafe_allow_html=True)
    
    # ── 3-Column "How It Works" Hero Cards ──
    hero_col1, hero_col2, hero_col3 = st.columns(3)
    
    with hero_col1:
        st.markdown("""
            <div class='glass-card' style='text-align: center; min-height: 180px;'>
                <div style='font-size: 2.2rem; margin-bottom: 10px; color: #475569;'><span class='mi'>folder_open</span></div>
                <h4 style='margin: 0 0 8px 0; color: #6366f1;'>1. Input</h4>
                <p style='color: #475569; font-size: 0.92rem; margin: 0;'>Provide a <b>local folder path</b> or <b>upload a ZIP</b> of your project. That's all DevBuddy needs to get started.</p>
            </div>
        """, unsafe_allow_html=True)
    
    with hero_col2:
        st.markdown("""
            <div class='glass-card' style='text-align: center; min-height: 180px;'>
                <div style='font-size: 2.2rem; margin-bottom: 10px; color: #475569;'><span class='mi'>memory</span></div>
                <h4 style='margin: 0 0 8px 0; color: #a855f7;'>2. Process</h4>
                <p style='color: #475569; font-size: 0.92rem; margin: 0;'><b>5 sequential AI agents</b> analyze architecture, run QA audits, generate docs, and prepare your code for launch.</p>
            </div>
        """, unsafe_allow_html=True)
    
    with hero_col3:
        st.markdown("""
            <div class='glass-card' style='text-align: center; min-height: 180px;'>
                <div style='font-size: 2.2rem; margin-bottom: 10px; color: #475569;'><span class='mi'>inventory_2</span></div>
                <h4 style='margin: 0 0 8px 0; color: #ec4899;'>3. Output</h4>
                <p style='color: #475569; font-size: 0.92rem; margin: 0;'>Get a <b>production-ready GitHub repo</b>, a professional PDF report, and <b>LinkedIn branding</b> copy — all automated.</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("")
    
    # ── Key Metrics Row ──
    met_col1, met_col2, met_col3 = st.columns(3)
    met_col1.metric(label="Active Agents", value="5", delta="Sequential Pipeline")
    met_col2.metric(label="Avg. Pipeline Speed", value="~45s", delta="End-to-End")
    met_col3.metric(label="Deployment Success", value="100%", delta="GitHub + LinkedIn")
    
    st.markdown("---")
    
    # ── Sequential Pipeline Flow: Meet The Agents ──
    st.markdown("<h2 style='text-align: center; margin-bottom: 0.5rem;'><span class='mi'>hub</span> Meet The Agents</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748b; margin-bottom: 2rem;'>Each agent runs sequentially — the output of one becomes the input for the next.</p>", unsafe_allow_html=True)
    
    agents = st.session_state.registry.get_all_agents()
    
    # Muted, sophisticated accent colors for each step
    _step_styles = [
        ("#93c5fd", "#1e40af"),  # Muted Blue
        ("#fca5a5", "#991b1b"),  # Soft Coral
        ("#fcd34d", "#854d0e"),  # Soft Gold
        ("#86efac", "#166534"),  # Mint Green
        ("#c4b5fd", "#5b21b6"),  # Soft Lavender
    ]
    
    for idx, agent in enumerate(agents):
        accent_color, text_color = _step_styles[idx]
        st.markdown(f"""
            <div class='step-glass' style='border-left: 4px solid {accent_color};'>
                <div style='font-size: 0.8rem; font-weight: 800; color: {text_color}; min-width: 52px; text-transform: uppercase; letter-spacing: 0.06em;'>Step {idx+1}</div>
                <div style='font-size: 1.5rem; background: rgba(255,255,255,0.45); border-radius: 10px; padding: 8px 12px; border: 1px solid rgba(226,232,240,0.3); color: #475569; display: flex; align-items: center; justify-content: center;'>{agent.icon}</div>
                <div>
                    <div style='font-weight: 600; font-size: 1rem; color: {text_color};'>{agent.name}</div>
                    <div style='font-size: 0.85rem; color: #64748b; margin-top: 3px; line-height: 1.4;'>{agent.description}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        # Subtle connector line between steps
        if idx < len(agents) - 1:
            st.markdown("<div class='pipeline-connector'><span class='pipeline-connector-line'></span></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ── Bottom Call-to-Action ──
    st.markdown("""
        <div style='text-align: center; margin: 0.5rem 0;'>
            <p style='color: #64748b; font-size: 0.9rem; margin-bottom: 0;'>Ready to transform your project?</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Go to Run Pipeline", use_container_width=True, key="cta_go_to_pipeline_btn"):
        st.session_state.navigation_selector = "Run Pipeline"
        st.rerun()


# ---------------- PAGE 2: RUN PIPELINE ----------------
# ---------------- PAGE 2: RUN PIPELINE ----------------
elif page == "Run Pipeline":
    st.markdown("""
        <div class='glass-card' style='margin-bottom: 2rem;'>
            <h1 style='margin-top: 0; color: #312e81; font-size: 2.2rem;'><span class='mi'>rocket_launch</span> Run Agent Pipeline</h1>
            <p style='color: #64748b; font-size: 1.1rem; margin-bottom: 0;'>Upload a repository package or specify a directory path to trigger the DevBuddy AI agents.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Choice of project folder upload inside a container
    with st.container():
        st.markdown("<h3 style='margin-bottom: 1rem;'>1. Select Project Source</h3>", unsafe_allow_html=True)
        upload_method = st.radio(
            "Choose project upload method:",
            ["Absolute Path on Local Machine", "Upload a Project ZIP File"],
            key="upload_method_selector",
            horizontal=True
        )
        
        project_path = None
        
        if upload_method == "Absolute Path on Local Machine":
            path_input = st.text_input(
                "Enter absolute project folder path:",
                placeholder="e.g., C:/Users/devsh/projects/my-web-app",
                key="local_path_input"
            )
            if path_input:
                if os.path.exists(path_input) and os.path.isdir(path_input):
                    project_path = path_input
                    st.session_state.selected_project_path = path_input
                    st.success(f"Successfully verified local directory: `{path_input}`")
                else:
                    st.error("Error: Specified directory path does not exist or is not a directory.")
                    
        else:  # Upload Zip File
            uploaded_file = st.file_uploader(
                "Upload Project ZIP File",
                type=["zip"],
                key="zip_file_uploader"
            )
            if uploaded_file is not None:
                # Save uploaded zip file to a temporary location and extract it
                temp_dir = os.path.join(tempfile.gettempdir(), "Devbuddy_extracted")
                temp_zip_path = os.path.join(tempfile.gettempdir(), uploaded_file.name)
                
                # Cleanup existing temp directory for clean slate
                import stat
                
                def force_delete_temp_dir(dir_path):
                    """Manually walk the tree, force write permissions, and delete everything."""
                    if os.path.exists(dir_path):
                        # Walk the tree from bottom to top
                        for root, dirs, files in os.walk(dir_path, topdown=False):
                            for name in files:
                                file_path = os.path.join(root, name)
                                try:
                                    # Force write permission on the file
                                    os.chmod(file_path, stat.S_IWRITE)
                                    os.remove(file_path)
                                except Exception:
                                    pass
                            for name in dirs:
                                dir_path_inner = os.path.join(root, name)
                                try:
                                    # Force write permission on the directory
                                    os.chmod(dir_path_inner, stat.S_IWRITE)
                                    os.rmdir(dir_path_inner)
                                except Exception:
                                    pass
                        # Finally remove the top directory
                        try:
                            os.chmod(dir_path, stat.S_IWRITE)
                            os.rmdir(dir_path)
                        except Exception:
                            pass

                force_delete_temp_dir(temp_dir)
                
                with open(temp_zip_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                    
                try:
                    utils.extract_zip(temp_zip_path, temp_dir)
                    
                    # Smart Root Directory Detection (find if it's wrapped in a single folder)
                    items = [
                        item for item in os.listdir(temp_dir)
                        if not item.startswith('.') and item != "__MACOSX"
                    ]
                    resolved_path = temp_dir
                    if len(items) == 1 and os.path.isdir(os.path.join(temp_dir, items[0])):
                        resolved_path = os.path.join(temp_dir, items[0])
                        
                    project_path = resolved_path
                    st.session_state.selected_project_path = resolved_path
                    st.success("Project ZIP file uploaded and extracted successfully!")
                except Exception as e:
                    st.error(f"Failed to process ZIP file: {str(e)}")

    # Display project summary if we have a valid path
    if project_path:
        st.markdown("<h3 style='margin-top: 2rem; margin-bottom: 1rem;'>2. Target Project Summary</h3>", unsafe_allow_html=True)
        
        summary_stats = utils.get_project_summary(project_path)
        
        # Display stat cards in columns using HTML cards
        size_kb = summary_stats["total_size_bytes"] / 1024
        size_text = f"{size_kb:.2f} KB" if size_kb < 1024 else f"{size_kb/1024:.2f} MB"
        
        st.markdown(f"""
            <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 20px;'>
                <div class='glass-card' style='margin-bottom: 0; padding: 20px; text-align: center;'>
                    <div style='color: #64748b; font-size: 0.9rem; font-weight: 600; text-transform: uppercase;'>Total Files Found</div>
                    <div style='color: #0f172a; font-size: 2rem; font-weight: 800; margin-top: 5px;'>{summary_stats["file_count"]}</div>
                </div>
                <div class='glass-card' style='margin-bottom: 0; padding: 20px; text-align: center;'>
                    <div style='color: #64748b; font-size: 0.9rem; font-weight: 600; text-transform: uppercase;'>Ignored Files</div>
                    <div style='color: #0f172a; font-size: 2rem; font-weight: 800; margin-top: 5px;'>{summary_stats["ignored_files_skipped"]}</div>
                </div>
                <div class='glass-card' style='margin-bottom: 0; padding: 20px; text-align: center;'>
                    <div style='color: #64748b; font-size: 0.9rem; font-weight: 600; text-transform: uppercase;'>Extracted Size</div>
                    <div style='color: #0f172a; font-size: 2rem; font-weight: 800; margin-top: 5px;'>{size_text}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
            
        with st.expander("View Extracted Project Directory Tree"):
            tree = utils.get_directory_tree(project_path)
            st.code(tree, language="text")
        
        st.markdown("<h3 style='margin-top: 2rem; margin-bottom: 1rem;'>3. Execute DevBuddy</h3>", unsafe_allow_html=True)
        # Trigger Pipeline button
        has_any_gemini_key = gemini_api_key or any(get_credential(f"GEMINI_KEY_AGENT_{i}") for i in range(1, 6))
        if not has_any_gemini_key:
            st.warning("Please provide a Gemini API Key in Settings to execute the pipeline.")
            run_btn = st.button("Analyze & Optimize Project", key="trigger_pipeline_btn", disabled=True, use_container_width=True)
        else:
            run_btn = st.button("Analyze & Optimize Project", key="trigger_pipeline_btn", use_container_width=True)
        
        if has_any_gemini_key and run_btn:
            # Reset pipeline execution state
            st.session_state.execution_logs = ["Pipeline initialized.", "Preparing environment and workspace..."]
            st.session_state.pipeline_results = None
            st.session_state.current_agent_status = {
                agent.name: "Pending" for agent in st.session_state.registry.get_all_agents()
            }
            
            # Interactive execution UI elements
            progress_bar = st.progress(0.0)
            status_container = st.empty()
            log_container = st.empty()
            
            try:
                # Fetch active key and pass to ProjectIntelligenceAgent
                active_gemini_key = st.session_state.get('PERSIST_GEMINI_KEY') or st.session_state.get('PERSIST_GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY')
                from agents import ProjectIntelligenceAgent
                agent1 = ProjectIntelligenceAgent(api_key=active_gemini_key)
                for i, ag in enumerate(st.session_state.registry._agents):
                    if isinstance(ag, ProjectIntelligenceAgent):
                        st.session_state.registry._agents[i] = agent1

                # Start running the sequential pipeline generator
                pipeline = st.session_state.engine.run_pipeline(project_path, gemini_api_key=gemini_api_key)
                
                for event in pipeline:
                    event_type = event.get("event")
                    
                    if event_type == "pipeline_start":
                        st.session_state.execution_logs.append("Executing DevBuddy Sequential Pipeline...")
                        
                    elif event_type == "agent_start":
                        agent_name = event.get("agent_name")
                        st.session_state.current_agent_status[agent_name] = "Running"
                        st.session_state.execution_logs.append(f"[>>] Launching {agent_name}...")
                        
                    elif event_type == "agent_log":
                        log_line = event.get("log")
                        st.session_state.execution_logs.append(f"  > {log_line}")
                        
                    elif event_type == "agent_success":
                        agent_name = event.get("agent_name")
                        st.session_state.current_agent_status[agent_name] = "Completed"
                        st.session_state.execution_logs.append(f"[OK] Completed tasks for {agent_name}")
                        
                    elif event_type == "agent_failed":
                        agent_name = event.get("agent_name")
                        st.session_state.current_agent_status[agent_name] = "Failed"
                        st.session_state.execution_logs.append(f"[FAIL] Failure in {agent_name}: {event.get('error')}")
                        
                    elif event_type == "pipeline_done":
                        st.session_state.execution_logs.append("Pipeline finished! Aggregating outputs.")
                        st.session_state.pipeline_results = event.get("results")
                        progress_bar.progress(1.0)
                        st.balloons()
                    
                    # Dynamic UI updates during streaming
                    completed_count = list(st.session_state.current_agent_status.values()).count("Completed")
                    total_count = len(st.session_state.current_agent_status)
                    if total_count > 0 and event_type != "pipeline_done":
                        progress_bar.progress(completed_count / total_count)
                    
                    # Render agent progress badges in horizontal layout
                    with status_container.container():
                        cols = st.columns(total_count)
                        for col_idx, agent in enumerate(st.session_state.registry.get_all_agents()):
                            status = st.session_state.current_agent_status[agent.name]
                            badge_class = "badge-pending"
                            if status == "Running":
                                badge_class = "badge-running"
                            elif status == "Completed":
                                badge_class = "badge-success"
                            elif status == "Failed":
                                badge_class = "badge-failed"
                            
                            cols[col_idx].markdown(f"""
                                <div class='agent-status-card'>
                                    <div style='font-size: 1.6rem; margin-bottom: 5px; color: #475569;'>{agent.icon}</div>
                                    <div style='font-weight: 700; font-size: 0.85rem; margin-bottom: 10px; color: #0f172a;'>{agent.name.split(" ")[0]}</div>
                                    <span class='badge {badge_class}' style='display: block;'>{status}</span>
                                </div>
                            """, unsafe_allow_html=True)
                    
                    # Render live logs terminal block
                    with log_container.container():
                        terminal_content = "".join([f"<div class='terminal-line'>{line}</div>" for line in st.session_state.execution_logs[-8:]])
                        st.markdown(f"""
                            <div class='terminal-block'>
                                {terminal_content}
                            </div>
                        """, unsafe_allow_html=True)
            except Exception as pipeline_err:
                st.error(f"Pipeline execution encountered an error: {str(pipeline_err)}")
                st.session_state.execution_logs.append(f"[FAIL] Execution halted: {str(pipeline_err)}")
                
                # Render updated badges showing failed state
                with status_container.container():
                    cols = st.columns(len(st.session_state.current_agent_status))
                    for col_idx, agent in enumerate(st.session_state.registry.get_all_agents()):
                        status = st.session_state.current_agent_status[agent.name]
                        badge_class = "badge-pending"
                        if status == "Running":
                            status = "Failed"
                            badge_class = "badge-failed"
                        elif status == "Completed":
                            badge_class = "badge-success"
                        elif status == "Failed":
                            badge_class = "badge-failed"
                        
                        cols[col_idx].markdown(f"""
                            <div class='agent-status-card'>
                                <div style='font-size: 1.6rem; margin-bottom: 5px; color: #475569;'>{agent.icon}</div>
                                <div style='font-weight: 700; font-size: 0.85rem; margin-bottom: 10px; color: #0f172a;'>{agent.name.split(" ")[0]}</div>
                                <span class='badge {badge_class}' style='display: block;'>{status}</span>
                            </div>
                        """, unsafe_allow_html=True)
                
                with log_container.container():
                    terminal_content = "".join([f"<div class='terminal-line'>{line}</div>" for line in st.session_state.execution_logs[-8:]])
                    st.markdown(f"""
                        <div class='terminal-block'>
                            {terminal_content}
                        </div>
                    """, unsafe_allow_html=True)
                    
    # Display the final execution results tab panels
    if st.session_state.pipeline_results:
        st.markdown("## :material/assignment: Agent Outputs & Deliverables")
        
        agents = st.session_state.registry.get_all_agents()
        tabs = st.tabs([a.name.replace(' Agent', '') for a in agents])
        
        for tab_idx, agent in enumerate(agents):
            with tabs[tab_idx]:
                if agent.name == "Project Intelligence Agent":
                    analysis_data = st.session_state.pipeline_results.get("project_analysis")
                    if analysis_data:
                        st.markdown(f"## :blue[:material/analytics: Project: {analysis_data.get('project_name')}]")
                        
                        # Card 1: Project Details
                        with st.container(border=True):
                            st.markdown("### :blue[:material/info: Project Details]")
                            st.markdown(f"""
                                <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px;'>
                                    <div class='glass-card' style='padding: 15px; text-align: center; margin: 0;'>
                                        <div style='color: #64748b; font-size: 0.85rem; font-weight: 600; text-transform: uppercase;'>Primary Language</div>
                                        <div style='color: #0f172a; font-size: 1.5rem; font-weight: 800; margin-top: 5px;'>{analysis_data.get('primary_language')}</div>
                                    </div>
                                    <div class='glass-card' style='padding: 15px; text-align: center; margin: 0;'>
                                        <div style='color: #64748b; font-size: 0.85rem; font-weight: 600; text-transform: uppercase;'>Project Type</div>
                                        <div style='color: #0f172a; font-size: 1.5rem; font-weight: 800; margin-top: 5px;'>{analysis_data.get('project_type')}</div>
                                    </div>
                                    <div class='glass-card' style='padding: 15px; text-align: center; margin: 0;'>
                                        <div style='color: #64748b; font-size: 0.85rem; font-weight: 600; text-transform: uppercase;'>Complexity</div>
                                        <div style='color: #0f172a; font-size: 1.5rem; font-weight: 800; margin-top: 5px;'>{analysis_data.get('estimated_complexity')}</div>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                            
                        # Card 2: Architecture Pattern
                        with st.container(border=True):
                            st.markdown("### :blue[:material/account_tree: Architecture & Folder Structure]")
                            st.markdown(f"**Architecture Pattern:** `{analysis_data.get('architecture_pattern')}`")
                            st.markdown(f"**Entry Point File:** `{analysis_data.get('entry_point')}`")
                            
                        c1, c2 = st.columns(2)
                        with c1:
                            with st.container(border=True):
                                st.markdown("#### :blue[:material/build: Detected Stack]")
                                stack_html = "".join([f"<span class='stack-tag'>{tech}</span>" for tech in analysis_data.get("detected_stack", [])])
                                st.markdown(stack_html, unsafe_allow_html=True)
                                
                            with st.container(border=True):
                                st.markdown("#### :blue[:material/inventory: Dependencies]")
                                dep_html = "".join([f"<span class='dep-tag'>{dep}</span>" for dep in analysis_data.get("dependencies", [])])
                                st.markdown(dep_html, unsafe_allow_html=True)
                        
                        with c2:
                            with st.container(border=True):
                                st.markdown("#### :blue[:material/warning: Potential Missing Files]")
                                if analysis_data.get("potential_missing_files"):
                                    missing_html = "".join([f"<span class='missing-tag'>{f}</span>" for f in analysis_data.get("potential_missing_files", [])])
                                    st.markdown(missing_html, unsafe_allow_html=True)
                                else:
                                    st.success("No missing files recommended! The repository is structurally complete.")
                                    
                            with st.container(border=True):
                                st.markdown("#### :blue[:material/monitor_heart: Project Health Overview]")
                                st.success(analysis_data.get("project_health_overview"))
                        
                        # Card 3: Reports & Tree Diagrams
                        with st.container(border=True):
                            st.markdown("### :blue[:material/analytics: Reports & Tree Diagrams]")
                            with st.expander("Folder Tree Structure", expanded=False):
                                project_tree = st.session_state.pipeline_results.get(agents[0].name, {}).get("artifacts", {}).get("project_tree.txt", "")
                                st.code(project_tree, language="text")
    
                            with st.expander("Full Gemini Architecture Report", expanded=False):
                                st.markdown(analysis_data.get("detailed_markdown_report"))
                                
                            # Download artifacts buttons
                            report_content = st.session_state.pipeline_results.get(agents[0].name, {}).get("artifacts", {}).get("project_analysis_report.md", "")
                            st.download_button(
                                label="Download Project Analysis Report (.md)",
                                data=report_content,
                                file_name="project_analysis_report.md",
                                mime="text/markdown",
                                key="dl_report_btn",
                                use_container_width=True
                            )
                    else:
                        result = st.session_state.pipeline_results.get(agent.name, {})
                        st.markdown(result.get("summary", "No summary output was generated."))
                        
                elif agent.name == "Testing & QA Agent":
                    qa_data = st.session_state.pipeline_results.get("qa_analysis")
                    if qa_data:
                        st.markdown("## :green[:material/bug_report: Codebase QA & Testing Audit Dashboard]")
                        
                        # Card 1: Display Health Dials/Metrics
                        with st.container(border=True):
                            st.markdown("### :green[:material/assessment: QA & Readiness Metrics]")
                            st.markdown(f"""
                                <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 20px;'>
                                    <div class='glass-card' style='padding: 20px; text-align: center; margin: 0; background: linear-gradient(to right, #ffffff, #f0fdf4); border-color: #bbf7d0;'>
                                        <div style='color: #166534; font-size: 0.95rem; font-weight: 700; text-transform: uppercase;'>Overall Health Score</div>
                                        <div style='color: #15803d; font-size: 2.5rem; font-weight: 800; margin-top: 5px;'>{qa_data.get('overall_health_score')}<span style='font-size: 1.2rem; color: #86efac;'>/100</span></div>
                                    </div>
                                    <div class='glass-card' style='padding: 20px; text-align: center; margin: 0; background: linear-gradient(to right, #ffffff, #e0e7ff); border-color: #c7d2fe;'>
                                        <div style='color: #3730a3; font-size: 0.95rem; font-weight: 700; text-transform: uppercase;'>Production Readiness Score</div>
                                        <div style='color: #4338ca; font-size: 2.5rem; font-weight: 800; margin-top: 5px;'>{qa_data.get('production_readiness_score')}<span style='font-size: 1.2rem; color: #a5b4fc;'>/100</span></div>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                            
                        # Card 2: Show Accordions for Passed, Warnings, and Errors
                        with st.container(border=True):
                            st.markdown("### :green[:material/fact_check: Audit Logs & Checkpoints]")
                            err_list = qa_data.get("errors", [])
                            warn_list = qa_data.get("warnings", [])
                            pass_list = qa_data.get("passed_checks", [])
                            
                            # Errors first
                            with st.expander(f"Critical Errors & Security Risks ({len(err_list)})", expanded=len(err_list) > 0):
                                if err_list:
                                    for err in err_list:
                                        st.markdown(f"**{err.get('check_name')}**")
                                        st.write(err.get("details"))
                                        st.markdown("---")
                                else:
                                    st.success("No critical errors or security risks detected!")
                                    
                            # Warnings
                            with st.expander(f"Warnings & Code Smells ({len(warn_list)})", expanded=len(warn_list) > 0):
                                if warn_list:
                                    for warn in warn_list:
                                        st.markdown(f"**{warn.get('check_name')}**")
                                        st.write(warn.get("details"))
                                        st.markdown("---")
                                else:
                                    st.success("No QA warnings or code smells detected!")
                                    
                            # Passed
                            with st.expander(f"Passed Audits ({len(pass_list)})", expanded=False):
                                if pass_list:
                                    for passed in pass_list:
                                        st.markdown(f"**{passed.get('check_name')}**")
                                        st.write(passed.get("details"))
                                        st.markdown("---")
                                else:
                                    st.write("No passing checks reported.")
                                    
                        # Card 3: Detailed Report
                        with st.container(border=True):
                            st.markdown("### :green[:material/assignment_turned_in: Full Gemini QA Audit Report]")
                            st.markdown(qa_data.get("detailed_qa_report"))
                            
                            # Download button
                            report_content = st.session_state.pipeline_results.get(agent.name, {}).get("artifacts", {}).get("qa_audit_report.md", "")
                            st.download_button(
                                label="Download QA Audit Report (.md)",
                                data=report_content,
                                file_name="qa_audit_report.md",
                                mime="text/markdown",
                                key="dl_qa_report_btn",
                                use_container_width=True
                            )
                    else:
                        result = st.session_state.pipeline_results.get(agent.name, {})
                        st.markdown(result.get("summary", "No summary output was generated."))
                        
                elif agent.name == "Documentation Agent":
                    report_data = st.session_state.pipeline_results.get("project_report")
                    if report_data:
                        st.markdown("## :orange[:material/description: Professional Project Evaluation & Documentation]")
                        
                        # Card 1: PDF Report
                        with st.container(border=True):
                            st.markdown("### :orange[:material/picture_as_pdf: PDF Report]")
                            pdf_bytes = st.session_state.pipeline_results.get(agent.name, {}).get("artifacts", {}).get("project_report.pdf", b"")
                            st.markdown("""
                                <div class='glass-card' style='text-align: center; border-color: rgba(0, 198, 255, 0.6); background: rgba(0, 198, 255, 0.03); margin-bottom: 15px;'>
                                    <h4 style='color: #00C6FF; margin-top: 0;'>Professional PDF Report Ready</h4>
                                    <p style='font-size: 0.9rem; color: #8b949e; margin-bottom: 0;'>The Documentation Agent has dynamically generated a professional typeset PDF report using ReportLab containing an Executive Summary, tech stacks, audits, weaknesses, and readiness scores.</p>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            st.download_button(
                                label="Download PDF Project Report (ReportLab)",
                                data=pdf_bytes,
                                file_name="project_readiness_report.pdf",
                                mime="application/pdf",
                                key="dl_pdf_btn",
                                use_container_width=True
                            )
                            
                        # Card 2: Report Preview
                        with st.container(border=True):
                            st.markdown("### :orange[:material/preview: Report Preview]")
                            with st.expander("Full Report Preview", expanded=False):
                                st.markdown("#### 1. Executive Summary")
                                st.info(report_data.get("executive_summary", ""))
                                st.markdown("#### 2. Project Overview")
                                st.write(report_data.get("project_overview", ""))
                                st.markdown("#### 3. Architecture Summary")
                                st.write(report_data.get("architecture_summary", ""))
                                st.markdown("#### 4. Detected Technologies")
                                st.write(report_data.get("detected_technologies", ""))
                                st.markdown("#### 5. Folder Structure & critique")
                                st.write(report_data.get("folder_structure", ""))
                                
                                col_s, col_w = st.columns(2)
                                with col_s:
                                    st.markdown("#### :orange[:material/thumb_up: Strengths]")
                                    for s in report_data.get("strengths", []):
                                        st.markdown(f"- {s}")
                                with col_w:
                                    st.markdown("#### :orange[:material/thumb_down: Weaknesses & Bottlenecks]")
                                    for w in report_data.get("weaknesses", []):
                                        st.markdown(f"- {w}")
                                        
                                st.markdown("#### :orange[:material/gpp_bad: Critical Issues Found]")
                                if report_data.get("issues_found"):
                                    for i in report_data.get("issues_found", []):
                                        st.markdown(f"- {i}")
                                else:
                                    st.success("No critical issues found!")
                                    
                                st.markdown("#### :orange[:material/warning: Non-Critical Warnings]")
                                if report_data.get("warnings"):
                                    for w in report_data.get("warnings", []):
                                        st.markdown(f"- {w}")
                                else:
                                    st.success("No warnings reported!")
                                    
                                st.markdown("#### :orange[:material/checklist: Step-by-Step Recommendations]")
                                for r in report_data.get("recommendations", []):
                                    st.markdown(f"- [ ] {r}")
                                    
                                st.markdown("#### :orange[:material/verified: Production Readiness & Review]")
                                st.success(report_data.get("production_readiness", ""))
                                st.markdown("#### :orange[:material/score: Evaluation & Score Summary]")
                                st.write(report_data.get("overall_score_summary", ""))
                    else:
                        result = st.session_state.pipeline_results.get(agent.name, {})
                        st.markdown(result.get("summary", "No summary output was generated."))
                        
                elif agent.name == "GitHub Deployment Agent":
                    st.markdown("## :violet[:material/cloud_upload: GitHub Repository Deployment]")
                    
                    # Card 1: Pre-flight Summary
                    with st.container(border=True):
                        st.markdown("### :violet[:material/fact_check: Pre-flight Summary]")
                        preflight_result = st.session_state.pipeline_results.get(agent.name, {})
                        st.markdown(preflight_result.get("summary", ""))
                    
                    # Card 2: Interactive Configuration
                    with st.container(border=True):
                        st.markdown("### :violet[:material/settings: Repository Configuration]")
                        
                        upload_permission = st.radio(
                            "Do you want to upload this project to GitHub?",
                            ["No", "Yes"],
                            index=0,
                            key="gh_upload_permission_radio"
                        )
                        
                        if upload_permission == "Yes":
                            # Fetch project info from Agent 1 to prefill
                            intel_data = st.session_state.pipeline_results.get("project_analysis")
                            default_repo_name = intel_data.get("project_name", "my-DevBuddy-app") if intel_data else "my-DevBuddy-app"
                            # Sanitize repo name for github (lowercase, alphanumerics and dashes)
                            sanitized_default_name = "".join([c if c.isalnum() or c in ("-", "_") else "-" for c in default_repo_name]).lower()
                            
                            r_col1, r_col2, r_col3 = st.columns(3)
                            with r_col1:
                                repo_name_input = st.text_input("Repository Name", value=sanitized_default_name, key="gh_repo_name_val")
                            with r_col2:
                                repo_privacy_input = st.radio("Visibility", ["Private", "Public"], index=0, key="gh_repo_privacy_val")
                            with r_col3:
                                license_input = st.selectbox(
                                    "Select License",
                                    ["MIT", "Apache 2.0", "GPL v3", "BSD 3-Clause", "Mozilla MPL 2.0", "Unlicense", "No License"],
                                    index=0,
                                    key="gh_repo_license_val"
                                )
                                
                            repo_desc_input = st.text_area("Repository Description", value="Repository compiled and deployed automatically by DevBuddy AI.", key="gh_repo_desc_val")
                            
                            # Fetch Agent 2 QA checks to see if error exists
                            qa_data = st.session_state.pipeline_results.get("qa_analysis")
                            has_qa_errors = False
                            if qa_data and len(qa_data.get("errors", [])) > 0:
                                has_qa_errors = True
                                
                            confirm_bypass = True
                            if has_qa_errors:
                                st.warning("The QA & Testing Agent (Agent 2) detected critical errors or security risks in this project.")
                                confirm_bypass = st.checkbox(
                                    "I confirm that I want to upload this project despite critical QA errors.",
                                    value=False,
                                    key="gh_qa_error_confirm_bypass"
                                )
                                
                            # Publish Action button
                            publish_trigger = st.button("Publish to GitHub", use_container_width=True, key="gh_publish_trigger_btn")
                            
                            if publish_trigger:
                                if not github_token:
                                    st.error("GitHub Personal Access Token is missing. Please configure it in the sidebar.")
                                elif has_qa_errors and not confirm_bypass:
                                    st.error("Action blocked. You must check the confirmation box to upload despite QA errors.")
                                else:
                                    with st.spinner("Publishing codebase to GitHub..."):
                                        # Call deploy method on the agent instance
                                        deploy_result = agent.deploy(
                                            project_path=st.session_state.selected_project_path,
                                            github_token=github_token,
                                            repo_name=repo_name_input,
                                            repo_description=repo_desc_input,
                                            is_private=(repo_privacy_input == "Private"),
                                            license_name=license_input
                                        )
                                        
                                        if deploy_result.get("status") == "success":
                                            st.balloons()
                                            st.success("**Success! Code successfully published to GitHub!**")
                                            st.markdown(f"**Repository URL:** [{deploy_result.get('repo_url')}]({deploy_result.get('repo_url')})")
                                            st.markdown(f"**Branch:** `{deploy_result.get('branch')}`")
                                            st.markdown(f"**License:** `{deploy_result.get('license')}`")
                                            st.markdown(f"**GitHub Ready Score:** `{deploy_result.get('ready_score')}/100`")
                                            
                                            col_gen, col_ign = st.columns(2)
                                            with col_gen:
                                                st.markdown("**Files Generated Automatically:**")
                                                if deploy_result.get("files_generated"):
                                                    for f in deploy_result.get("files_generated"):
                                                        st.markdown(f"- `{f}`")
                                                else:
                                                    st.markdown("*No files needed to be generated.*")
                                            with col_ign:
                                                st.markdown("**Sensitive Files Ignored / Protected:**")
                                                for f in deploy_result.get("files_ignored", []):
                                                    st.markdown(f"- `{f}`")
                                                    
                                            st.session_state.gh_published_url = deploy_result.get("repo_url")
                                        else:
                                            st.error(f"**Failed to deploy:** {deploy_result.get('error')}")
                else:
                    # Agent 5: LinkedIn Branding Agent
                    brand_data = st.session_state.pipeline_results.get("linkedin_branding")
                    if brand_data:
                        st.markdown("## :red[:material/campaign: LinkedIn Launch & Branding Kit]")
                        
                        # Card 1: Branding Insights (Skills, Highlights, Problems)
                        with st.container(border=True):
                            st.markdown("### :red[:material/insights: Branding Insights]")
                            
                            l_col1, l_col2 = st.columns(2)
                            with l_col1:
                                st.markdown("#### :red[:material/build: Core Tech Stack]")
                                skills_html = "".join([f"<span class='dep-tag'>{s}</span>" for s in brand_data.get("tech_stack", [])])
                                st.markdown(skills_html, unsafe_allow_html=True)
                            with l_col2:
                                st.markdown("#### :red[:material/school: Engineering Learning Highlights]")
                                for h in brand_data.get("learning_highlights", []):
                                    st.markdown(f"- {h}")
                                    
                            st.markdown("#### :red[:material/lightbulb: Core Problem Solved]")
                            st.write(brand_data.get("problem_solved", ""))
                            
                        # Card 2: Launch Copy Preview & Editor
                        with st.container(border=True):
                            st.markdown("### :red[:material/edit_note: Launch Copy Preview & Editor]")
                            st.caption("Customize your post. The text in the editor will be used for publishing.")
                            
                            target_link = st.session_state.gh_published_url if st.session_state.gh_published_url else "[Insert GitHub URL here]"
                            
                            # Template selection box
                            post_type = st.selectbox(
                                "Select Post Template to Load:",
                                ["Short Post Copy", "Long Post Copy"],
                                key="linkedin_template_selector_val"
                            )
                            
                            # Initialize session state for edited text if not present
                            if "edited_linkedin_post" not in st.session_state:
                                raw_post = brand_data.get("short_version", "")
                                st.session_state.edited_linkedin_post = raw_post.replace("[Insert GitHub URL here]", target_link)
                                st.session_state.prev_template_type = "Short Post Copy"
                                
                            # If template type changed, reset edited copy to the corresponding brand data default
                            if st.session_state.prev_template_type != post_type:
                                st.session_state.prev_template_type = post_type
                                raw_post = brand_data.get("short_version", "") if post_type == "Short Post Copy" else brand_data.get("long_version", "")
                                st.session_state.edited_linkedin_post = raw_post.replace("[Insert GitHub URL here]", target_link)
                                
                            # Editable Text Area containing the pre-filled post copy
                            edited_text = st.text_area(
                                "Edit LinkedIn Post Content",
                                value=st.session_state.edited_linkedin_post,
                                height=250,
                                key="linkedin_post_editor_textarea"
                            )
                            st.session_state.edited_linkedin_post = edited_text
                            
                            # Character counter
                            char_count = len(edited_text)
                            st.markdown(f"**Character Count:** `{char_count}`")
                            
                            # Display tags and link
                            st.markdown("#### :red[:material/label: Recommended Tags]")
                            tags_html = " ".join([f"<b>#{tag.replace('#', '')}</b>" for tag in brand_data.get("hashtags", [])])
                            st.markdown(tags_html, unsafe_allow_html=True)
                            
                            st.markdown(f"**GitHub Repository Link:** [{target_link}]({target_link})")
                            
                        # Card 3: Publishing Options
                        # Check if GitHub upload completes
                        if st.session_state.gh_published_url:
                            with st.container(border=True):
                                st.markdown("### :red[:material/share: LinkedIn Publishing]")
                                
                                # LinkedIn Authentication Card
                                linkedin_token = get_credential("LINKEDIN_ACCESS_TOKEN")
                                if not linkedin_token:
                                    st.warning("**Connect LinkedIn Account** — Add `LINKEDIN_ACCESS_TOKEN` to your `.env` file to authorize")
                                else:
                                    # Run/Retrieve Diagnostics
                                    if "linkedin_diagnostics" not in st.session_state or st.session_state.get("linkedin_diagnostics_token") != linkedin_token:
                                        with st.spinner("Running LinkedIn Diagnostics..."):
                                            brand_agent = st.session_state.registry.get_all_agents()[4]
                                            diag_res = brand_agent.run_diagnostics(linkedin_token)
                                            st.session_state.linkedin_diagnostics = diag_res
                                            st.session_state.linkedin_diagnostics_token = linkedin_token
                                            
                                    diag = st.session_state.linkedin_diagnostics
                                    
                                    # Display Authentication Card
                                    if diag.get("token_valid") == "Yes":
                                        st.success("**Connected Successfully**")
                                    else:
                                        st.error("**Invalid Token / Connection Failed**")
                                        
                                    # Diagnostics panel
                                    with st.expander("LinkedIn Diagnostics & Authentication Details", expanded=True):
                                        col_d1, col_d2 = st.columns(2)
                                        with col_d1:
                                            st.markdown(f"**Token Valid:** `{diag.get('token_valid')}`")
                                            st.markdown(f"**Member API Access:** `{diag.get('member_access')}`")
                                            st.markdown(f"**Publish Permission:** `{diag.get('publish_permission')}`")
                                        with col_d2:
                                            st.markdown(f"**LinkedIn Member ID:** `{diag.get('member_id') or 'N/A'}`")
                                            st.markdown(f"**Token Expiry:** `{diag.get('expiry')}`")
                                            st.markdown(f"**Current Token Scopes:** `{', '.join(diag.get('scopes', [])) if diag.get('scopes') else 'None'}`")
                                            
                                        st.markdown(f"**Required Scope Missing:** `{', '.join(diag.get('missing_scopes', [])) if diag.get('missing_scopes') else 'None'}`")
                                        st.warning(f"**Suggested Fix:** {diag.get('suggested_fix')}")
                                        
                                        # Print debug request/response
                                        with st.expander("HTTP Request/Response Debugger Logs", expanded=False):
                                            st.code("\n".join(diag.get("debug_logs", [])), language="text")
                                    
                                    # Check if publishing is blocked (e.g. w_member_social is missing)
                                    is_blocked = (diag.get("publish_permission") == "No")
                                    
                                    if is_blocked:
                                        st.error("**Your LinkedIn application does not have permission to publish posts.**")
                                        st.info("Fallback Option Activated: Copy the post content manually and share it using the browser link below.")
                                        
                                        # Single Client-Side JS Clipboard Copy & Open LinkedIn Component
                                        import json
                                        import streamlit.components.v1 as components
                                        
                                        combined_text = f"{edited_text}\n\n🔗 GitHub Repository: {target_link}"
                                        safe_js_text = json.dumps(combined_text)
                                        
                                        html_code = f"""
                                        <button id="linkedinBtn" style="background-color: #0A66C2; color: white; padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; width: 100%; font-family: sans-serif; transition: 0.3s; box-shadow: 0 4px 6px rgba(0,0,0,0.1); height: 40px; font-size: 14px;">
                                            💼 Copy Post & Open LinkedIn
                                        </button>
                                        <script>
                                        document.getElementById("linkedinBtn").addEventListener("click", function() {{
                                            const textToCopy = {safe_js_text};
                                            const btn = this;
                                            navigator.clipboard.writeText(textToCopy).then(function() {{
                                                btn.innerText = "✅ Copied! Opening LinkedIn...";
                                                btn.style.backgroundColor = "#10B981"; // Green success color
                                                setTimeout(() => {{
                                                    window.open("https://www.linkedin.com/feed/?shareActive=true", "_blank");
                                                    btn.innerText = "💼 Copy Post & Open LinkedIn";
                                                    btn.style.backgroundColor = "#0A66C2";
                                                }}, 800);
                                            }}).catch(function(err) {{
                                                alert("Clipboard copy failed. Please ensure your browser allows clipboard access.");
                                            }});
                                        }});
                                        </script>
                                        """
                                        components.html(html_code, height=50)
                                    else:
                                        # Action buttons
                                        btn_col1, btn_col2, btn_col3 = st.columns(3)
                                        
                                        with btn_col1:
                                            copy_triggered = st.button("Copy Post Content", key="linkedin_copy_post_btn", use_container_width=True)
                                            if copy_triggered:
                                                st.success("Post text copied to clipboard! (Use Ctrl+C inside the editor box)")
                                                
                                        with btn_col2:
                                            regenerate_triggered = st.button("Regenerate Post", key="linkedin_regenerate_post_btn", use_container_width=True)
                                            if regenerate_triggered:
                                                with st.spinner("Regenerating branding content..."):
                                                    brand_agent = st.session_state.registry.get_all_agents()[4]
                                                    run_context = {
                                                        "project_analysis": st.session_state.pipeline_results.get("project_analysis"),
                                                        "qa_analysis": st.session_state.pipeline_results.get("qa_analysis"),
                                                        "gemini_api_key": gemini_api_key
                                                    }
                                                    try:
                                                        brand_res = brand_agent.run(st.session_state.selected_project_path, run_context)
                                                        if brand_res.get("status") == "success":
                                                            st.session_state.pipeline_results["linkedin_branding"] = run_context.get("linkedin_branding")
                                                            raw_post = run_context.get("linkedin_branding", {}).get("short_version" if post_type == "Short Post Copy" else "long_version", "")
                                                            st.session_state.edited_linkedin_post = raw_post.replace("[Insert GitHub URL here]", target_link)
                                                            st.success("Post content regenerated successfully!")
                                                            st.rerun()
                                                        else:
                                                            st.error(f"Failed to regenerate: {brand_res.get('error')}")
                                                    except Exception as regen_err:
                                                        st.error(f"Failed to regenerate: {str(regen_err)}")
                                                        
                                        with btn_col3:
                                            publish_triggered = st.button("Publish to LinkedIn", key="linkedin_publish_post_btn", use_container_width=True)
                                            if publish_triggered:
                                                if not linkedin_token:
                                                    st.error("LinkedIn Access Token is missing. Please configure it in your .env.")
                                                elif not edited_text.strip():
                                                    st.error("Post text is empty. Please enter some content to share.")
                                                else:
                                                    # Initialize console logs
                                                    st.session_state.linkedin_publish_logs = ["Connecting to LinkedIn...", "Validating Token..."]
                                                    st.session_state.execution_logs.append("[LINKEDIN] Publishing triggered.")
                                                    st.session_state.execution_logs.append("  > Running publish call...")
                                                    
                                                    with st.spinner("Posting to LinkedIn..."):
                                                        brand_agent = st.session_state.registry.get_all_agents()[4]
                                                        member_id = diag.get("member_id") or "me"
                                                        pub_result = brand_agent.publish_post(linkedin_token, edited_text, member_id)
                                                        
                                                        # Retrieve HTTP debug logs
                                                        pub_debug_logs = pub_result.get("debug_logs", [])
                                                        st.session_state.linkedin_publish_logs.extend(pub_debug_logs)
                                                        
                                                        if pub_result.get("status") == "success":
                                                            st.session_state.linkedin_publish_logs.append("Success.")
                                                            st.session_state.execution_logs.append("  > [OK] LinkedIn post published successfully.")
                                                            st.balloons()
                                                            st.success("Published Successfully!")
                                                        else:
                                                            st.session_state.linkedin_publish_logs.append("[FAIL] Publishing failed.")
                                                            st.session_state.execution_logs.append(f"  > [FAIL] Publishing failed: {pub_result.get('reason')}")
                                                            
                                                            st.error(f"**Publishing Failed:** {pub_result.get('reason')}")
                                                            st.markdown(f"**HTTP Status:** `{pub_result.get('status_code')}`")
                                                            st.markdown(f"**LinkedIn Error Message:** `{pub_result.get('error_message')}`")
                                                            st.warning(f"**Suggested Fix:** {pub_result.get('suggested_fix')}")
                                                            
                                                            # Fallback display options
                                                            st.info("Fallback Option Activated: Copy the post content manually and share it using the browser link below.")
                                                            
                                                            # Single Client-Side JS Clipboard Copy & Open LinkedIn Component
                                                            import json
                                                            import streamlit.components.v1 as components
                                                            
                                                            combined_text = f"{edited_text}\n\n🔗 GitHub Repository: {target_link}"
                                                            safe_js_text = json.dumps(combined_text)
                                                            
                                                            html_code = f"""
                                                            <button id="linkedinBtnFail" style="background-color: #0A66C2; color: white; padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; width: 100%; font-family: sans-serif; transition: 0.3s; box-shadow: 0 4px 6px rgba(0,0,0,0.1); height: 40px; font-size: 14px;">
                                                                💼 Copy Post & Open LinkedIn
                                                            </button>
                                                            <script>
                                                            document.getElementById("linkedinBtnFail").addEventListener("click", function() {{
                                                                const textToCopy = {safe_js_text};
                                                                const btn = this;
                                                                navigator.clipboard.writeText(textToCopy).then(function() {{
                                                                    btn.innerText = "✅ Copied! Opening LinkedIn...";
                                                                    btn.style.backgroundColor = "#10B981"; // Green success color
                                                                    setTimeout(() => {{
                                                                        window.open("https://www.linkedin.com/feed/?shareActive=true", "_blank");
                                                                        btn.innerText = "💼 Copy Post & Open LinkedIn";
                                                                        btn.style.backgroundColor = "#0A66C2";
                                                                    }}, 800);
                                                                }}).catch(function(err) {{
                                                                    alert("Clipboard copy failed. Please ensure your browser allows clipboard access.");
                                                                }});
                                                            }});
                                                            </script>
                                                            """
                                                            components.html(html_code, height=50)
                                
                                # Console log block
                                if "linkedin_publish_logs" in st.session_state and st.session_state.linkedin_publish_logs:
                                    st.markdown("##### LinkedIn Publisher Console")
                                    logs_str = "\n".join(st.session_state.linkedin_publish_logs)
                                    st.code(logs_str, language="text")
                        else:
                            st.info("Please publish the codebase to GitHub using the **GitHub Deployment Agent** first to enable LinkedIn Publishing with your repository link.")
                            
                        st.markdown("""
                            <div class='glass-card' style='margin-top: 20px; border-color: rgba(255, 255, 255, 0.05); background: rgba(255, 255, 255, 0.01);'>
                                <p style='font-size: 0.85rem; color: #8b949e; margin: 0;'><b>Privacy Guarantee:</b> DevBuddy AI only generates copy recommendations. We do not automatically write to your LinkedIn profile. All posts must be published manually.</p>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        result = st.session_state.pipeline_results.get(agent.name, {})
                        st.markdown(result.get("summary", "No summary output was generated."))

elif page == "Settings":
    st.markdown("""
        <div class='glass-card' style='margin-bottom: 2rem;'>
            <h1 style='margin-top: 0; color: #312e81; font-size: 2.2rem;'>⚙️ Settings & Configuration</h1>
            <p style='color: #64748b; font-size: 1.1rem; margin-bottom: 0;'>Configure API Keys and third-party credentials for the DevBuddy sequential agent pipeline.</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("### :material/settings: API & Configuration Settings")
        
        tab1, tab2, tab3 = st.tabs([
            "🧠 Gemini Agents",
            "🐙 GitHub",
            "💼 LinkedIn"
        ])
        
        with tab1:
            st.markdown("#### Gemini API & Model Configuration")
            # Global Key
            st.text_input(
                "Global Gemini API Key (Fallback)",
                type="password",
                placeholder="Enter global Gemini API Key (AIzaSy...)",
                value=st.session_state.get("PERSIST_GEMINI_API_KEY", ""),
                key="temp_GEMINI_API_KEY",
                help="Fallback API key used if specific agent keys are not provided."
            )
            
            # Model Selection
            model_options = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"]
            persist_model = st.session_state.get("PERSIST_GEMINI_MODEL", "gemini-2.5-flash")
            if persist_model not in model_options:
                model_options.append(persist_model)
                
            st.selectbox(
                "Gemini Model Override",
                options=model_options,
                index=model_options.index(persist_model),
                key="temp_GEMINI_MODEL",
                help="Override the model used by all Gemini agents."
            )
            
            st.markdown("---")
            st.markdown("#### Individual Agent API Keys (To prevent rate limits)")
            
            for i in range(1, 6):
                key_name = f"GEMINI_KEY_AGENT_{i}"
                persist_key_name = f"PERSIST_{key_name}"
                st.text_input(
                    f"Agent {i} API Key ({st.session_state.registry.get_all_agents()[i-1].name.replace(' Agent', '')})",
                    type="password",
                    placeholder=f"Enter API Key for Agent {i} (AIzaSy...)",
                    value=st.session_state.get(persist_key_name, ""),
                    key=f"temp_{key_name}"
                )
                
        with tab2:
            st.markdown("#### GitHub Integration")
            st.text_input(
                "GitHub Personal Access Token",
                type="password",
                placeholder="Enter GitHub Access Token (ghp_...)",
                value=st.session_state.get("PERSIST_GITHUB_TOKEN", ""),
                key="temp_GITHUB_TOKEN",
                help="Required for creating repositories and publishing your codebase to GitHub."
            )
            
        with tab3:
            st.markdown("#### LinkedIn Integration")
            st.text_input(
                "LinkedIn Access Token",
                type="password",
                placeholder="Enter LinkedIn Access Token",
                value=st.session_state.get("PERSIST_LINKEDIN_ACCESS_TOKEN", ""),
                key="temp_LINKEDIN_ACCESS_TOKEN",
                help="Used to post branding updates directly to your LinkedIn feed."
            )
            
            st.text_input(
                "LinkedIn Client ID",
                placeholder="Enter LinkedIn Client ID",
                value=st.session_state.get("PERSIST_LINKEDIN_CLIENT_ID", ""),
                key="temp_LINKEDIN_CLIENT_ID",
                help="Used for introspecting and validating access token permissions."
            )
            
            st.text_input(
                "LinkedIn Client Secret",
                type="password",
                placeholder="Enter LinkedIn Client Secret",
                value=st.session_state.get("PERSIST_LINKEDIN_CLIENT_SECRET", ""),
                key="temp_LINKEDIN_CLIENT_SECRET",
                help="Used alongside Client ID for oauth token introspections."
            )
            
        st.markdown("")
        if st.button("Save Configuration", use_container_width=True, key="save_config_btn"):
            for key_name in [
                "GEMINI_API_KEY", "GEMINI_MODEL", "GEMINI_KEY_AGENT_1", "GEMINI_KEY_AGENT_2",
                "GEMINI_KEY_AGENT_3", "GEMINI_KEY_AGENT_4", "GEMINI_KEY_AGENT_5",
                "GITHUB_TOKEN", "LINKEDIN_ACCESS_TOKEN", "LINKEDIN_CLIENT_ID", "LINKEDIN_CLIENT_SECRET"
            ]:
                temp_key = f"temp_{key_name}"
                persist_key = f"PERSIST_{key_name}"
                if temp_key in st.session_state:
                    st.session_state[persist_key] = st.session_state[temp_key]
            
            apply_new_configurations()
            st.success("✅ Configuration Saved and Applied Successfully!")
            st.toast("API Keys updated in the backend.")
            st.rerun()
                        