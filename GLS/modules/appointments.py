"""
Core appointment scheduling and conflict prevention engine.
Guarantees zero overlapping bookings for staff and salon chairs.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from database.connection import fetch_one, fetch_all, execute_query, get_db_connection
from utils.validators import generate_code
from modules.services import get_service_by_id
from modules.chairs import get_available_chair_for_slot


def get_next_appointment_code() -> str:
    """Generate sequential appointment identifier: GLZ-APT-0001, GLZ-APT-0002..."""
    row = fetch_one("SELECT COUNT(*) as total FROM appointments;")
    count = (row["total"] if row else 0) + 1
    return generate_code("GLZ-APT", count, padding=4)


def calculate_end_time(start_time_str: str, duration_minutes: int) -> str:
    """Calculate appointment finish time based on service duration."""
    fmt = "%H:%M"
    start_dt = datetime.strptime(start_time_str, fmt)
    end_dt = start_dt + timedelta(minutes=duration_minutes)
    return end_dt.strftime(fmt)


def check_staff_conflict(staff_id: int, date_str: str, start_time: str, end_time: str) -> bool:
    """
    Check if the requested staff member is already occupied in the specified time window.
    Returns True if a conflict exists.
    """
    query = """
        SELECT id FROM appointments
        WHERE staff_id = ?
        AND appointment_date = ?
        AND status IN ('Confirmed', 'In Progress', 'Pending')
        AND (
            (start_time < ? AND end_time > ?)
        );
    """
    row = fetch_one(query, (staff_id, date_str, end_time, start_time))
    return row is not None


def book_appointment(
    customer_id: int,
    staff_id: int,
    service_id: int,
    appointment_date: str,
    start_time: str,
    notes: Optional[str] = None
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Book an appointment with real-time validation and chair assignment.
    """
    # 1. Fetch service to determine duration
    service = get_service_by_id(service_id)
    if not service:
        return False, "Selected service does not exist.", None

    duration = service.get("duration_minutes", 30)
    end_time = calculate_end_time(start_time, duration)

    # 2. Strict Staff Conflict Verification
    if check_staff_conflict(staff_id, appointment_date, start_time, end_time):
        return False, f"Selected specialist is already booked between {start_time} and {end_time}. Please choose another time or specialist.", None

    # 3. Chair Allocation
    chair_id = get_available_chair_for_slot(appointment_date, start_time, end_time)
    if not chair_id:
        return False, "All salon stations/chairs are fully occupied at this time slot. Please select a different time.", None

    appointment_code = get_next_appointment_code()

    # 4. Insert Appointment
    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO appointments (
                    appointment_code, customer_id, staff_id, service_id, chair_id,
                    appointment_date, start_time, end_time, status, notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Confirmed', ?);
                """,
                (appointment_code, customer_id, staff_id, service_id, chair_id, appointment_date, start_time, end_time, notes)
            )
            apt_id = cursor.lastrowid

            return True, f"Appointment booked successfully! Booking Code: {appointment_code}", {
                "appointment_id": apt_id,
                "appointment_code": appointment_code,
                "chair_id": chair_id,
                "start_time": start_time,
                "end_time": end_time
            }
    except Exception as e:
        return False, f"Failed to book appointment: {str(e)}", None
    finally:
        conn.close()


def update_appointment_status(appointment_id: int, new_status: str, cancellation_reason: Optional[str] = None) -> bool:
    """Update status of appointment ('In Progress', 'Completed', 'Cancelled', etc.)."""
    try:
        execute_query(
            "UPDATE appointments SET status = ?, cancellation_reason = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?;",
            (new_status, cancellation_reason, appointment_id)
        )
        return True
    except Exception:
        return False


def get_customer_appointments(customer_id: int) -> List[Dict[str, Any]]:
    """Retrieve all appointments for a given customer."""
    query = """
        SELECT a.*, s.name as service_name, s.price as service_price,
               st.full_name as staff_name, c.chair_name
        FROM appointments a
        JOIN services s ON a.service_id = s.id
        JOIN staff st ON a.staff_id = st.id
        LEFT JOIN chairs c ON a.chair_id = c.id
        WHERE a.customer_id = ?
        ORDER BY a.appointment_date DESC, a.start_time DESC;
    """
    return fetch_all(query, (customer_id,))


def get_staff_appointments(staff_id: int, date_str: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve appointments assigned to a specific staff member."""
    sql = """
        SELECT a.*, s.name as service_name, s.duration_minutes,
               cust.full_name as customer_name, cust.phone as customer_phone, c.chair_name
        FROM appointments a
        JOIN services s ON a.service_id = s.id
        JOIN customers cust ON a.customer_id = cust.id
        LEFT JOIN chairs c ON a.chair_id = c.id
        WHERE a.staff_id = ?
    """
    params: List[Any] = [staff_id]
    if date_str:
        sql += " AND a.appointment_date = ?"
        params.append(date_str)
    sql += " ORDER BY a.start_time ASC;"
    return fetch_all(sql, tuple(params))