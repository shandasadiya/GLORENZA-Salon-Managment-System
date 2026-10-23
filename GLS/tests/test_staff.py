"""
Staff creation and query verification test.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from modules.staff import create_staff_member, get_all_staff
from database.schema import init_database


def run_test():
    print("Testing Staff Creation & Retrieval...")
    init_database()

    success, msg, data = create_staff_member(
        full_name="Rajesh Sharma",
        phone="9898012345",
        password="StaffPass123",
        role="Senior Stylist",
        specialization="Hair Styling, Keratin Treatment",
        experience_years=5,
        salary=25000.0,
        service_commission=12.0
    )

    print(f"Staff Creation Result: {msg}")
    assert success is True or "already exists" in msg

    staff_list = get_all_staff()
    print(f"Total active staff in database: {len(staff_list)}")
    print("Staff module passed successfully.\n")


if __name__ == "__main__":
    run_test()