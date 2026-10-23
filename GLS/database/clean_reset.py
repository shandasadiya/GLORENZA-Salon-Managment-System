"""
Resets transactions to 0 while keeping 6 stations, 6 staff, 30 services, and 50 inventory items.
"""

from database.connection import get_db_connection
from database.seed import seed_database


def reset_transactions():
    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM payments;")
            cursor.execute("DELETE FROM bill_items;")
            cursor.execute("DELETE FROM staff_commissions;")
            cursor.execute("DELETE FROM appointments;")
            cursor.execute("DELETE FROM bills;")
            print("Transactions and old test data purged.")
    finally:
        conn.close()

    seed_database()
    print("Master catalog, staff, and stations ready.")


if __name__ == "__main__":
    reset_transactions()