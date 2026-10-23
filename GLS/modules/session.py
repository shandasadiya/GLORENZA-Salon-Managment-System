"""
Session state manager for Streamlit interface.
Provides role isolation, logged-in status checks, and clean session cleanup.
"""

import streamlit as st
from typing import Optional, Dict, Any


def init_session() -> None:
    """Initialize default session state keys if not already present."""
    defaults = {
        "is_authenticated": False,
        "user_id": None,
        "username": None,
        "full_name": None,
        "role": None,
        "phone": None,
        "email": None,
        "customer_id": None,
        "customer_code": None,
        "staff_id": None,
        "staff_code": None,
        "active_view": "dashboard"
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def login_user(user: Dict[str, Any], extra_data: Optional[Dict[str, Any]] = None) -> None:
    """Populate active session state with authenticated user profile."""
    init_session()
    st.session_state.is_authenticated = True
    st.session_state.user_id = user.get("id")
    st.session_state.username = user.get("username")
    st.session_state.full_name = user.get("full_name")
    st.session_state.role = user.get("role")
    st.session_state.phone = user.get("phone")
    st.session_state.email = user.get("email")

    if extra_data:
        for k, v in extra_data.items():
            st.session_state[k] = v


def logout_user() -> None:
    """Clear active user session state completely."""
    st.session_state.clear()
    init_session()


def is_logged_in() -> bool:
    """Check if a valid active session exists."""
    return st.session_state.get("is_authenticated", False)


def get_current_user() -> Dict[str, Any]:
    """Retrieve basic active user metadata from session."""
    return {
        "user_id": st.session_state.get("user_id"),
        "username": st.session_state.get("username"),
        "full_name": st.session_state.get("full_name"),
        "role": st.session_state.get("role"),
        "phone": st.session_state.get("phone"),
        "email": st.session_state.get("email"),
    }


def get_current_role() -> Optional[str]:
    """Return active user role: 'owner', 'staff', or 'customer'."""
    return st.session_state.get("role")