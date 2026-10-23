"""
Input validation and security utility functions.
Handles password hashing, phone validation, email checks, and code generation.
"""

import re
import secrets
import bcrypt
from typing import Tuple


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def validate_phone(phone: str) -> Tuple[bool, str]:
    """Validate standard 10-digit Indian phone number format."""
    clean_phone = re.sub(r"\D", "", phone)
    if len(clean_phone) == 10 and clean_phone[0] in "6789":
        return True, clean_phone
    if len(clean_phone) == 12 and clean_phone.startswith("91") and clean_phone[2] in "6789":
        return True, clean_phone[2:]
    return False, "Phone must be a valid 10-digit mobile number."


def validate_email(email: str) -> Tuple[bool, str]:
    """Validate email address format."""
    if not email:
        return True, ""  # Optional field
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if re.match(pattern, email.strip()):
        return True, ""
    return False, "Invalid email address format."


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """Ensure password has minimum required length."""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    return True, ""


def generate_code(prefix: str, sequence_num: int, padding: int = 4) -> str:
    """
    Generate clean readable system codes.
    Example: prefix='GLZ-CUS', sequence_num=1 -> 'GLZ-CUS-0001'
    """
    return f"{prefix}-{str(sequence_num).zfill(padding)}"