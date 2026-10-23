"""
Customer registration UI screen for GL Orenza Salon Ahmedabad.
"""

import streamlit as st
from modules.customers import register_customer


def render_customer_register_form():
    """Render customer registration form."""
    st.markdown("### Customer Registration")
    st.caption("Create your account to schedule appointments and track salon visits.")

    with st.form("customer_reg_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full Name *", placeholder="e.g. Pooja Patel")
            phone = st.text_input("Mobile Number (10 digits) *", placeholder="e.g. 9825012345")
            gender = st.selectbox("Gender", ["Unspecified", "Female", "Male", "Other"])
        with col2:
            email = st.text_input("Email (Optional)", placeholder="e.g. pooja@example.com")
            password = st.text_input("Create Password *", type="password", help="Minimum 6 characters")
            confirm_pwd = st.text_input("Confirm Password *", type="password")

        address = st.text_area("Address / Area (Optional)", placeholder="e.g. Navrangpura, Ahmedabad")
        
        submitted = st.form_submit_button("Create Account", use_container_width=True)

        if submitted:
            if not full_name.strip() or not phone.strip() or not password:
                st.error("Please fill in all mandatory fields (*).")
                return

            if password != confirm_pwd:
                st.error("Passwords do not match. Please try again.")
                return

            success, msg, data = register_customer(
                full_name=full_name,
                phone=phone,
                password=password,
                email=email,
                gender=gender,
                address=address
            )

            if success:
                st.success(msg)
                st.info("You can now click **Back to Login** and sign in using your mobile number and password.")
            else:
                st.error(msg)