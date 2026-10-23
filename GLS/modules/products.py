"""
Product management module for GL Orenza Salon.
Handles creation and tracking of retail and in-salon products.
"""

from typing import Optional, Dict, Any, List, Tuple
from database.connection import fetch_one, fetch_all, execute_query
from utils.validators import generate_code


def get_next_product_code() -> str:
    """Generate sequential product identifier: GLZ-PRD-0001"""
    row = fetch_one("SELECT COUNT(*) as total FROM products;")
    count = (row["total"] if row else 0) + 1
    return generate_code("GLZ-PRD", count, padding=4)


def add_product(
    name: str,
    category: str,
    brand: str,
    purchase_price: float,
    selling_price: float,
    initial_stock: int = 0,
    min_stock_alert: int = 5,
    vendor_id: Optional[int] = None
) -> Tuple[bool, str, Optional[int]]:
    """Register a new product in the salon database."""
    code = get_next_product_code()
    try:
        product_id = execute_query(
            """
            INSERT INTO products (
                product_code, name, category, brand, 
                purchase_price, selling_price, stock_quantity, 
                min_stock_alert, vendor_id, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'active');
            """,
            (code, name.strip(), category.strip(), brand.strip(), purchase_price, selling_price, initial_stock, min_stock_alert, vendor_id)
        )
        # If initial stock > 0, we should ideally log it in inventory_transactions, 
        # but for simplicity we rely on the inventory module for future updates.
        return True, f"Product '{name}' added ({code}).", product_id
    except Exception as e:
        return False, f"Failed to add product: {str(e)}", None


def get_all_products(active_only: bool = True) -> List[Dict[str, Any]]:
    """Retrieve all products, optionally filtering out discontinued ones."""
    sql = "SELECT * FROM products"
    if active_only:
        sql += " WHERE status = 'active'"
    sql += " ORDER BY name ASC;"
    return fetch_all(sql)