"""
GLORENZA SALON AHMEDABAD — Master Web Application Entry Point.
Initializes schema and seed dataset, manages session routing, and renders luxury layout.
"""

import streamlit as st
from database.schema import init_database
from database.seed import seed_database
from modules.session import init_session, is_logged_in, get_current_role
from ui.login import render_login_page
from panels.customer_panel import render_customer_panel
from panels.staff_panel import render_staff_panel
from panels.owner_panel import render_owner_panel

# 1. Streamlit Application Configuration
st.set_page_config(
    page_title="GLORENZA SALON AHMEDABAD",
    page_icon="✂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Initialize Database & Seed Master Data
init_database()
seed_database()
init_session()

# 3. Portal Routing
if not is_logged_in():
    render_login_page()
else:
    role = get_current_role()
    if role == "customer":
        render_customer_panel()
    elif role == "staff":
        render_staff_panel()
    elif role == "owner":
        render_owner_panel()
    else:
        st.session_state.clear()
        st.rerun()