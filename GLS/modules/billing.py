"""
Invoicing and billing module.
Handles calculation of services and products, and updates statuses.
"""

from typing import Optional, Dict, Any, List, Tuple
from database.connection import fetch_one, execute_query, get_db_connection
from utils.validators import generate_code
from modules.inventory import adjust_stock


def get_next_invoice_number() -> str:
    """Generate sequential invoice number: GLZ-INV-000001"""
    row = fetch_one("SELECT COUNT(*) as total FROM bills;")
    count = (row["total"] if row else 0) + 1
    return generate_code("GLZ-INV", count, padding=6)


def create_bill(
    customer_id: int,
    items: List[Dict[str, Any]],  # List of dicts: {'type': 'SERVICE'|'PRODUCT', 'id': int, 'staff_id': Optional[int], 'name': str, 'price': float, 'qty': int}
    appointment_id: Optional[int] = None,
    discount_amount: float = 0.0,
    tax_amount: float = 0.0
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Generate a final bill.
    Deducts product inventory if products are sold.
    Marks appointment as Completed if linked.
    """
    if not items:
        return False, "Cannot create an empty bill.", None

    subtotal = sum((item['price'] * item['qty']) for item in items)
    grand_total = (subtotal - discount_amount) + tax_amount
    
    if grand_total < 0:
        return False, "Grand total cannot be negative.", None

    bill_number = get_next_invoice_number()
    conn = get_db_connection()
    
    try:
        with conn:
            cursor = conn.cursor()
            
            # Create main bill record
            cursor.execute(
                """
                INSERT INTO bills (bill_number, customer_id, appointment_id, subtotal, discount_amount, tax_amount, grand_total, payment_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'Pending');
                """,
                (bill_number, customer_id, appointment_id, subtotal, discount_amount, tax_amount, grand_total)
            )
            bill_id = cursor.lastrowid

            # Insert line items
            for item in items:
                total_price = item['price'] * item['qty']
                cursor.execute(
                    """
                    INSERT INTO bill_items (bill_id, item_type, item_id, staff_id, item_name, unit_price, quantity, total_price)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (bill_id, item['type'], item['id'], item.get('staff_id'), item['name'], item['price'], item['qty'], total_price)
                )

            # Update appointment status if linked
            if appointment_id:
                cursor.execute("UPDATE appointments SET status = 'Completed' WHERE id = ?;", (appointment_id,))
                # Free up the chair
                cursor.execute(
                    "UPDATE chairs SET status = 'Available' WHERE id = (SELECT chair_id FROM appointments WHERE id = ?);", 
                    (appointment_id,)
                )

        # Handle inventory deduction outside the main transaction to utilize existing logic, 
        # but in a real-world scenario, you might wrap it all in one.
        for item in items:
            if item['type'] == 'PRODUCT':
                adjust_stock(
                    product_id=item['id'],
                    quantity_change=-(item['qty']),
                    transaction_type='SALE',
                    reference_id=bill_number,
                    notes=f"Sold on invoice {bill_number}"
                )

        return True, f"Bill {bill_number} generated successfully.", {"bill_id": bill_id, "bill_number": bill_number, "total": grand_total}

    except Exception as e:
        return False, f"Billing failed: {str(e)}", None