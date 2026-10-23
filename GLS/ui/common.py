"""
GLORENZA SALON AHMEDABAD - Master Global Design & Theme Engine
Protects all Material Icon glyphs and prevents text overlaps on expanders.
"""

import streamlit as st


def apply_custom_css():
    css_content = """
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800;900&display=swap');

    html, body, .stApp {
        font-family: 'Montserrat', sans-serif !important;
        color-scheme: light !important;
        background-color: #FFFFFF !important;
        color: #111111 !important;
    }

    [data-testid="stStatusWidget"], #MainMenu, footer {
        display: none !important;
    }
    header[data-testid="stHeader"] {
        background: transparent !important;
        z-index: 9999 !important;
    }
    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 95% !important;
    }

    /* FIX MATERIAL ICONS & EXPANDER ARROW OVERLAP */
    [data-testid="stExpander"] summary svg,
    [data-testid="stExpanderToggleIcon"],
    .material-icons,
    .material-symbols-rounded,
    .material-symbols-outlined,
    [data-testid="stSidebarCollapseButton"] svg {
        font-family: inherit !important;
    }
    [data-testid="stExpander"] summary span:first-child {
        font-size: 0px !important;
        color: transparent !important;
    }
    [data-testid="stExpander"] summary span:first-child::before {
        content: "▼ " !important;
        font-size: 13px !important;
        color: #C2185B !important;
        display: inline-block !important;
        margin-right: 4px !important;
    }

    /* Brand Header */
    .gl-brand-container {
        text-align: center;
        padding: 4px 0 10px 0;
        border-bottom: 2px solid #111111;
        margin-bottom: 16px;
    }
    .gl-brand-logo {
        font-size: 32px;
        font-weight: 800;
        letter-spacing: 6px;
        margin: 0;
        color: #000000;
        text-transform: uppercase;
    }
    .gl-brand-logo .accent {
        color: #C2185B !important;
    }
    .gl-brand-sub {
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 5px;
        color: #666666;
        margin-top: 3px;
        text-transform: uppercase;
    }

    /* Luxury Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #880E4F 0%, #C2185B 65%, #AD1457 100%) !important;
        border-right: none !important;
        padding-top: 1rem !important;
    }
    section[data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    .sidebar-brand-title {
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 2.5px;
        color: #FFFFFF !important;
        text-transform: uppercase;
        padding: 4px 8px 8px 8px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.25);
        margin-bottom: 12px;
    }
    section[data-testid="stSidebar"] .stButton > button {
        background-color: rgba(255, 255, 255, 0.15) !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        border-radius: 6px !important;
        color: #FFFFFF !important;
        text-align: left !important;
        justify-content: flex-start !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        padding: 9px 12px !important;
        margin-bottom: 4px !important;
        width: 100% !important;
        box-shadow: none !important;
    }
    section[data-testid="stSidebar"] .stButton > button p,
    section[data-testid="stSidebar"] .stButton > button span {
        color: #FFFFFF !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        font-family: 'Montserrat', sans-serif !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background-color: #FFFFFF !important;
        border-color: #FFFFFF !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover p,
    section[data-testid="stSidebar"] .stButton > button:hover span {
        color: #C2185B !important;
        font-weight: 700 !important;
    }

    /* Solid Michanta Buttons */
    .main button,
    .main .stButton > button,
    .main div[data-testid="stButton"] > button,
    .main div[data-testid="stFormSubmitButton"] > button,
    button[kind="primary"],
    button[kind="secondary"],
    div[data-testid="stFormSubmitButton"] button {
        background-color: #C2185B !important;
        background: #C2185B !important;
        border: 1px solid #AD1457 !important;
        border-radius: 6px !important;
        padding: 10px 18px !important;
        width: 100% !important;
        box-shadow: 0 2px 5px rgba(194, 24, 91, 0.28) !important;
        cursor: pointer !important;
        color: #FFFFFF !important;
    }
    .main button *,
    .main .stButton > button *,
    .main div[data-testid="stButton"] > button *,
    .main div[data-testid="stFormSubmitButton"] > button *,
    button[kind="primary"] *,
    button[kind="secondary"] *,
    div[data-testid="stFormSubmitButton"] button * {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        font-family: 'Montserrat', sans-serif !important;
        background: transparent !important;
    }
    .main button:hover,
    .main .stButton > button:hover,
    .main div[data-testid="stButton"] > button:hover,
    .main div[data-testid="stFormSubmitButton"] > button:hover {
        background-color: #880E4F !important;
        background: #880E4F !important;
        border-color: #880E4F !important;
    }

    /* Clean White Inputs */
    label[data-testid="stWidgetLabel"] p {
        font-size: 13px !important;
        font-weight: 700 !important;
        color: #111111 !important;
        margin-bottom: 4px !important;
        font-family: 'Montserrat', sans-serif !important;
    }
    div[data-baseweb="input"],
    div[data-baseweb="select"],
    div[data-baseweb="textarea"],
    div[data-testid="stDateInput"] div[data-baseweb="input"],
    div[data-testid="stDateInput"] input {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
        border: 1.5px solid #D1D5DB !important;
        border-radius: 6px !important;
        color: #111111 !important;
    }
    div[data-baseweb="input"]:focus-within,
    div[data-baseweb="select"]:focus-within {
        border-color: #C2185B !important;
        box-shadow: 0 0 0 1px #C2185B !important;
    }
    input, select, textarea {
        color: #111111 !important;
        background-color: #FFFFFF !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        font-family: 'Montserrat', sans-serif !important;
    }
    input::placeholder, textarea::placeholder {
        color: #757575 !important;
        font-weight: 400 !important;
    }

    /* Expanders */
    div[data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: 1.5px solid #F8BBD0 !important;
        border-radius: 8px !important;
        margin-bottom: 10px !important;
    }
    div[data-testid="stExpander"] summary {
        background-color: #FFF5F8 !important;
        border-radius: 6px !important;
        color: #C2185B !important;
        font-weight: 700 !important;
        padding: 10px 14px !important;
    }
    div[data-testid="stExpander"] summary p,
    div[data-testid="stExpander"] summary span {
        color: #C2185B !important;
        font-weight: 700 !important;
        font-family: 'Montserrat', sans-serif !important;
    }

    /* KPI Cards */
    .kpi-row-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin: 12px 0 18px 0;
        width: 100%;
    }
    .kpi-single-card {
        background: #FFFFFF;
        border: 1.5px solid #EBEBEB;
        border-left: 5px solid #C2185B;
        border-radius: 6px;
        padding: 12px 14px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.04);
    }
    .kpi-single-card .card-title {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        color: #555555;
        margin-bottom: 4px;
    }
    .kpi-single-card .card-value {
        font-size: 22px;
        font-weight: 800;
        color: #C2185B;
        margin: 0;
    }
    """
    st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)


def render_header():
    apply_custom_css()
    st.markdown(
        """
        <div class="gl-brand-container">
            <div class="gl-brand-logo">GL<span class="accent">O</span>RENZA</div>
            <div class="gl-brand-sub">SALON &bull; AHMEDABAD</div>
        </div>
        """,
        unsafe_allow_html=True
    )