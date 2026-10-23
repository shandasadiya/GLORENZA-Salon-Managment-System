"""
Services and staff-service mapping module for GL Orenza Salon Ahmedabad.
"""

from typing import Optional, Dict, Any, List, Tuple
from database.connection import fetch_one, fetch_all, execute_query, get_db_connection
from utils.validators import generate_code


def get_next_service_code() -> str:
    """Generate next sequential service code: GLZ-SRV-0001, GLZ-SRV-0002..."""
    row = fetch_one("SELECT COUNT(*) as total FROM services;")
    count = (row["total"] if row else 0) + 1
    return generate_code("GLZ-SRV", count, padding=4)


def create_service(
    name: str,
    category: str,
    price: float,
    duration_minutes: int = 30,
    description: Optional[str] = None
) -> Tuple[bool, str, Optional[int]]:
    """Create a new salon service."""
    if not name.strip():
        return False, "Service name cannot be empty.", None
    if price < 0:
        return False, "Price cannot be negative.", None

    service_code = get_next_service_code()
    try:
        service_id = execute_query(
            """
            INSERT INTO services (service_code, name, category, description, duration_minutes, price, status)
            VALUES (?, ?, ?, ?, ?, ?, 'active');
            """,
            (service_code, name.strip(), category.strip(), description, duration_minutes, float(price))
        )
        return True, f"Service '{name}' created with code {service_code}", service_id
    except Exception as e:
        return False, f"Failed to create service: {str(e)}", None


def get_all_services(category: Optional[str] = None, active_only: bool = True) -> List[Dict[str, Any]]:
    """Retrieve list of services."""
    sql = "SELECT * FROM services WHERE 1=1"
    params: List[Any] = []
    if active_only:
        sql += " AND status = 'active'"
    if category and category != "All":
        sql += " AND category = ?"
        params.append(category)
    sql += " ORDER BY category ASC, name ASC;"
    return fetch_all(sql, tuple(params))


def get_service_by_id(service_id: int) -> Optional[Dict[str, Any]]:
    """Fetch single service details."""
    return fetch_one("SELECT * FROM services WHERE id = ?;", (service_id,))


def assign_service_to_staff(staff_id: int, service_id: int) -> bool:
    """Link a staff specialist to a service."""
    try:
        execute_query(
            "INSERT OR IGNORE INTO staff_services (staff_id, service_id) VALUES (?, ?);",
            (staff_id, service_id)
        )
        return True
    except Exception:
        return False


def get_staff_for_service(service_id: int) -> List[Dict[str, Any]]:
    """Retrieve all active staff members eligible to perform a specific service."""
    query = """
        SELECT s.id, s.staff_code, s.full_name, s.role, s.specialization
        FROM staff s
        JOIN staff_services ss ON s.id = ss.staff_id
        WHERE ss.service_id = ? AND s.status = 'active'
        ORDER BY s.full_name ASC;
    """
    return fetch_all(query, (service_id,))