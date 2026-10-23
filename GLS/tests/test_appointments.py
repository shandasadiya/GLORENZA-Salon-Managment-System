"""
Appointment conflict prevention test runner.
Verifies that overlapping bookings are rejected.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from database.schema import init_database
from modules.customers import register_customer, get_all_customers
from modules.staff import create_staff_member, get_all_staff
from modules.services import create_service, assign_service_to_staff, get_all_services
from modules.chairs import add_chair, get_all_chairs
from modules.appointments import book_appointment


def run_test():
    print("Testing Services, Chairs & Appointment Engine...")
    init_database()

    # 1. Setup sample entities
    add_chair("Styling Chair 01", "General")
    add_chair("Styling Chair 02", "General")

    create_service("Signature Haircut", "Hair", price=500.0, duration_minutes=45)
    services = get_all_services()
    srv_id = services[0]["id"]

    staff_list = get_all_staff()
    staff_id = staff_list[0]["id"]
    assign_service_to_staff(staff_id, srv_id)

    customers = get_all_customers()
    cust_id = customers[0]["id"]

    # 2. Book first appointment (10:00 - 10:45)
    success1, msg1, data1 = book_appointment(
        customer_id=cust_id,
        staff_id=staff_id,
        service_id=srv_id,
        appointment_date="2026-08-25",
        start_time="10:00"
    )
    print(f"Booking 1 (10:00): {msg1}")
    assert success1 is True

    # 3. Attempt overlapping appointment (10:15 - 11:00) with SAME staff
    success2, msg2, data2 = book_appointment(
        customer_id=cust_id,
        staff_id=staff_id,
        service_id=srv_id,
        appointment_date="2026-08-25",
        start_time="10:15"
    )
    print(f"Booking 2 (Overlapping Attempt 10:15): {msg2}")
    assert success2 is False, "Conflict prevention failed! Double booking was allowed."
    print("Conflict prevention verified: Double booking prevented successfully.\n")


if __name__ == "__main__":
    run_test()