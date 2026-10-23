"""
In-app notifications system for GL Orenza Salon Ahmedabad.
"""

from typing import Dict, Any, List, Optional
from database.connection import fetch_all, execute_query


def send_notification(
    recipient_role: str,
    title: str,
    message: str,
    recipient_user_id: Optional[int] = None
) -> bool:
    """Dispatch an in-app notification to users or roles."""
    try:
        execute_query(
            """
            INSERT INTO notifications (recipient_role, recipient_user_id, title, message, is_read)
            VALUES (?, ?, ?, ?, 0);
            """,
            (recipient_role, recipient_user_id, title.strip(), message.strip())
        )
        return True
    except Exception:
        return False


def get_user_notifications(role: str, user_id: int) -> List[Dict[str, Any]]:
    """Retrieve unread and recent notifications for a user."""
    query = """
        SELECT * FROM notifications
        WHERE (recipient_role = 'all' OR recipient_role = ? OR recipient_user_id = ?)
        ORDER BY created_at DESC
        LIMIT 20;
    """
    return fetch_all(query, (role, user_id))