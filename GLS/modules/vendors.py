"""
Vendor management module for GL Orenza Salon Ahmedabad.
"""

from typing import Optional, Dict, Any, List, Tuple
from database.connection import fetch_one, fetch_all, execute_query
from utils.validators import generate_code, validate_phone


def get_next_vendor_code() -> str:
    """Generate sequential vendor code: GLZ-VND-0001"""
    row = fetch_one("SELECT COUNT(*) as total FROM vendors;")
    count = (row["total"] if row else 0) + 1
    return generate_code("GLZ-VND", count, padding=4)


def add_vendor(
    vendor_name: str,
    phone: str,
    contact_person: Optional[str] = None,
    email: Optional[str] = None,
    address: Optional[str] = None,
    gst_number: Optional[str] = None,
    notes: Optional[str] = None
) -> Tuple[bool, str, Optional[int]]:
    """Create a new vendor profile."""
    if not vendor_name.strip():
        return False, "Vendor name is required.", None

    is_valid_phone, clean_phone = validate_phone(phone)
    if not is_valid_phone:
        return False, clean_phone, None

    code = get_next_vendor_code()
    try:
        vendor_id = execute_query(
            """
            INSERT INTO vendors (vendor_code, vendor_name, contact_person, phone, email, address, gst_number, notes, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active');
            """,
            (code, vendor_name.strip(), contact_person, clean_phone, email, address, gst_number, notes)
        )
        return True, f"Vendor '{vendor_name}' added successfully ({code}).", vendor_id
    except Exception as e:
        return False, f"Failed to add vendor: {str(e)}", None


def get_all_vendors(active_only: bool = True) -> List[Dict[str, Any]]:
    """Retrieve list of vendors."""
    sql = "SELECT * FROM vendors"
    if active_only:
        sql += " WHERE status = 'active'"
    sql += " ORDER BY vendor_name ASC;"
    return fetch_all(sql)