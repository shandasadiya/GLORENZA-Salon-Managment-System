"""
Inventory and stock management module.
Strictly logs all stock changes via transactions (Audit Trail).
"""

from typing import Optional, Dict, Any, List, Tuple
from database.connection import fetch_all, execute_query, get_db_connection


def adjust_stock(
    product_id: int, 
    quantity_change: int, 
    transaction_type: str, 
    reference_id: Optional[str] = None, 
    notes: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Safely update product stock and create an audit log entry.
    Quantity change can be positive (Purchase/Return) or negative (Sale/Usage/Damage).
    """
    if quantity_change == 0:
        return False, "Quantity change cannot be zero."

    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()
            
            # Check current stock to prevent negative inventory
            cursor.execute("SELECT stock_quantity, name FROM products WHERE id = ? AND status != 'discontinued';", (product_id,))
            product = cursor.fetchone()
            if not product:
                return False, "Product not found or is discontinued."
                
            new_stock = product["stock_quantity"] + quantity_change
            if new_stock < 0:
                return False, f"Insufficient stock for '{product['name']}'. Current stock is {product['stock_quantity']}."

            # Update master stock
            cursor.execute("UPDATE products SET stock_quantity = ? WHERE id = ?;", (new_stock, product_id))
            
            # Log transaction
            cursor.execute(
                """
                INSERT INTO inventory_transactions (product_id, transaction_type, quantity, reference_id, notes)
                VALUES (?, ?, ?, ?, ?);
                """,
                (product_id, transaction_type.upper(), quantity_change, reference_id, notes)
            )
            return True, f"Stock updated. New quantity: {new_stock}"
    except Exception as e:
        return False, f"Inventory update failed: {str(e)}"
    finally:
        conn.close()


def get_low_stock_alerts() -> List[Dict[str, Any]]:
    """Return products whose current stock is at or below the minimum alert level."""
    query = """
        SELECT id, product_code, name, stock_quantity, min_stock_alert 
        FROM products 
        WHERE stock_quantity <= min_stock_alert AND status = 'active'
        ORDER BY stock_quantity ASC;
    """
    return fetch_all(query)