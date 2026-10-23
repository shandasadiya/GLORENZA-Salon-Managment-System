"""
Authentication module for GL Orenza Salon Ahmedabad.
Handles login verification, role validation, registration, and first-time owner setup.
"""

from typing import Optional, Dict, Any, Tuple
from database.connection import fetch_one, execute_query, get_db_connection
from utils.validators import hash_password, verify_password, validate_phone, validate_email, validate_password_strength


def is_first_time_setup() -> bool:
    """Check whether an owner account already exists in the system."""
    row = fetch_one("SELECT COUNT(*) as count FROM users WHERE role = 'owner' AND status = 'active';")
    return (row["count"] == 0) if row else True


def authenticate_user(identifier: str, password: str, required_role: Optional[str] = None) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Authenticate a user by username or phone number.
    Validates role, status, and password hash.
    """
    identifier_clean = identifier.strip()
    
    # Query user by either username or phone
    query = """
        SELECT id, username, password_hash, role, full_name, phone, email, status
        FROM users
        WHERE (username = ? OR phone = ?);
    """
    user = fetch_one(query, (identifier_clean, identifier_clean))
    
    if not user:
        return False, "Invalid username/phone or password.", None
    
    if user["status"] != "active":
        return False, f"Account is {user['status']}. Please contact salon administration.", None
    
    if required_role and user["role"] != required_role:
        return False, f"Access restricted. Account is not authorized for {required_role.upper()} portal.", None
    
    if not verify_password(password, user["password_hash"]):
        return False, "Invalid username/phone or password.", None
    
    # Update last login timestamp
    execute_query("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?;", (user["id"],))
    
    return True, "Login successful.", user


def setup_first_owner(full_name: str, username: str, phone: str, email: str, password: str) -> Tuple[bool, str]:
    """
    Initialize the primary salon owner account during first startup.
    Disabled permanently once an owner exists.
    """
    if not is_first_time_setup():
        return False, "Owner account is already configured. Public setup is disabled."
    
    # Validations
    is_valid_phone, phone_msg = validate_phone(phone)
    if not is_valid_phone:
        return False, phone_msg
    
    is_valid_pwd, pwd_msg = validate_password_strength(password)
    if not is_valid_pwd:
        return False, pwd_msg
    
    pwd_hash = hash_password(password)
    
    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO users (username, password_hash, role, full_name, phone, email, status)
                VALUES (?, ?, 'owner', ?, ?, ?, 'active');
                """,
                (username.strip().lower(), pwd_hash, full_name.strip(), phone_msg, email.strip().lower() if email else None)
            )
            cursor.execute("UPDATE system_info SET is_setup_completed = 1 WHERE id = 1;")
            return True, "Owner account successfully configured."
    except Exception as e:
        return False, f"Setup error: {str(e)}"
    finally:
        conn.close()