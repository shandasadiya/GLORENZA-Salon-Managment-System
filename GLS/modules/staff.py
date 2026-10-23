"""
Staff management module for GL Orenza Salon Ahmedabad.
Handles staff creation, code generation, service specialization, and status.
"""

from typing import Optional, Dict, Any, List, Tuple
from database.connection import get_db_connection, fetch_one, fetch_all, execute_query
from utils.validators import hash_password, validate_phone, validate_email, validate_password_strength, generate_code


def get_next_staff_code() -> str:
    """Generate next sequential staff identifier: GLZ-STF-0001, GLZ-STF-0002..."""
    row = fetch_one("SELECT COUNT(*) as total FROM staff;")
    count = (row["total"] if row else 0) + 1
    return generate_code("GLZ-STF", count, padding=4)


def create_staff_member(
    full_name: str,
    phone: str,
    password: str,
    role: str = "Stylist",
    specialization: Optional[str] = None,
    experience_years: int = 0,
    salary: float = 0.0,
    daily_target: float = 0.0,
    service_commission: float = 10.0,
    product_commission: float = 5.0,
    email: Optional[str] = None
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Create a new staff member profile and associated login account (Controlled by Owner).
    """
    # 1. Validation
    is_valid_phone, clean_phone = validate_phone(phone)
    if not is_valid_phone:
        return False, clean_phone, None

    is_valid_pwd, pwd_msg = validate_password_strength(password)
    if not is_valid_pwd:
        return False, pwd_msg, None

    existing = fetch_one("SELECT id FROM users WHERE phone = ?;", (clean_phone,))
    if existing:
        return False, "A user account with this mobile number already exists.", None

    pwd_hash = hash_password(password)
    staff_code = get_next_staff_code()

    # 2. Transaction Execution
    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()
            # Create user account with staff role
            cursor.execute(
                """
                INSERT INTO users (username, password_hash, role, full_name, phone, email, status)
                VALUES (?, ?, 'staff', ?, ?, ?, 'active');
                """,
                (clean_phone, pwd_hash, full_name.strip(), clean_phone, email.strip().lower() if email else None)
            )
            user_id = cursor.lastrowid

            # Create staff profile
            cursor.execute(
                """
                INSERT INTO staff (
                    user_id, staff_code, full_name, phone, email, role, specialization,
                    experience_years, salary, daily_target, service_commission_percent,
                    product_commission_percent, status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active');
                """,
                (
                    user_id, staff_code, full_name.strip(), clean_phone,
                    email.strip().lower() if email else None, role, specialization,
                    experience_years, salary, daily_target, service_commission,
                    product_commission
                )
            )
            staff_db_id = cursor.lastrowid

            return True, f"Staff created successfully with ID: {staff_code}", {
                "staff_id": staff_db_id,
                "staff_code": staff_code,
                "full_name": full_name.strip()
            }
    except Exception as e:
        return False, f"Staff creation failed: {str(e)}", None
    finally:
        conn.close()


def get_staff_by_user_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Fetch complete staff profile by linked user ID."""
    return fetch_one("SELECT * FROM staff WHERE user_id = ?;", (user_id,))


def get_all_staff(status_filter: Optional[str] = "active") -> List[Dict[str, Any]]:
    """Retrieve staff members optionally filtered by active status."""
    if status_filter:
        return fetch_all("SELECT * FROM staff WHERE status = ? ORDER BY full_name ASC;", (status_filter,))
    return fetch_all("SELECT * FROM staff ORDER BY id DESC;")