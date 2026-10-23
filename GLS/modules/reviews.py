"""
Customer review and ratings module.
"""

from typing import Dict, Any, List, Tuple
from database.connection import fetch_all, execute_query


def add_review(
    customer_id: int,
    appointment_id: int,
    staff_id: int,
    rating: int,
    review_text: str
) -> Tuple[bool, str]:
    """Submit a customer rating and feedback."""
    if not (1 <= rating <= 5):
        return False, "Rating must be between 1 and 5 stars."

    try:
        execute_query(
            """
            INSERT INTO reviews (customer_id, appointment_id, staff_id, rating, review_text, status)
            VALUES (?, ?, ?, ?, ?, 'Visible');
            """,
            (customer_id, appointment_id, staff_id, rating, review_text.strip())
        )
        return True, "Thank you! Your feedback has been recorded."
    except Exception as e:
        return False, f"Failed to submit review: {str(e)}"


def get_all_reviews() -> List[Dict[str, Any]]:
    """Fetch visible customer reviews."""
    query = """
        SELECT r.*, c.full_name as customer_name, s.full_name as staff_name
        FROM reviews r
        JOIN customers c ON r.customer_id = c.id
        LEFT JOIN staff s ON r.staff_id = s.id
        WHERE r.status = 'Visible'
        ORDER BY r.created_at DESC;
    """
    return fetch_all(query)