"""
Customer support inquiries and resolution management.
"""

from typing import Dict, Any, List, Tuple
from database.connection import fetch_all, execute_query


def create_support_ticket(customer_id: int, subject: str, message: str) -> Tuple[bool, str]:
    """Create a new customer inquiry/support request."""
    if not subject.strip() or not message.strip():
        return False, "Subject and message are required."

    try:
        execute_query(
            """
            INSERT INTO support_messages (customer_id, subject, message, status)
            VALUES (?, ?, ?, 'Open');
            """,
            (customer_id, subject.strip(), message.strip())
        )
        return True, "Your message has been sent to salon management."
    except Exception as e:
        return False, f"Failed to send message: {str(e)}"


def get_customer_tickets(customer_id: int) -> List[Dict[str, Any]]:
    """Fetch tickets submitted by a specific customer."""
    return fetch_all(
        "SELECT * FROM support_messages WHERE customer_id = ? ORDER BY created_at DESC;",
        (customer_id,)
    )


def get_all_tickets() -> List[Dict[str, Any]]:
    """Fetch all support tickets for owner dashboard."""
    query = """
        SELECT sm.*, c.full_name as customer_name, c.phone as customer_phone
        FROM support_messages sm
        JOIN customers c ON sm.customer_id = c.id
        ORDER BY sm.created_at DESC;
    """
    return fetch_all(query)