"""
Salon expense tracking module for GL Orenza Salon.
"""

from typing import Optional, Dict, Any, List, Tuple
from database.connection import fetch_all, fetch_one, execute_query
from utils.validators import generate_code


def get_next_expense_code() -> str:
    row = fetch_one("SELECT COUNT(*) as total FROM expenses;")
    count = (row["total"] if row else 0) + 1
    return generate_code("GLZ-EXP", count, padding=4)


def add_expense(
    category: str,
    description: str,
    amount: float,
    expense_date: str,
    payment_method: str = "Cash",
    notes: Optional[str] = None
) -> Tuple[bool, str]:
    """Record an operational expense with strict validation."""
    if amount <= 0:
        return False, "Expense amount must be greater than zero."
        
    code = get_next_expense_code()
    try:
        execute_query(
            """
            INSERT INTO expenses (expense_code, category, description, amount, expense_date, payment_method, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            (code, category, description.strip(), float(amount), expense_date, payment_method, notes)
        )
        return True, f"Expense recorded successfully ({code})."
    except Exception as e:
        return False, f"Failed to record expense: {str(e)}"


def get_expenses_by_date_range(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """Retrieve expenses within a specific date range."""
    return fetch_all(
        "SELECT * FROM expenses WHERE expense_date BETWEEN ? AND ? ORDER BY expense_date DESC;",
        (start_date, end_date)
    )