"""
Authentication and validation test runner.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from utils.validators import hash_password, verify_password, validate_phone
from modules.auth import is_first_time_setup, setup_first_owner, authenticate_user
from database.schema import init_database


def run_test():
    print("Testing Security & Auth Module...")
    init_database()

    # 1. Test Password Hashing
    pwd = "SalonAdmin@2026"
    hashed = hash_password(pwd)
    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongPassword", hashed) is False
    print("Password hashing & verification working.")

    # 2. Test Phone Validation
    valid, res = validate_phone("9876543210")
    assert valid is True and res == "9876543210"
    print("Phone validator working.")

    # 3. Test First-time setup check
    print(f"Is first time setup required? {is_first_time_setup()}")

    print("\nSecurity & Auth test passed successfully.")


if __name__ == "__main__":
    run_test()
    