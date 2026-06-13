import streamlit as st
import random
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import io
import zipfile
import json
import os

THEME_CONFIG_FILE = "theme_config.json"

def load_theme_config():
    if os.path.exists(THEME_CONFIG_FILE):
        try:
            with open(THEME_CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"manual_theme": "🌊 Ocean Blue", "auto_color": True}

def save_theme_config(manual_theme, auto_color):
    try:
        with open(THEME_CONFIG_FILE, "w") as f:
            json.dump({"manual_theme": manual_theme, "auto_color": auto_color}, f)
    except:
        pass

from modules.database import init_db, insert_migration, fetch_history, fetch_full_record
from modules.risk_model import predict_risk, train_model
from modules.report_generator import generate_text_report, export_findings_csv, generate_pdf_report, generate_docx_report, generate_html_report
from modules.email_service import send_email_report

from modules.advanced_engine import run_migration_workflow, build_dashboard_metrics
from modules.input_handler import handle_zip_upload, extract_code_from_pdf, extract_code_from_docx
from modules.github_integration import fetch_github_file, clone_github_repo

from modules.analyzer import analyze_code, extract_basic_metrics, generate_suggestions
from modules.converter import convert_python2_to_python3, create_diff_summary
from modules.api_key_manager import render_api_key_manager_page


st.set_page_config(
    page_title='AI-Based Legacy Code Migration System',
    page_icon='🧠',
    layout='wide'
)

init_db()

# ─────────────────────────────────────────────
# THEME DEFINITIONS
# ─────────────────────────────────────────────
THEMES = {
    "🌊 Ocean Blue": {
        "bg":           "#0a1628",
        "sidebar_bg":   "#0d1f3c",
        "card_bg":      "#112240",
        "accent1":      "#00b4d8",
        "accent2":      "#90e0ef",
        "accent3":      "#0077b6",
        "text":         "#caf0f8",
        "subtext":      "#90e0ef",
        "border":       "#00b4d8",
        "btn_bg":       "linear-gradient(135deg,#0077b6,#00b4d8)",
        "metric_glow":  "0 0 18px #00b4d855",
        "hero_grad":    "linear-gradient(135deg,#0077b6 0%,#00b4d8 50%,#90e0ef 100%)",
        "chart_palette":["#00b4d8","#0077b6","#90e0ef","#caf0f8","#023e8a"],
    },
    "🌙 Galaxy Purple": {
        "bg":           "#0b0015",
        "sidebar_bg":   "#120025",
        "card_bg":      "#1a003a",
        "accent1":      "#c77dff",
        "accent2":      "#e0aaff",
        "accent3":      "#7b2ff7",
        "text":         "#f3d9fa",
        "subtext":      "#c77dff",
        "border":       "#7b2ff7",
        "btn_bg":       "linear-gradient(135deg,#7b2ff7,#c77dff)",
        "metric_glow":  "0 0 18px #c77dff55",
        "hero_grad":    "linear-gradient(135deg,#3a0068 0%,#7b2ff7 50%,#c77dff 100%)",
        "chart_palette":["#c77dff","#7b2ff7","#e0aaff","#f3d9fa","#3a0068"],
    },
    "🌅 Sunset Fire": {
        "bg":           "#1a0800",
        "sidebar_bg":   "#2b0d00",
        "card_bg":      "#3d1500",
        "accent1":      "#ff6b35",
        "accent2":      "#ffd166",
        "accent3":      "#ef233c",
        "text":         "#fff3e0",
        "subtext":      "#ffd166",
        "border":       "#ff6b35",
        "btn_bg":       "linear-gradient(135deg,#ef233c,#ff6b35)",
        "metric_glow":  "0 0 18px #ff6b3555",
        "hero_grad":    "linear-gradient(135deg,#ef233c 0%,#ff6b35 50%,#ffd166 100%)",
        "chart_palette":["#ff6b35","#ffd166","#ef233c","#fff3e0","#c9184a"],
    },
    "🌿 Emerald Forest": {
        "bg":           "#021a0f",
        "sidebar_bg":   "#032b18",
        "card_bg":      "#053d22",
        "accent1":      "#2dc653",
        "accent2":      "#80ed99",
        "accent3":      "#1a7431",
        "text":         "#d8f3dc",
        "subtext":      "#80ed99",
        "border":       "#2dc653",
        "btn_bg":       "linear-gradient(135deg,#1a7431,#2dc653)",
        "metric_glow":  "0 0 18px #2dc65355",
        "hero_grad":    "linear-gradient(135deg,#1a7431 0%,#2dc653 50%,#80ed99 100%)",
        "chart_palette":["#2dc653","#80ed99","#1a7431","#d8f3dc","#52b788"],
    },
    "⚡ Cyber Neon": {
        "bg":           "#000814",
        "sidebar_bg":   "#001427",
        "card_bg":      "#001f3f",
        "accent1":      "#00f5ff",
        "accent2":      "#f72585",
        "accent3":      "#7209b7",
        "text":         "#e0fbfc",
        "subtext":      "#00f5ff",
        "border":       "#f72585",
        "btn_bg":       "linear-gradient(135deg,#7209b7,#f72585,#00f5ff)",
        "metric_glow":  "0 0 22px #00f5ff66",
        "hero_grad":    "linear-gradient(135deg,#7209b7 0%,#f72585 50%,#00f5ff 100%)",
        "chart_palette":["#00f5ff","#f72585","#7209b7","#e0fbfc","#4cc9f0"],
    },
    "🌹 Rose Gold": {
        "bg":           "#1a0a10",
        "sidebar_bg":   "#2a1018",
        "card_bg":      "#3d1525",
        "accent1":      "#e8998d",
        "accent2":      "#eec4c8",
        "accent3":      "#b5636c",
        "text":         "#fde8e8",
        "subtext":      "#eec4c8",
        "border":       "#e8998d",
        "btn_bg":       "linear-gradient(135deg,#b5636c,#e8998d,#eec4c8)",
        "metric_glow":  "0 0 18px #e8998d55",
        "hero_grad":    "linear-gradient(135deg,#b5636c 0%,#e8998d 50%,#eec4c8 100%)",
        "chart_palette":["#e8998d","#b5636c","#eec4c8","#fde8e8","#c97b84"],
    },
    "❄️ Arctic Ice": {
        "bg":           "#050e1a",
        "sidebar_bg":   "#081828",
        "card_bg":      "#0c2238",
        "accent1":      "#a8dadc",
        "accent2":      "#f1faee",
        "accent3":      "#457b9d",
        "text":         "#f1faee",
        "subtext":      "#a8dadc",
        "border":       "#457b9d",
        "btn_bg":       "linear-gradient(135deg,#1d3557,#457b9d,#a8dadc)",
        "metric_glow":  "0 0 18px #a8dadc55",
        "hero_grad":    "linear-gradient(135deg,#1d3557 0%,#457b9d 50%,#a8dadc 100%)",
        "chart_palette":["#a8dadc","#457b9d","#1d3557","#f1faee","#e63946"],
    },
    "🌌 Midnight Teal": {
        "bg":           "#04100f",
        "sidebar_bg":   "#081c1a",
        "card_bg":      "#0d2927",
        "accent1":      "#2ec4b6",
        "accent2":      "#cbf3f0",
        "accent3":      "#1a936f",
        "text":         "#e0f5f0",
        "subtext":      "#2ec4b6",
        "border":       "#1a936f",
        "btn_bg":       "linear-gradient(135deg,#1a936f,#2ec4b6,#cbf3f0)",
        "metric_glow":  "0 0 18px #2ec4b655",
        "hero_grad":    "linear-gradient(135deg,#114b5f 0%,#1a936f 50%,#2ec4b6 100%)",
        "chart_palette":["#2ec4b6","#1a936f","#cbf3f0","#e0f5f0","#88d498"],
    },
    "🌫️ Neutral Gray": {
        "bg":           "#f4f4f5",
        "sidebar_bg":   "#ffffff",
        "card_bg":      "#ffffff",
        "accent1":      "#52525b",
        "accent2":      "#71717a",
        "accent3":      "#a1a1aa",
        "text":         "#18181b",
        "subtext":      "#52525b",
        "border":       "#e4e4e7",
        "btn_bg":       "linear-gradient(135deg,#52525b,#71717a)",
        "metric_glow":  "0 0 18px #a1a1aa55",
        "hero_grad":    "linear-gradient(135deg,#18181b 0%,#52525b 50%,#71717a 100%)",
        "chart_palette":["#52525b","#71717a","#a1a1aa","#d4d4d8","#18181b"],
    },
}

THEME_NAMES = list(THEMES.keys())

# Map each page to a unique theme so colors auto-change per page
PAGE_THEME_MAP = {
    "🏠 Home":                      "🌊 Ocean Blue",
    "📤 Upload & Migrate":          "🌙 Galaxy Purple",
    "🔬 Advanced Analysis Center":  "⚡ Cyber Neon",
    "📊 Analytics Dashboard":       "🌅 Sunset Fire",
    "🕐 Migration History":         "🌿 Emerald Forest",
    "🤖 ML Risk Model":             "🌌 Midnight Teal",
    "⚙️ Settings":                  "❄️ Arctic Ice",
    "🔑 API Key Manager":           "🌹 Rose Gold",
}

# ─────────────────────────────────────────────
# CSS INJECTION
# ─────────────────────────────────────────────
def inject_theme_css(t: dict) -> None:
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

    /* ── Global transition — smooth color change on page/theme switch ── */
    *, *::before, *::after {{
        transition: background-color 0.6s cubic-bezier(.4,0,.2,1),
                    color 0.5s cubic-bezier(.4,0,.2,1),
                    border-color 0.5s ease,
                    box-shadow 0.5s ease,
                    transform 0.3s ease,
                    filter 0.3s ease !important;
    }}

    /* Apply custom font safely without breaking Material Icons */
    html, body, .stApp, p, h1, h2, h3, h4, h5, h6, li, label, .stMarkdown {{
        font-family: 'Inter', sans-serif;
    }}

    /* ── App background ── */
    .stApp, [data-testid="stAppViewContainer"] {{
        background: {t["bg"]} !important;
        background-image: radial-gradient(ellipse at 20% 10%, {t["accent3"]}18 0%, transparent 55%),
                          radial-gradient(ellipse at 80% 90%, {t["accent1"]}12 0%, transparent 55%) !important;
    }}

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {{
        background: {t["sidebar_bg"]} !important;
        border-right: 1px solid {t["border"]}44 !important;
        box-shadow: 4px 0 24px {t["accent1"]}22 !important;
    }}
    [data-testid="stSidebar"] * {{
        color: {t["text"]} !important;
    }}
    [data-testid="stSidebarNav"] li span,
    [data-testid="stSidebar"] label {{
        color: {t["subtext"]} !important;
        font-weight: 600 !important;
    }}

    /* ── All text ── */
    h1, h2, h3, h4, h5, h6, p, span, label, div, .stMarkdown {{
        color: {t["text"]} !important;
    }}

    /* ── Main title animation ── */
    .main-title {{
        font-size: 42px !important;
        font-weight: 800 !important;
        background: {t["hero_grad"]} !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        animation: fadeInDown 0.8s ease, shimmer 4s ease-in-out infinite alternate !important;
        letter-spacing: -1px !important;
    }}
    @keyframes fadeInDown {{
        from {{ opacity: 0; transform: translateY(-30px); }}
        to   {{ opacity: 1; transform: translateY(0);     }}
    }}
    @keyframes shimmer {{
        0%   {{ filter: brightness(1);   }}
        100% {{ filter: brightness(1.3); }}
    }}

    /* ── Fade-in for page content ── */
    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(24px); }}
        to   {{ opacity: 1; transform: translateY(0);    }}
    }}
    @keyframes slideInLeft {{
        from {{ opacity: 0; transform: translateX(-30px); }}
        to   {{ opacity: 1; transform: translateX(0);     }}
    }}
    .block-container {{
        animation: fadeInUp 0.6s cubic-bezier(.4,0,.2,1) !important;
        padding-top: 2rem !important;
    }}

    /* ── Metrics cards ── */
    [data-testid="stMetric"] {{
        background: {t["card_bg"]} !important;
        border: 1px solid {t["border"]}66 !important;
        border-radius: 14px !important;
        padding: 18px !important;
        box-shadow: {t["metric_glow"]} !important;
        animation: fadeInUp 0.7s ease !important;
    }}
    [data-testid="stMetric"]:hover {{
        transform: translateY(-6px) scale(1.03) !important;
        box-shadow: 0 12px 40px {t["accent1"]}55 !important;
        border-color: {t["accent1"]} !important;
    }}
    [data-testid="stMetricValue"] {{
        color: {t["accent1"]} !important;
        font-size: 28px !important;
        font-weight: 800 !important;
    }}
    [data-testid="stMetricLabel"] {{
        color: {t["subtext"]} !important;
        font-weight: 600 !important;
    }}

    /* ── Info / success / warning / error boxes ── */
    [data-testid="stAlert"] {{
        background: {t["card_bg"]} !important;
        border-left: 4px solid {t["accent1"]} !important;
        border-radius: 10px !important;
        animation: slideInLeft 0.5s ease !important;
    }}
    [data-testid="stAlert"]:hover {{
        transform: translateX(6px) !important;
        border-left-width: 6px !important;
        box-shadow: 0 4px 20px {t["accent1"]}33 !important;
    }}

    /* ── Buttons ── */
    .stButton > button {{
        background: {t["btn_bg"]} !important;
        color: #fff !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        padding: 10px 24px !important;
        box-shadow: 0 4px 16px {t["accent1"]}44 !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-3px) scale(1.05) !important;
        box-shadow: 0 10px 32px {t["accent1"]}66 !important;
        filter: brightness(1.15) !important;
    }}
    .stButton > button:active {{
        transform: scale(0.96) !important;
        box-shadow: 0 2px 8px {t["accent1"]}33 !important;
    }}

    /* ── Download buttons ── */
    .stDownloadButton > button {{
        background: {t["btn_bg"]} !important;
        color: #fff !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 16px {t["accent1"]}44 !important;
    }}
    .stDownloadButton > button:hover {{
        transform: translateY(-3px) scale(1.04) !important;
        box-shadow: 0 8px 28px {t["accent1"]}66 !important;
    }}

    /* ── Inputs / text areas / select ── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div,
    .stRadio > div {{
        background: {t["card_bg"]} !important;
        color: {t["text"]} !important;
        border: 1px solid {t["border"]}66 !important;
        border-radius: 10px !important;
    }}
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: {t["accent1"]} !important;
        box-shadow: 0 0 0 3px {t["accent1"]}33 !important;
    }}

    /* ── Dataframe / tables ── */
    [data-testid="stDataFrame"], .dataframe {{
        background: {t["card_bg"]} !important;
        border: 1px solid {t["border"]}44 !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }}

    /* ── Divider ── */
    hr {{
        border-color: {t["border"]}44 !important;
        margin: 20px 0 !important;
    }}

    /* ── Code blocks ── */
    [data-testid="stCode"] {{
        background: {t["card_bg"]} !important;
        border: 1px solid {t["border"]}44 !important;
        border-radius: 10px !important;
    }}

    /* ── Subheader text ── */
    .stApp h2, .stApp h3 {{
        color: {t["accent2"]} !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px !important;
    }}

    /* ── Caption ── */
    .stApp [data-testid="stCaptionContainer"] {{
        color: {t["subtext"]} !important;
    }}

    /* ── Theme badge in sidebar ── */
    .theme-badge {{
        display: inline-block;
        padding: 6px 16px;
        border-radius: 20px;
        background: {t["btn_bg"]};
        color: #fff;
        font-size: 13px;
        font-weight: 700;
        margin-top: 6px;
        box-shadow: 0 2px 10px {t["accent1"]}44;
        animation: pulse 2s ease-in-out infinite;
    }}
    @keyframes pulse {{
        0%, 100% {{ box-shadow: 0 2px 10px {t["accent1"]}44; }}
        50%        {{ box-shadow: 0 6px 24px {t["accent1"]}88; }}
    }}

    /* ── Color swatch circles ── */
    .color-swatch {{
        display: inline-block;
        width: 18px; height: 18px;
        border-radius: 50%;
        margin: 0 3px;
        border: 2px solid {t["text"]}66;
        vertical-align: middle;
    }}

    /* ── Spinner ── */
    .stSpinner > div {{
        border-top-color: {t["accent1"]} !important;
    }}

    /* ── Progress bar ── */
    .stProgress > div > div > div {{
        background: {t["btn_bg"]} !important;
        border-radius: 10px !important;
    }}

    /* ── Sidebar radio active ── */
    [data-testid="stSidebar"] [aria-checked="true"] + div {{
        color: {t["accent1"]} !important;
        font-weight: 800 !important;
    }}

    /* ── Scrollbar ── */
    ::-webkit-scrollbar {{ width: 6px; }}
    ::-webkit-scrollbar-track {{ background: {t["bg"]}; }}
    ::-webkit-scrollbar-thumb {{
        background: {t["accent3"]} !important;
        border-radius: 10px !important;
    }}

    /* ── File uploader ── */
    [data-testid="stFileUploader"] {{
        background: {t["card_bg"]} !important;
        border: 1px dashed {t["border"]}66 !important;
        border-radius: 12px !important;
        padding: 12px !important;
    }}
    [data-testid="stFileUploader"]:hover {{
        border-color: {t["accent1"]} !important;
        box-shadow: 0 0 16px {t["accent1"]}22 !important;
    }}

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab"] {{
        color: {t["subtext"]} !important;
        font-weight: 600 !important;
    }}
    .stTabs [aria-selected="true"] {{
        color: {t["accent1"]} !important;
        border-bottom-color: {t["accent1"]} !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

    # Replace Streamlit default upload label text.
    # Scope this to the Upload & Migrate page to avoid duplicated/incorrect visuals elsewhere.
    st.markdown(
        """
        <style>
        /* Upload & Migrate — scoped improvements (do not affect other pages) */

        /* Make the page content breathe a bit more consistently */
        .upload-migrate-page .block-container {
            padding-top: 1.2rem !important;
        }

        /* Hide Streamlit's default label + helper text (commonly shows “more then/other”) */
        .upload-migrate-page [data-testid="stFileUploader"] label,
        .upload-migrate-page [data-testid="stFileUploader"] .stMarkdown,
        .upload-migrate-page [data-testid="stFileUploader"] p,
        .upload-migrate-page [data-testid="stFileUploader"] span,
        .upload-migrate-page [data-testid="stFileUploader"] small,
        .upload-migrate-page [data-testid="stFileUploader"] em {
            display: none !important;
        }

        /* Keep the dropzone clickable + centered visually */
        .upload-migrate-page [data-testid="stFileUploader"] section {
            text-align: center;
        }

        /* Re-inject a single consistent label as a badge */
        .upload-migrate-page [data-testid="stFileUploader"] section::before {
            content: "Upload";
            visibility: visible !important;
            display: inline-block;
            font-size: 13px;
            letter-spacing: 0.2px;
            line-height: 1.2;
            color: #ffffff;
            font-weight: 800;
            padding: 6px 12px;
            margin: 2px 0 10px 0;
            border-radius: 999px;
            background: linear-gradient(135deg, rgba(199,125,255,0.95), rgba(0,180,216,0.95));
            border: 1px solid rgba(255,255,255,0.18);
            box-shadow: 0 10px 30px rgba(0,0,0,0.25);
        }

        /* Make the internal Browse button styling consistent */
        .upload-migrate-page [data-testid="stFileUploader"] button {
            background-color: rgba(18,18,18,0.95) !important;
            color: white !important;
            border-radius: 10px !important;
            padding: 10px 16px !important;
            line-height: 1.2 !important;
            margin: 10px auto 0 auto !important;
            display: inline-block !important;
            font-weight: 800 !important;
        }

        /* Dropzone hover polish */
        .upload-migrate-page [data-testid="stFileUploader"]:hover {
            box-shadow: 0 0 0 1px rgba(255,255,255,0.08), 0 0 22px rgba(199,125,255,0.18) !important;
        }

        /* Fix alignment/width for the separate Analyze button under the uploader */
        .upload-migrate-page .stButton > button {
            width: auto !important;
            min-width: 220px !important;
            text-align: center !important;
            border-radius: 12px !important;
        }

        /* Improve the radio group spacing slightly */
        .upload-migrate-page .stRadio {
            margin-top: 0.2rem !important;
        }

        /* Tabs inside Upload & Migrate (scoped) */
        .upload-migrate-page .stTabs [data-baseweb="tab"] {
            border-radius: 12px !important;
            padding: 10px 14px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )



# ─────────────────────────────────────────────
# SIDEBAR — Navigation + auto-color per page
# ─────────────────────────────────────────────
theme_config = load_theme_config()

if "auto_color_toggle" not in st.session_state:
    st.session_state["auto_color_toggle"] = theme_config.get("auto_color", True)
if "theme_select" not in st.session_state:
    st.session_state["theme_select"] = theme_config.get("manual_theme", "🌊 Ocean Blue")

def shuffle_theme():
    current_theme = st.session_state.get("theme_select", "🌊 Ocean Blue")
    other_themes = [n for n in THEME_NAMES if n != current_theme]
    new_theme = random.choice(other_themes)
    
    st.session_state["theme_select"] = new_theme
    st.session_state["auto_color_toggle"] = False
    save_theme_config(new_theme, False)

def on_theme_change():
    save_theme_config(st.session_state["theme_select"], st.session_state["auto_color_toggle"])

def on_auto_color_change():
    save_theme_config(st.session_state["theme_select"], st.session_state["auto_color_toggle"])

def on_page_change():
    page = st.session_state.get('nav_radio')
    if page:
        st.session_state['current_page'] = page
        st.query_params["page"] = page

with st.sidebar:
    st.markdown("## 🧠 CodeMigrate AI")
    st.markdown("---")

    # Navigation first — so we know which page is active
    st.markdown("### 🗂️ Navigation")
    
    pages_list = [
        "🏠 Home",
        "📤 Upload & Migrate",
        "🔬 Advanced Analysis Center",
        "📊 Analytics Dashboard",
        "🕐 Migration History",
        "🤖 ML Risk Model",
        "⚙️ Settings",
        "🔑 API Key Manager",
    ]
    
    # Read from query params to persist state
    current_page = st.query_params.get("page")
    if not current_page:
        current_page = st.session_state.get('current_page', "🏠 Home")
    if current_page not in pages_list:
        current_page = "🏠 Home"
        
    page = st.radio(
        "Go to",
        pages_list,
        index=pages_list.index(current_page),
        label_visibility="collapsed",
        key="nav_radio",
        on_change=on_page_change
    )
    st.session_state['current_page'] = page
    st.query_params["page"] = page
    st.markdown("---")

    # Theme controls
    st.markdown("### 🎨 Theme Controls")

    auto_color = st.toggle("🌈 Auto-Color per Page", key="auto_color_toggle", on_change=on_auto_color_change)

    if auto_color:
        # Each page gets its own assigned theme
        active_theme_name = PAGE_THEME_MAP.get(page, "🌊 Ocean Blue")
        t = THEMES[active_theme_name]
        st.caption(f"Page theme: **{active_theme_name}**")
    else:
        # Manual theme selector
        chosen_theme = st.selectbox(
            "Color Theme",
            THEME_NAMES,
            label_visibility="collapsed",
            key="theme_select",
            on_change=on_theme_change
        )
        active_theme_name = chosen_theme
        t = THEMES[chosen_theme]

    # Shuffle button — picks a random theme
    st.button("🎲 Shuffle Colors", key="shuffle_btn", on_click=shuffle_theme)

    # Show active theme badge with color swatches
    st.markdown(
        f'<div class="theme-badge">{active_theme_name} Active</div>'
        f'<div style="margin-top:8px;">'
        f'<span class="color-swatch" style="background:{t["accent1"]}"></span>'
        f'<span class="color-swatch" style="background:{t["accent2"]}"></span>'
        f'<span class="color-swatch" style="background:{t["accent3"]}"></span>'
        f'<span class="color-swatch" style="background:{t["card_bg"]}"></span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

# Inject CSS for the active theme
inject_theme_css(t)


# ─────────────────────────────────────────────
# HELPER — chart styling to match theme
# ─────────────────────────────────────────────
def style_fig(fig, ax):
    fig.patch.set_facecolor(t["card_bg"])
    ax.set_facecolor(t["card_bg"])
    ax.tick_params(colors=t["subtext"])
    ax.xaxis.label.set_color(t["subtext"])
    ax.yaxis.label.set_color(t["subtext"])
    ax.title.set_color(t["accent2"])
    for spine in ax.spines.values():
        spine.set_edgecolor(t["border"] + "55")


# ─────────────────────────────────────────────
# PAGE: HOME
# ─────────────────────────────────────────────
def show_home():
    st.markdown('# 🧠 AI-Based Legacy Code Migration & Analysis System')
    st.markdown('## **Modernize your legacy codebase with AI-powered analysis.**')
    st.markdown(
        f'<p style="color:{t["subtext"]};font-size:17px;margin-top:8px;">'
        'Upload code from multiple sources, detect deprecated syntax, auto-migrate Python 2 → 3, '
        'scan for security risks, analyze dependencies, predict migration risk, and generate professional reports — all in one place.'
        '</p>', unsafe_allow_html=True
    )

    st.markdown("---")
    st.subheader("🚀 What This System Can Do")

    st.markdown(f'<h4 style="color:{t["accent1"]}">📥 Input Sources — Multiple Ways to Bring Your Code</h4>', unsafe_allow_html=True)
    r1c1, r1c2, r1c3, r1c4, r1c5 = st.columns(5)
    with r1c1:
        st.info('📄 **Upload Files**\n`.py` `.js` `.java` `.php` `.c` `.cpp` `.ts` `.sql` `.sh`\nDirect file upload for instant analysis.')
    with r1c2:
        st.info('📋 **Paste Code**\nDirectly paste any code snippet and run analysis on the fly.')
    with r1c3:
        st.info('🗜️ **ZIP Archive**\nUpload a ZIP of your project — extract and pick any file to analyze.')
    with r1c4:
        st.info('🐙 **GitHub URL**\nPaste a GitHub file or repo URL — fetch and analyze code directly.')
    with r1c5:
        st.info('📑 **PDF / DOCX**\nExtract and analyze code snippets embedded inside documents.')

    st.markdown("---")
    st.markdown(f'<h4 style="color:{t["accent1"]}">🔄 Core Code Migration & Modernization</h4>', unsafe_allow_html=True)
    r2c1, r2c2, r2c3 = st.columns(3)
    with r2c1:
        st.success('🐍 **Python 2 → Python 3**\nAuto-convert `print`, `xrange`, `raw_input`, unicode literals, and more.')
    with r2c2:
        st.success('🔍 **Deprecated Syntax Detection**\nScan legacy patterns across multiple languages using rule-based and ML engines.')
    with r2c3:
        st.success('📊 **Side-by-Side Diff**\nOriginal vs. migrated code with a detailed diff summary of all changed lines.')

    st.markdown("---")
    st.markdown(f'<h4 style="color:{t["accent1"]}">🔬 Advanced Code Analysis</h4>', unsafe_allow_html=True)
    r3c1, r3c2, r3c3, r3c4 = st.columns(4)
    with r3c1:
        st.warning('🛡️ **Security Scanning**\nDetect hardcoded credentials, unsafe `eval`, SQL injection patterns, and more.')
    with r3c2:
        st.warning('📦 **Dependency Analysis**\nIdentify outdated libraries and get modernization hints with replacements.')
    with r3c3:
        st.warning('⚠️ **Runtime Risk Detection**\nFlag risky patterns that may cause runtime failures post-migration.')
    with r3c4:
        st.warning('🗑️ **Unused Code Detection**\nSpot unused helpers and dead code that can be safely removed.')

    st.markdown("---")
    st.markdown(f'<h4 style="color:{t["accent1"]}">🤖 AI / ML & Reporting</h4>', unsafe_allow_html=True)
    r4c1, r4c2, r4c3 = st.columns(3)
    with r4c1:
        st.error('🎯 **ML Risk Prediction**\nScikit-learn RandomForest predicts migration risk: Low / Medium / High.')
    with r4c2:
        st.error('📝 **Automated Reports**\nDownload text reports and CSV exports of all findings.')
    with r4c3:
        st.error('🗺️ **Migration Roadmap**\nStep-by-step actionable roadmap tailored to your codebase\'s issues.')

    st.markdown("---")
    st.markdown(f'<h4 style="color:{t["accent1"]}">📊 Analytics, History & Settings</h4>', unsafe_allow_html=True)
    r5c1, r5c2, r5c3 = st.columns(3)
    with r5c1:
        st.info('🕐 **Migration History**\nAll past migrations stored in SQLite — browse, compare, revisit anytime.')
    with r5c2:
        st.info('📈 **Analytics Dashboard**\nVisual charts: risk distributions, issue trends, file-level comparisons.')
    with r5c3:
        st.info('🔑 **API Key Manager**\nConfigure LLM provider keys (OpenAI, Gemini, etc.) saved persistently to `.env`.')

    st.markdown("---")
    st.subheader("🛠️ Project Tools Used")
    tools = pd.DataFrame({
        'Area': ['Frontend', 'Backend', 'Code Parsing', 'AI/ML', 'Security', 'Database', 'Visualization', 'File Handling', 'Deployment'],
        'Tools': [
            'Streamlit',
            'Python 3',
            'Regex, Python built-ins, Pandas',
            'Scikit-learn (RandomForest), Rule-based engine, LLM Router (OpenAI / Gemini)',
            'Custom static scanner (eval, hardcoded secrets, SQL injection)',
            'SQLite',
            'Matplotlib, Seaborn',
            'ZIP extraction, PDF (pdfplumber), DOCX (python-docx), GitHub API',
            'GitHub, Streamlit Cloud',
        ]
    })
    st.dataframe(tools, use_container_width=True)


# ─────────────────────────────────────────────
# PAGE: UPLOAD & MIGRATE
# ─────────────────────────────────────────────
def get_file_extension(language: str) -> str:
    ext_map = {
        "Python": ".py", "JavaScript": ".js", "Java": ".java", 
        "PHP": ".php", "C": ".c", "C++": ".cpp", "SQL": ".sql", 
        "Shell": ".sh", "TypeScript": ".ts"
    }
    return ext_map.get(language, ".txt")

def render_analysis_output(code: str, filename: str, source_label: str = 'uploaded code'):
    # Create a unique key for the current file content to detect changes
    import hashlib
    content_hash = hashlib.md5(code.encode()).hexdigest()
    
    if ("current_analysis" not in st.session_state or 
        st.session_state.get("last_file_hash") != content_hash):
        
        with st.status("🚀 Processing code...", expanded=True) as status:
            st.write("Detecting language and metrics...")
            analysis = run_migration_workflow(code, filename=filename)
            st.session_state.current_analysis = analysis
            st.session_state.last_file_hash = content_hash
            status.update(label="Analysis Complete!", state="complete", expanded=False)

    res = st.session_state.current_analysis
    lang_ext = get_file_extension(res.get('language', 'Unknown'))
    
    # Extract variables from results dictionary to avoid NameErrors
    findings_df = res['findings_df']
    metrics = res['metrics']
    migrated_code = res['migrated_code']
    diff_summary = res['diff_summary']
    issue_count = res['issue_count']
    risk_level = res['risk_level']
    risk_score = res['risk_score']
    suggestions = res['suggestions_text']
    security_findings_df = res['security_findings_df']
    security_summary = res['security_summary']
    roadmap_text = res.get('roadmap_text', '')
    runtime_risks = res.get('runtime_risks', [])
    unused_functions = res.get('unused_functions', [])
    syntax_error = res.get('syntax_error')
    language = res.get('language', 'Unknown')
    migration_target = res.get('migration_target', 'Modern equivalent')
    dependency_findings = res.get('dependency_findings', [])

    tab_mig, tab_issues, tab_risk, tab_reports = st.tabs([
        "🔄 Migration Hub", "🔍 Issue Explorer", "📊 ML Risk Dashboard", "📥 Export Center"
    ])

    with tab_mig:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"#### 📄 Original ({res['language']})")
            st.code(code, language=res['language'].lower())
        with c2:
            st.markdown(f"#### ✨ Migrated ({res['migration_target']})")
            st.code(res['migrated_code'], language='python')
        
        st.download_button(
            label=f"💾 Download Migrated {lang_ext}",
            data=res['migrated_code'],
            file_name=f"migrated_{filename}{lang_ext}",
            mime="text/plain"
        )

    with tab_issues:
        st.markdown("### 🔍 Static Analysis Findings")
        if findings_df is not None and not findings_df.empty:
            st.dataframe(findings_df, use_container_width=True)
        else:
            st.success("No deprecated syntax found!")
            
        if res.get('security_findings_df') is not None and not res['security_findings_df'].empty:
            st.markdown("### 🛡️ Security Alerts")
            st.dataframe(res['security_findings_df'], use_container_width=True)

    with tab_risk:
        col_m1, col_m2 = st.columns([1, 2])
        with col_m1:
            st.metric("Risk Level", res['risk_level'])
            st.metric("Risk Score", f"{res['risk_score']}%")
            st.metric("Complexity Issues", len(findings_df))
        
        with col_m2:
            # Enhanced Donut Chart
            fig = go.Figure(data=[go.Pie(
                labels=['Confidence', 'Risk Factor'],
                values=[100 - res['risk_score'], res['risk_score']],
                hole=.6,
                marker_colors=[t["accent1"], t["accent2"]]
            )])
            fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), height=250, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

    with tab_reports:
        st.markdown("### 📥 Generate & Export Reports")
        r_col1, r_col2, r_col3 = st.columns(3)
        with r_col1:
            pdf_data = generate_pdf_report(res)
            st.download_button("📄 Download PDF Report", pdf_data, f"{filename}.pdf", "application/pdf")
        with r_col2:
            docx_data = generate_docx_report(res)
            st.download_button("📘 Download Word Report", docx_data, f"{filename}.docx")
        with r_col3:
            html_data = generate_html_report(res)
            st.download_button("🌐 Download HTML Report", html_data, f"{filename}.html", "text/html")
            
        st.divider()
        st.markdown("### 📧 Send Report to Email")
        email_addr = st.text_input("Enter recipient email", placeholder="client@example.com")
        if st.button("🚀 Send PDF Report"):
            if email_addr:
                with st.spinner("Sending..."):
                    ok, msg = send_email_report(email_addr, generate_pdf_report(res), filename, "pdf")
                    if ok: st.success(msg)
                    else: st.error(msg)
            else:
                st.warning("Please enter an email address.")

    st.caption(f'Detected language: {language} | Target path: {migration_target}')
    if dependency_findings:
        st.info(f'Found {len(dependency_findings)} dependency or library modernization hints.')
        st.dataframe(pd.DataFrame(dependency_findings)[['library', 'status', 'replacement', 'line']], use_container_width=True)

    st.subheader('🔍 Detected Issues')
    if findings_df is None or findings_df.empty:
        st.success('No major deprecated syntax found.')
    else:
        st.dataframe(findings_df, use_container_width=True)

    st.subheader('💡 Suggestions')
    st.text(suggestions)

    st.subheader('🗺️ Migration Roadmap')
    st.text(roadmap_text)

    if runtime_risks:
        st.caption('Runtime risk signals')
        for item in runtime_risks:
            st.warning(item)

    if unused_functions:
        st.caption('Potentially unused helpers')
        st.write(', '.join(unused_functions))

    if syntax_error:
        st.error(f'Syntax check issue on line {syntax_error["line"]}: {syntax_error["message"]}')

    st.subheader('🛡️ Security Findings (Basic Static Checks)')
    if security_findings_df is None or security_findings_df.empty:
        st.success('No high-confidence security issues found by basic static checks.')
    else:
        st.dataframe(security_findings_df, use_container_width=True)
        st.text('Security Summary:')
        st.text(security_summary)

    st.subheader('📊 Metrics Chart')
    metric_df = pd.DataFrame({
        'Metric': ['Lines', 'Functions', 'Classes', 'Imports', 'Issues'],
        'Count': [metrics.get('total_lines', 0), metrics.get('functions', 0), metrics.get('classes', 0), metrics.get('imports', 0), issue_count]
    })
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(data=metric_df, x='Metric', y='Count', ax=ax, palette=t["chart_palette"])
    ax.set_title('Code Analysis Metrics')
    style_fig(fig, ax)
    st.pyplot(fig)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.download_button('⬇️ Download Migrated Code', migrated_code, file_name=f'migrated_{filename}', mime='text/plain')
    with col_b:
        report_path, report_content = generate_text_report(filename, metrics, findings_df, risk_level, risk_score, suggestions)
        st.download_button('📄 Download Report', report_content, file_name=report_path.name, mime='text/plain')
    with col_c:
        if findings_df is not None and not findings_df.empty:
            csv_path = export_findings_csv(findings_df)
            st.download_button('📋 Download Issues CSV', findings_df.to_csv(index=False), file_name=csv_path.name, mime='text/csv')

    if st.button('💾 Save Migration History'):
        insert_migration(filename, code, migrated_code, issue_count, risk_score, risk_level, suggestions)
        st.success('Migration saved successfully in SQLite database.')


def create_bulk_migration_zip(migrated_files: dict):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in migrated_files.items():
            zf.writestr(name, content)
    buf.seek(0)
    return buf.getvalue()

def show_upload_migrate():
    st.markdown('<div class="upload-migrate-page">', unsafe_allow_html=True)

    st.header('📤 Upload & Migrate Code')
    st.divider()
    st.write('Choose a source to analyze. ZIP, GitHub, PDF, DOCX, and pasted code all flow through the same modernization engine.')

    input_mode = st.radio('Input source', ['Upload file', 'Paste code', 'ZIP archive', 'GitHub URL', 'PDF or DOCX'], horizontal=True)

    # Ensure the Upload & Migrate page has a stable state bucket
    # so the upload/analysis button can reliably trigger reruns.
    if 'upload_migrate_last_filename' not in st.session_state:
        st.session_state['upload_migrate_last_filename'] = None
    if 'upload_migrate_last_hash' not in st.session_state:
        st.session_state['upload_migrate_last_hash'] = None

    if input_mode == 'Upload file':
        uploaded_file = st.file_uploader(
            'Upload a legacy code file',
            type=['py', 'txt', 'js', 'java', 'php', 'c', 'cpp', 'cs', 'ts', 'sql', 'sh'],
            key='upload_legacy_file',
        )

        # Re-create a deterministic button-driven workflow:
        # - Do NOT auto-run analysis on upload (it can feel like the button “doesn’t work”)
        # - Only run analysis when user clicks the explicit button.
        def on_analyze_file_click():
            st.session_state['run_upload_analysis'] = True
            st.session_state['upload_migrate_last_filename'] = st.session_state.get('tmp_filename')
            st.session_state['upload_migrate_last_hash'] = st.session_state.get('tmp_filehash')

        if uploaded_file is not None:
            raw = uploaded_file.read()
            code = raw.decode('utf-8', errors='ignore')

            import hashlib
            content_hash = hashlib.md5(code.encode()).hexdigest()
            st.session_state['tmp_filename'] = uploaded_file.name
            st.session_state['tmp_filehash'] = content_hash

            # Use a dedicated container so the button UI is not affected by surrounding layout/CSS.
            with st.container():
                st.caption(f"Selected: {uploaded_file.name}")

                # Center the upload action button visually.
                btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
                with btn_col1:
                    st.write("")
                with btn_col2:
                    st.button(
                        '▶ Analyze Uploaded File',
                        key='analyze_uploaded_file_btn',
                        use_container_width=True,
                        on_click=on_analyze_file_click
                    )
                with btn_col3:
                    st.write("")

            if st.session_state.get('run_upload_analysis') and st.session_state.get('upload_migrate_last_filename') == uploaded_file.name:
                render_analysis_output(code, uploaded_file.name, 'uploaded file')

    elif input_mode == 'Paste code':
        sample_codes = {
            "Blank (Type your own)": "",
            "Python 2 (Deprecated syntax)": "import urllib2\nimport md5\n\ntry:\n    print 'Starting script...'\n    for i in xrange(5):\n        print 'Count:', i\nexcept Exception, e:\n    print 'Error:', e\n",
            "JavaScript (Unsafe Eval)": "var data = '{ \"user\": \"admin\" }';\nvar parsed = eval('(' + data + ')');\n\nvar req = new XMLHttpRequest();\nreq.open('GET', '/api/data', false);\nreq.send(null);\n",
            "SQL (Injection Vulnerability)": "SELECT * FROM users WHERE username = '\" + username + \"' AND password = '\" + pwd + \"';\n\nIF @user = 'admin' BEGIN\n    PRINT 'Welcome Admin'\nEND\n"
        }
        
        def on_sample_change():
            sel = st.session_state.get('sample_code_select')
            if sel and sel in sample_codes:
                st.session_state['paste_code_area'] = sample_codes[sel]
                
        st.selectbox("💡 Need an example? Load a legacy snippet:", list(sample_codes.keys()), key='sample_code_select', on_change=on_sample_change)
        
        if 'paste_code_area' not in st.session_state:
            st.session_state['paste_code_area'] = ""
            
        code = st.text_area('Paste code to analyze', height=260, key='paste_code_area')
        
        def on_analyze_paste_click():
            st.session_state['run_paste_analysis'] = True
            st.session_state['pasted_code_content'] = st.session_state.get('paste_code_area', '')

        st.button('▶ Run analysis on pasted code', on_click=on_analyze_paste_click)
            
        if st.session_state.get('run_paste_analysis') and st.session_state.get('pasted_code_content', '').strip():
            render_analysis_output(st.session_state['pasted_code_content'], 'pasted_code.py', 'pasted code')

    elif input_mode == 'ZIP archive':
        zip_file = st.file_uploader('Upload a ZIP archive containing code files', type=['zip'])
        if zip_file is not None:
            files = handle_zip_upload(zip_file)
            if not files:
                st.warning('No supported code files were found in that archive.')
            else:
                st.caption(f'Extracted {len(files)} supported file(s) from the archive.')

                zip_tabs = st.tabs(["📄 Individual Analysis", "🚀 Bulk Migration"])

                with zip_tabs[0]:
                    selected_name = st.selectbox('Choose a file to analyze', list(files.keys()))
                    st.code(files[selected_name][:1000] + ("..." if len(files[selected_name]) > 1000 else ""), language='text')
                    
                    def on_analyze_zip_click():
                        st.session_state['run_zip_analysis'] = st.session_state.get('tmp_zip_filename')
                    
                    st.session_state['tmp_zip_filename'] = selected_name
                    st.button('▶ Analyze selected ZIP file', key='zip_analyze_btn', on_click=on_analyze_zip_click)
                        
                    if st.session_state.get('run_zip_analysis') == selected_name:
                        render_analysis_output(files[selected_name], selected_name, 'ZIP archive file')

                with zip_tabs[1]:
                    st.subheader("Bulk Migration Mode")
                    st.write(f"Process all **{len(files)}** files and download the results as a new ZIP archive.")
                    st.info("This will apply the modernization workflow to every supported file in the project.")
                    
                    def on_bulk_migrate_click():
                        st.session_state['run_bulk_migration'] = True
                        
                    st.button('🚀 Start Bulk Migration', key='bulk_zip_btn', on_click=on_bulk_migrate_click)
                    
                    if st.session_state.get('run_bulk_migration'):
                        st.session_state['run_bulk_migration'] = False
                        bulk_results = {}
                        bulk_prog = st.progress(0)
                        bulk_status = st.empty()

                        for i, (name, content) in enumerate(files.items()):
                            bulk_status.text(f"Migrating: {name}...")
                            # Run the full workflow to get migrated code
                            res = run_migration_workflow(content, filename=name)
                            bulk_results[name] = res.get('migrated_code', content)
                            bulk_prog.progress((i + 1) / len(files))

                        bulk_status.text("Creating ZIP archive...")
                        st.session_state['bulk_zip_data'] = create_bulk_migration_zip(bulk_results)
                        st.session_state['bulk_zip_count'] = len(files)
                        st.session_state['bulk_zip_name'] = f"migrated_{zip_file.name}"
                        bulk_status.empty()
                        bulk_prog.empty()
                        
                    if st.session_state.get('bulk_zip_data'):
                        st.success(f"Migration complete! {st.session_state['bulk_zip_count']} files processed.")
                        st.download_button(
                            label="📥 Download Migrated Project (ZIP)",
                            data=st.session_state['bulk_zip_data'],
                            file_name=st.session_state['bulk_zip_name'],
                            mime="application/zip"
                        )

    elif input_mode == 'GitHub URL':
        sample_urls = {
            "Blank (Type your own)": "",
            "Example: Small Repository (octocat/Hello-World)": "https://github.com/octocat/Hello-World",
            "Example: Single Python File": "https://github.com/psf/requests/blob/main/setup.py",
            "Example: Your GitHub Repository": "https://github.com/premprasad1707"
        }
        
        def on_github_sample_change():
            sel = st.session_state.get('github_sample_select')
            if sel and sel in sample_urls:
                st.session_state['github_url_input'] = sample_urls[sel]
                
        st.selectbox("💡 Need an example? Load a sample repository or file URL:", list(sample_urls.keys()), key='github_sample_select', on_change=on_github_sample_change)
        
        if 'github_url_input' not in st.session_state:
            st.session_state['github_url_input'] = ""
            
        github_url = st.text_input('GitHub file or repository URL', key='github_url_input', placeholder='https://github.com/owner/repo/blob/main/app.py')
        st.info("💡 **Suggestion:** You can paste a link to a specific file (e.g., `.../blob/main/app.py`) or an entire repository. Public repositories are fully supported.")
        if github_url:
            import requests
            url_parts = github_url.strip('/').split('github.com/')
            if len(url_parts) == 2:
                path_parts = url_parts[1].split('/')
                if len(path_parts) == 1:
                    owner = path_parts[0]
                    try:
                        r = requests.get(f"https://api.github.com/users/{owner}/repos", timeout=10)
                        if r.status_code == 200:
                            repos = r.json()
                            repo_names = [repo['name'] for repo in repos]
                            if repo_names:
                                selected_repo = st.selectbox(f"📦 Select a repository for @{owner}:", repo_names)
                                github_url = f"https://github.com/{owner}/{selected_repo}"
                            else:
                                st.warning(f"No public repositories found for user @{owner}.")
                                github_url = None
                        else:
                            st.error(f"Could not fetch user repositories from GitHub API (Status: {r.status_code}).")
                            github_url = None
                    except Exception as e:
                        st.error(f"Error fetching repositories: {e}")
                        github_url = None

        if github_url:
            if 'blob/' in github_url:
                code, error = fetch_github_file(github_url)
                if error:
                    st.error(error)
                else:
                    filename = github_url.split('/')[-1]
                    render_analysis_output(code, filename, 'GitHub file')
            else:
                files, error = clone_github_repo(github_url)
                if error:
                    st.error(error)
                else:
                    selected_name = st.selectbox('Choose a GitHub file to analyze', list(files.keys()))
                    st.caption('Fetched repository files from GitHub (first 30 supported files).')
                    st.code(files[selected_name], language='text')
                    def on_analyze_github_click():
                        st.session_state['run_github_analysis'] = st.session_state.get('tmp_github_filename')
                        
                    st.session_state['tmp_github_filename'] = selected_name
                    st.button('▶ Analyze selected GitHub file', on_click=on_analyze_github_click)
                    
                    if st.session_state.get('run_github_analysis') == selected_name:
                        render_analysis_output(files[selected_name], selected_name, 'GitHub repository file')

    elif input_mode == 'PDF or DOCX':
        pdf_docx = st.file_uploader('Upload a PDF or DOCX file containing code or snippets', type=['pdf', 'docx'])
        if pdf_docx is not None:
            ext = pdf_docx.name.lower().rsplit('.', 1)[-1]
            if ext == 'pdf':
                code = extract_code_from_pdf(pdf_docx)
            else:
                code = extract_code_from_docx(pdf_docx)
            if code.strip():
                render_analysis_output(code, pdf_docx.name, 'PDF/DOCX extraction')
            else:
                st.warning('No text could be extracted from that document.')

    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PAGE: ANALYTICS
# ─────────────────────────────────────────────
def show_analytics():
    st.header('📊 Analytics Dashboard')

    with st.expander("🛠️ Developer Tools", expanded=False):
        st.write("Generate bulk migration records to test charts, risk distributions, and history filters.")
        if st.button("🧪 Generate 50 Mock Transactions"):
            sample_data = {
                "legacy_mod.py": {
                    "orig": "import urllib2\nimport md5\nprint 'Starting legacy module...'\nfor i in xrange(10):\n    if dict.has_key('test'): pass\n",
                    "mig": "import urllib.request\nimport hashlib\nprint('Starting legacy module...')\nfor i in range(10):\n    if 'test' in dict: pass\n"
                },
                "auth_v1.js": {
                    "orig": "var user = eval('(' + jsonString + ')');\nvar req = new XMLHttpRequest();\nreq.open('GET', '/api', false);\n",
                    "mig": "const user = JSON.parse(jsonString);\nconst req = new XMLHttpRequest();\nreq.open('GET', '/api', true);\n"
                },
                "query.sql": {
                    "orig": "SELECT * FROM users WHERE username = '\" + username + \"' AND password = '\" + pwd + \"';\nIF @user = 'admin' BEGIN PRINT 'Welcome' END",
                    "mig": "SELECT * FROM users WHERE username = ? AND password = ?;\n-- Removed SQL injection vulnerabilities"
                },
                "deprecated.py": {
                    "orig": "import ConfigParser\ntry:\n    f = open('test.txt', 'r')\nexcept Exception, e:\n    print 'Error:', e\n",
                    "mig": "import configparser\ntry:\n    with open('test.txt', 'r') as f:\n        pass\nexcept Exception as e:\n    print(f'Error: {e}')\n"
                },
                "old_script.sh": {
                    "orig": "#!/bin/sh\neval \"$(curl -s http://example.com/script.sh)\"\nexport API_KEY=\"12345abcdef\"",
                    "mig": "#!/bin/bash\n# Removed unsafe eval curl\n# Ensure API keys are stored securely"
                }
            }
            sample_names = list(sample_data.keys())
            for _ in range(50):
                name = random.choice(sample_names)
                issues = random.randint(1, 100)
                score = random.randint(0, 100)
                level = "Low" if score < 30 else ("Medium" if score < 75 else "High")
                
                insert_migration(
                    filename=f"mock_{random.randint(100, 999)}_{name}",
                    original_code=sample_data[name]["orig"],
                    migrated_code=sample_data[name]["mig"],
                    issue_count=issues,
                    risk_score=score,
                    risk_level=level,
                    suggestions="Refactor deprecated libraries. Ensure strict type checking and avoid unsafe eval()."
                )
            st.success("Successfully added 50 mock transactions to the history!")
            st.rerun()

    rows = fetch_history()
    if not rows:
        st.info('No migration history found. Upload and save at least one file first.')
        return

    df = pd.DataFrame(rows, columns=['ID', 'Filename', 'Issue Count', 'Risk Score', 'Risk Level', 'Created At'])
    st.dataframe(df, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        risk_counts = df['Risk Level'].value_counts().reset_index()
        risk_counts.columns = ['Risk Level', 'Count']
        risk_colors = {'Low': t["accent1"], 'Medium': t["accent2"], 'High': t["accent3"]}
        
        fig1 = px.pie(
            risk_counts, 
            names='Risk Level', 
            values='Count',
            hole=0.5,
            title='Risk Level Distribution',
            color='Risk Level',
            color_discrete_map=risk_colors
        )
        fig1.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color=t["subtext"],
            title_font_color=t["accent2"],
            title_font_size=16,
            margin=dict(l=0, r=0, t=40, b=0),
        )
        st.plotly_chart(fig1, use_container_width=True)
        
    with col2:
        top_files = df.groupby('Filename')['Issue Count'].sum().reset_index()
        top_files = top_files.sort_values(by='Issue Count', ascending=True).tail(12)
        
        fig2 = px.bar(
            top_files,
            x='Issue Count',
            y='Filename',
            orientation='h',
            title='Top 12 Files by Issues',
            color='Issue Count',
            color_continuous_scale=[t["accent3"], t["accent1"]]
        )
        fig2.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color=t["subtext"],
            title_font_color=t["accent2"],
            title_font_size=16,
            margin=dict(l=0, r=0, t=40, b=0),
            coloraxis_showscale=False
        )
        border_hex = t["border"].lstrip('#')
        border_rgba = f"rgba({int(border_hex[0:2], 16)}, {int(border_hex[2:4], 16)}, {int(border_hex[4:6], 16)}, 0.27)"
        fig2.update_xaxes(showgrid=True, gridcolor=border_rgba, title="")
        fig2.update_yaxes(showgrid=False, title="")
        st.plotly_chart(fig2, use_container_width=True)


# ─────────────────────────────────────────────
# PAGE: HISTORY
# ─────────────────────────────────────────────
def show_history():
    st.header('🕐 Migration History')
    rows = fetch_history()
    if not rows:
        st.info('No records yet.')
        return
    df = pd.DataFrame(rows, columns=['ID', 'Filename', 'Issue Count', 'Risk Score', 'Risk Level', 'Created At'])
    st.dataframe(df, use_container_width=True)

    selected_id = st.selectbox('Select record ID to view details', df['ID'].tolist())
    record = fetch_full_record(int(selected_id))
    if record:
        st.subheader(f'Record Details: {record[1]}')
        left, right = st.columns(2)
        with left:
            st.caption('Original Code')
            st.code(record[2], language='python')
        with right:
            st.caption('Migrated Code')
            st.code(record[3], language='python')
        st.write('Suggestions:')
        st.text(record[7])


# ─────────────────────────────────────────────
# PAGE: ML TRAINING
# ─────────────────────────────────────────────
def show_ml_training():
    st.header('🤖 ML Risk Model')
    st.write('This page trains a sample Scikit-learn RandomForest model for migration risk prediction.')
    if st.button('🚀 Train / Retrain Risk Model'):
        import importlib
        import sys
        if 'modules.risk_model' in sys.modules:
            importlib.reload(sys.modules['modules.risk_model'])
        from modules.risk_model import train_model
        with st.spinner('Training model...'):
            model, metrics = train_model()
        st.success('Model trained successfully.')
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric('Accuracy', f"{round(metrics['accuracy'] * 100, 1)}%")
            st.write('**Confusion Matrix**')
            cm_df = pd.DataFrame(metrics['confusion_matrix'], columns=['Low', 'Medium', 'High'], index=['Low', 'Medium', 'High'])
            st.dataframe(cm_df, use_container_width=True)
            
        with col2:
            st.write('**Confusion Matrix Heatmap**')
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.heatmap(metrics['confusion_matrix'], annot=True, fmt='d', cmap='Blues',
                        xticklabels=['Low', 'Medium', 'High'], yticklabels=['Low', 'Medium', 'High'], ax=ax)
            ax.set_xlabel('Predicted')
            ax.set_ylabel('Actual')
            style_fig(fig, ax)
            st.pyplot(fig)
            
        st.markdown("---")
        st.subheader("📊 Model Feature Importance")
        
        # Get feature importances from the model
        features = ['total_lines', 'issue_count', 'functions', 'classes', 'imports']
        importances = model.feature_importances_
        feat_df = pd.DataFrame({'Feature': features, 'Importance': importances}).sort_values('Importance', ascending=True)
        
        fig2 = px.bar(
            feat_df, x='Importance', y='Feature', orientation='h', 
            title='Feature Importance in Risk Prediction',
            color='Importance',
            color_continuous_scale=[t["accent3"], t["accent1"]]
        )
        fig2.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color=t["subtext"],
            title_font_color=t["accent2"],
            title_font_size=16,
            coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        fig2.update_xaxes(showgrid=True, gridcolor=f"rgba(128,128,128,0.2)", title="Importance")
        fig2.update_yaxes(showgrid=False, title="")
        st.plotly_chart(fig2, use_container_width=True)


# ─────────────────────────────────────────────
# PAGE: ADVANCED ANALYSIS CENTER
# ─────────────────────────────────────────────
def show_analysis_center():
    st.header('🔬 Advanced Analysis Center')
    st.write('Inspect deprecated patterns, dependency risks, code smells, syntax/runtime issues, and security findings.')

    sample_adv_codes = {
        "Blank (Type your own)": "",
        "Python (Deprecated Syntax + Security)": "import md5\nimport urllib2\n\npwd = 'supersecretpassword'\n\ndef fetch_data(url):\n    req = urllib2.urlopen(url)\n    return req.read()\n\neval(\"print('Executing unsafe string...')\")",
        "JavaScript (Hardcoded Secrets + Unsafe Eval)": "const API_KEY = 'AIzaSyA_1234567890abcdef';\n\nfunction processData(userInput) {\n    var data = eval('(' + userInput + ')');\n    console.log(data);\n}",
        "SQL (Injection Example)": "SELECT * FROM users WHERE username = '\" + username + \"' AND password = '\" + pwd + \"';\nDROP TABLE test_users;"
    }
    
    def on_adv_sample_change():
        sel = st.session_state.get('adv_sample_select')
        if sel and sel in sample_adv_codes:
            st.session_state['adv_code_area'] = sample_adv_codes[sel]
            
    st.selectbox("💡 Need an example? Load a legacy snippet:", list(sample_adv_codes.keys()), key='adv_sample_select', on_change=on_adv_sample_change)
    
    if 'adv_code_area' not in st.session_state:
        st.session_state['adv_code_area'] = ""

    code = st.text_area('Paste code to analyze', key='adv_code_area', height=220)

    def on_adv_analyze_click():
        st.session_state['run_advanced_analysis'] = True
        st.session_state['adv_code_content'] = st.session_state.get('adv_code_area')
        
    st.button('▶ Run analysis on pasted code', on_click=on_adv_analyze_click)
        
    if st.session_state.get('run_advanced_analysis') and st.session_state.get('adv_code_content', '').strip():
        with st.spinner('Running full analysis pipeline...'):
            result = run_migration_workflow(st.session_state['adv_code_content'], filename='pasted_analysis.py')
        findings_df  = result['findings_df']
        security_df  = result['security_findings_df']
        dependency_df = pd.DataFrame(result.get('dependency_findings', []))

        c1, c2, c3, c4 = st.columns(4)
        c1.metric('Detected language', result.get('language', 'Unknown'))
        c2.metric('Migration target', result.get('migration_target', 'Modern equivalent'))
        c3.metric('Deprecated findings', len(findings_df) if findings_df is not None else 0)
        c4.metric('Security findings', len(security_df) if security_df is not None else 0)

        st.subheader('⚡ Code Quality & Runtime Risk Signals')
        st.write('Unused helpers:', ', '.join(result.get('unused_functions', [])) if result.get('unused_functions') else 'None detected')
        st.write('Runtime risks:')
        for item in result.get('runtime_risks', []):
            st.warning(item)
        if result.get('syntax_error'):
            st.error(f"Syntax check issue on line {result['syntax_error']['line']}: {result['syntax_error']['message']}")

        st.subheader('📦 Dependency Modernization Hints')
        if dependency_df.empty:
            st.info('No obvious dependency modernization hints were found.')
        else:
            st.dataframe(dependency_df[['library', 'status', 'replacement', 'line']], use_container_width=True)

        st.subheader('🛡️ Security Findings')
        if security_df is None or security_df.empty:
            st.success('No static security findings detected.')
        else:
            st.dataframe(security_df, use_container_width=True)

        st.subheader('🗺️ Migration Roadmap')
        st.text(result.get('roadmap_text', ''))
    elif not st.session_state.get('adv_code_content', '').strip():
        st.info('Paste some code above to run the analysis pipeline.')


# ─────────────────────────────────────────────
# ROUTER
# ─────────────────────────────────────────────
if page == "🏠 Home":
    show_home()
elif page == "📤 Upload & Migrate":
    show_upload_migrate()
elif page == "🔬 Advanced Analysis Center":
    show_analysis_center()
elif page == "📊 Analytics Dashboard":
    show_analytics()
elif page == "🕐 Migration History":
    show_history()
elif page == "🤖 ML Risk Model":
    show_ml_training()
elif page == "⚙️ Settings":
    st.header("⚙️ Settings")
    st.info('Use **API Key Manager** to configure model provider keys.')
    
    st.markdown("---")
    st.subheader("🛠️ System Maintenance")
    st.write("If the application becomes unresponsive, holds onto outdated analysis, or acts unpredictably, you can forcefully clear its memory. This will reset your active session but keep your API keys and history intact.")
    
    def on_clear_cache():
        st.cache_data.clear()
        # Keep API keys and theme if possible, clear temporary analysis data
        keys_to_keep = ['current_page', 'nav_radio', 'auto_color_toggle', 'theme_select']
        for k in list(st.session_state.keys()):
            if k not in keys_to_keep and not k.startswith('api_'):
                del st.session_state[k]
                
    if st.button("🗑️ Clear Application Cache & Session State"):
        on_clear_cache()
        st.success("Cache and temporary session state cleared successfully!")
        st.rerun()
elif page == "🔑 API Key Manager":
    render_api_key_manager_page()
