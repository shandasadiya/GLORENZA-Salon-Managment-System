"""
Payment processing module.
Records received payments against invoices.
"""

from typing import Optional, Dict, Any, List, Tuple
from database.connection import fetch_one, execute_query, get_db_connection
from utils.validators import generate_code


def get_next_payment_code() -> str:
    row = fetch_one("SELECT COUNT(*) as total FROM payments;")
    count = (row["total"] if row else 0) + 1
    return generate_code("GLZ-PAY", count, padding=5)


def record_payment(
    bill_id: int,
    amount: float,
    payment_method: str,
    transaction_reference: Optional[str] = None
) -> Tuple[bool, str]:
    """Record a payment and update bill status."""
    
    # Verify bill exists and amount is valid
    bill = fetch_one("SELECT grand_total, payment_status FROM bills WHERE id = ?;", (bill_id,))
    if not bill:
        return False, "Invoice not found."
    if bill["payment_status"] == "Paid":
        return False, "This invoice is already fully paid."

    # Check total payments so far
    paid_so_far_row = fetch_one("SELECT SUM(amount) as total_paid FROM payments WHERE bill_id = ? AND status = 'Success';", (bill_id,))
    paid_so_far = paid_so_far_row["total_paid"] if paid_so_far_row and paid_so_far_row["total_paid"] else 0.0
    
    remaining_balance = bill["grand_total"] - paid_so_far
    if amount > remaining_balance + 0.01: # Small float tolerance
        return False, f"Payment amount ({amount}) exceeds remaining balance ({remaining_balance})."

    payment_code = get_next_payment_code()
    conn = get_db_connection()
    
    try:
        with conn:
            cursor = conn.cursor()
            
            # Insert payment record
            cursor.execute(
                """
                INSERT INTO payments (payment_code, bill_id, amount, payment_method, transaction_reference, status)
                VALUES (?, ?, ?, ?, ?, 'Success');
                """,
                (payment_code, bill_id, amount, payment_method, transaction_reference)
            )
            
            # Determine new bill status
            new_total_paid = paid_so_far + amount
            new_status = "Paid" if new_total_paid >= (bill["grand_total"] - 0.01) else "Partially Paid"
            
            cursor.execute("UPDATE bills SET payment_status = ? WHERE id = ?;", (new_status, bill_id))
            
            return True, f"Payment of ₹{amount} recorded successfully. Bill Status: {new_status}"
    except Exception as e:
        return False, f"Payment recording failed: {str(e)}"