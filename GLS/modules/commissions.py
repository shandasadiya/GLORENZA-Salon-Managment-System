"""
Staff commission tracking module.
Calculates service and retail product commissions.
"""

from typing import Dict, Any, List, Tuple
from database.connection import fetch_all, execute_query, get_db_connection


def calculate_and_record_commission(bill_id: int) -> bool:
    """
    Calculate and record commissions for all bill items linked to a staff member.
    """
    conn = get_db_connection()
    try:
        with conn:
            cursor = conn.cursor()
            # Fetch bill items with staff mapping and staff commission percentage
            query = """
                SELECT bi.item_type, bi.item_id, bi.staff_id, bi.total_price,
                       s.service_commission_percent, s.product_commission_percent
                FROM bill_items bi
                JOIN staff s ON bi.staff_id = s.id
                WHERE bi.bill_id = ? AND bi.staff_id IS NOT NULL;
            """
            cursor.execute(query, (bill_id,))
            items = cursor.fetchall()

            for item in items:
                comm_pct = (
                    item["service_commission_percent"]
                    if item["item_type"] == "SERVICE"
                    else item["product_commission_percent"]
                )
                comm_amount = (item["total_price"] * comm_pct) / 100.0

                cursor.execute(
                    """
                    INSERT INTO staff_commissions (
                        staff_id, bill_id, item_type, item_id, item_amount,
                        commission_percent, commission_amount, status
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'Unpaid');
                    """,
                    (
                        item["staff_id"],
                        bill_id,
                        item["item_type"],
                        item["item_id"],
                        item["total_price"],
                        comm_pct,
                        comm_amount,
                    ),
                )
        return True
    except Exception:
        return False
    finally:
        conn.close()


def get_staff_commissions(staff_id: int, status: str = "All") -> List[Dict[str, Any]]:
    """Fetch commission details for a staff member."""
    sql = """
        SELECT sc.*, b.bill_number, b.created_at as bill_date
        FROM staff_commissions sc
        JOIN bills b ON sc.bill_id = b.id
        WHERE sc.staff_id = ?
    """
    params = [staff_id]
    if status != "All":
        sql += " AND sc.status = ?"
        params.append(status)
    sql += " ORDER BY sc.created_at DESC;"
    return fetch_all(sql, tuple(params))