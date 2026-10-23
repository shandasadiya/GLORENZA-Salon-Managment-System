"""
Customer management module for GL Orenza Salon Ahmedabad.
Handles customer registration, profiles, codes, and segmentation.
"""

from typing import Optional, Dict, Any, List, Tuple
from database.connection import get_db_connection, fetch_one, fetch_all, execute_query
from utils.validators import hash_password, validate_phone, validate_email, validate_password_strength, generate_code


def get_next_customer_code() -> str:
    """Generate the next sequential customer identifier: GLZ-CUS-0001, GLZ-CUS-0002..."""
    row = fetch_one("SELECT COUNT(*) as total FROM customers;")
    count = (row["total"] if row else 0) + 1
    return generate_code("GLZ-CUS", count, padding=4)


def register_customer(
    full_name: str,
    phone: str,
    password: str,
    email: Optional[str] = None,
    gender: str = "Unspecified",
    address: Optional[str] = None
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Register a new customer with a unified database transaction.
    Creates user login and customer profile simultaneously.
    """
    # 1. Validation
    is_valid_phone, clean_phone = validate_phone(phone)
    if not is_valid_phone:
        return False, clean_phone, None

    is_valid_pwd, pwd_msg = validate_password_strength(password)
    if not is_valid_pwd:
        return False, pwd_msg, None

    if email:
        is_valid_email, email_msg = validate_email(email)
        if not is_valid_email:
            return False, email_msg, None

    # 2. Check for duplicate phone or username
    existing_user = fetch_one("SELECT id FROM users WHERE phone = ? OR username = ?;", (clean_phone, clean_phone))
    if existing_user:
        return False, "An account with this mobile number already exists. Please login.", None

    pwd_hash = hash_password(password)
    customer_code = get_next_customer_code()

    # 3. Transaction Execution
    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()
            # Insert into users table
            cursor.execute(
                """
                INSERT INTO users (username, password_hash, role, full_name, phone, email, status)
                VALUES (?, ?, 'customer', ?, ?, ?, 'active');
                """,
                (clean_phone, pwd_hash, full_name.strip(), clean_phone, email.strip().lower() if email else None)
            )
            user_id = cursor.lastrowid

            # Insert into customers table
            cursor.execute(
                """
                INSERT INTO customers (user_id, customer_code, full_name, phone, email, gender, address, customer_type, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'New', 1);
                """,
                (user_id, customer_code, full_name.strip(), clean_phone, email.strip().lower() if email else None, gender, address)
            )
            customer_db_id = cursor.lastrowid

            return True, f"Registration successful! Your Customer ID is {customer_code}", {
                "user_id": user_id,
                "customer_id": customer_db_id,
                "customer_code": customer_code,
                "full_name": full_name.strip(),
                "phone": clean_phone
            }
    except Exception as e:
        return False, f"Registration failed: {str(e)}", None
    finally:
        conn.close()


def get_customer_by_user_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Fetch complete customer profile by linked user ID."""
    return fetch_one("SELECT * FROM customers WHERE user_id = ?;", (user_id,))


def get_all_customers(search_query: Optional[str] = None, customer_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve filtered list of customers for owner/staff directory."""
    sql = "SELECT * FROM customers WHERE 1=1"
    params: List[Any] = []

    if customer_type and customer_type != "All":
        sql += " AND customer_type = ?"
        params.append(customer_type)

    if search_query:
        sql += " AND (full_name LIKE ? OR phone LIKE ? OR customer_code LIKE ?)"
        term = f"%{search_query.strip()}%"
        params.extend([term, term, term])

    sql += " ORDER BY id DESC;"
    return fetch_all(sql, tuple(params))