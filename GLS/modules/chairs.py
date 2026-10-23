"""
Salon station / chair management module.
Tracks real-time physical seat availability inside GL Orenza Salon Ahmedabad.
"""

from typing import Optional, Dict, Any, List, Tuple
from database.connection import fetch_one, fetch_all, execute_query
from utils.validators import generate_code


def get_next_chair_code() -> str:
    """Generate sequential chair code: GLZ-CHR-01, GLZ-CHR-02..."""
    row = fetch_one("SELECT COUNT(*) as total FROM chairs;")
    count = (row["total"] if row else 0) + 1
    return generate_code("GLZ-CHR", count, padding=2)


def add_chair(chair_name: str, chair_type: str = "General") -> Tuple[bool, str, Optional[int]]:
    """Register a new salon station/chair."""
    code = get_next_chair_code()
    try:
        chair_id = execute_query(
            "INSERT INTO chairs (chair_code, chair_name, chair_type, status) VALUES (?, ?, ?, 'Available');",
            (code, chair_name.strip(), chair_type)
        )
        return True, f"Chair '{chair_name}' added ({code})", chair_id
    except Exception as e:
        return False, f"Failed to add chair: {str(e)}", None


def get_all_chairs() -> List[Dict[str, Any]]:
    """Retrieve all salon chairs with live status."""
    return fetch_all("SELECT * FROM chairs ORDER BY chair_code ASC;")


def get_available_chair_for_slot(appointment_date: str, start_time: str, end_time: str) -> Optional[int]:
    """
    Find first available chair that does not conflict with confirmed/in-progress bookings.
    """
    query = """
        SELECT c.id FROM chairs c
        WHERE c.status NOT IN ('Maintenance', 'Inactive')
        AND c.id NOT IN (
            SELECT a.chair_id FROM appointments a
            WHERE a.appointment_date = ?
            AND a.status IN ('Confirmed', 'In Progress', 'Pending')
            AND a.chair_id IS NOT NULL
            AND (
                (a.start_time < ? AND a.end_time > ?)
            )
        )
        ORDER BY c.id ASC
        LIMIT 1;
    """
    row = fetch_one(query, (appointment_date, end_time, start_time))
    return row["id"] if row else None