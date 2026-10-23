"""
Verification script for GL Orenza Salon database setup.
"""

import sys
from pathlib import Path

# Add project root directory to sys.path so imports work directly
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from database.schema import init_database
from database.connection import get_db_connection


def run_test():
    print("Initializing database...")
    init_database()

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;")
        tables = [row[0] for row in cursor.fetchall()]

        print("\n--- DATABASE VERIFICATION REPORT ---")
        print(f"Total tables created: {len(tables)}")
        for idx, table in enumerate(tables, start=1):
            print(f"{idx}. {table}")
        print("------------------------------------")
    finally:
        conn.close()


if __name__ == "__main__":
    run_test()