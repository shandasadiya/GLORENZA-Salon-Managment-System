"""
GLORENZA SALON AHMEDABAD - Master Authentication & Portal Switcher
Zero-latency role selection, solid Michanta styling, and session management.
"""

import streamlit as st
from modules.auth import is_first_time_setup, setup_first_owner, authenticate_user
from modules.session import login_user
from modules.customers import get_customer_by_user_id
from modules.staff import get_staff_by_user_id
from ui.common import render_header
from ui.register import render_customer_register_form


def render_login_page():
    render_header()

    # 1. First Time System Installation Check
    if is_first_time_setup():
        st.info("Initial salon setup required. Please configure the primary Owner administrator account.")
        with st.form("first_time_setup_form"):
            full_name = st.text_input("Full Name *", placeholder="Enter owner full name")
            col1, col2 = st.columns(2)
            with col1:
                username = st.text_input("Username / Login ID *", placeholder="e.g. owner")
                phone = st.text_input("Mobile Number *", placeholder="10-digit mobile number")
            with col2:
                email = st.text_input("Email Address", placeholder="e.g. owner@glorenza.com")
                password = st.text_input("Create Password *", type="password", placeholder="Minimum 6 characters")

            confirm = st.text_input("Confirm Password *", type="password", placeholder="Re-enter password")
            submitted = st.form_submit_button("COMPLETE SETUP & CREATE OWNER ACCOUNT", use_container_width=True)

            if submitted:
                if not full_name.strip() or not username.strip() or not phone.strip() or not password:
                    st.error("Please fill all required fields.")
                    return
                if password != confirm:
                    st.error("Passwords do not match.")
                    return
                success, msg = setup_first_owner(full_name.strip(), username.strip(), phone.strip(), email.strip(), password)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
        return

    # 2. Session Role State Initialization
    if "selected_role" not in st.session_state:
        st.session_state.selected_role = "owner"
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"

    st.markdown(
        "<p style='text-align:center; font-size:12px; font-weight:800; letter-spacing:2px; color:#555555; margin-bottom:12px; text-transform:uppercase;'>SELECT ACCESS PORTAL</p>",
        unsafe_allow_html=True
    )

    # 3. 3-Button Portal Selector with Active Highlight
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("👑 OWNER PORTAL", key="btn_portal_owner", use_container_width=True):
            st.session_state.selected_role = "owner"
            st.session_state.auth_mode = "login"
            st.rerun()
    with col2:
        if st.button("✂️ STAFF PORTAL", key="btn_portal_staff", use_container_width=True):
            st.session_state.selected_role = "staff"
            st.session_state.auth_mode = "login"
            st.rerun()
    with col3:
        if st.button("✨ CLIENT PORTAL", key="btn_portal_cust", use_container_width=True):
            st.session_state.selected_role = "customer"
            st.session_state.auth_mode = "login"
            st.rerun()

    active_role = st.session_state.selected_role

    st.markdown(
        f"""
        <div style="text-align:center; margin:16px 0 12px 0;">
            <span style="font-size:16px; font-weight:800; color:#C2185B; letter-spacing:1.5px; border-bottom:2px solid #C2185B; padding-bottom:4px;">
                {active_role.upper()} AUTHENTICATION
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 4. Client Sub-Navigation (Sign In vs Register)
    if active_role == "customer":
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔑 Sign In Existing Account", key="btn_cust_mode_login", use_container_width=True):
                st.session_state.auth_mode = "login"
                st.rerun()
        with c2:
            if st.button("📝 Register New Account", key="btn_cust_mode_reg", use_container_width=True):
                st.session_state.auth_mode = "register"
                st.rerun()

    # 5. Form Execution Block
    if active_role == "customer" and st.session_state.auth_mode == "register":
        render_customer_register_form()
    else:
        label = "Username or Registered Mobile" if active_role == "owner" else "Registered 10-Digit Mobile Number"
        placeholder_text = "Enter username or 10-digit mobile (e.g. owner)" if active_role == "owner" else "e.g. 9825012345"

        with st.form(f"{active_role}_login_form"):
            identifier = st.text_input(label, placeholder=placeholder_text)
            password = st.text_input("Password", type="password", placeholder="Enter account password")
            submit_btn = st.form_submit_button(f"SIGN IN TO {active_role.upper()} ACCOUNT", use_container_width=True)

            if submit_btn:
                if not identifier.strip() or not password:
                    st.error("Please enter both login identifier and password.")
                    return

                success, msg, user = authenticate_user(identifier.strip(), password, required_role=active_role)
                if not success or not user:
                    st.error(msg)
                    return

                extra_data = {}
                if active_role == "customer":
                    cust = get_customer_by_user_id(user["id"])
                    if cust:
                        extra_data["customer_id"] = cust["id"]
                        extra_data["customer_code"] = cust["customer_code"]
                elif active_role == "staff":
                    stf = get_staff_by_user_id(user["id"])
                    if stf:
                        extra_data["staff_id"] = stf["id"]
                        extra_data["staff_code"] = stf["staff_code"]

                login_user(user, extra_data)
                st.rerun()