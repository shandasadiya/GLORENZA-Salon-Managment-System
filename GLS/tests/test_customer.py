"""
Customer registration and query verification test.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from modules.customers import register_customer, get_all_customers
from database.schema import init_database


def run_test():
    print("Testing Customer Registration & Retrieval...")
    init_database()

    # Attempt customer registration
    success, msg, data = register_customer(
        full_name="Pooja Patel",
        phone="9825012345",
        password="CustomerPass123",
        email="pooja@example.com",
        gender="Female",
        address="Navrangpura, Ahmedabad"
    )

    print(f"Registration Result: {msg}")
    assert success is True or "already exists" in msg

    customers = get_all_customers()
    print(f"Total customers in database: {len(customers)}")
    print("Customer module passed successfully.\n")


if __name__ == "__main__":
    run_test()