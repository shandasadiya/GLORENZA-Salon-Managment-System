"""
Staff payroll and monthly salary tracking module.
"""

from typing import Dict, Any, List, Tuple
from database.connection import fetch_one, fetch_all, execute_query


def process_monthly_salary(
    staff_id: int,
    month_year: str,  # Format 'YYYY-MM'
    deductions: float = 0.0,
    notes: str = ""
) -> Tuple[bool, str]:
    """Calculate and record total net salary (Base + Commission - Deductions)."""
    # Check if already processed
    existing = fetch_one(
        "SELECT id FROM staff_salary WHERE staff_id = ? AND month_year = ?;",
        (staff_id, month_year)
    )
    if existing:
        return False, f"Salary for {month_year} has already been generated."

    # Fetch staff base salary
    staff = fetch_one("SELECT salary FROM staff WHERE id = ?;", (staff_id,))
    if not staff:
        return False, "Staff member not found."

    base_salary = staff.get("salary", 0.0)

    # Calculate total unpaid commissions
    comm_row = fetch_one(
        """
        SELECT SUM(commission_amount) as total_comm
        FROM staff_commissions
        WHERE staff_id = ? AND status = 'Unpaid';
        """,
        (staff_id,)
    )
    total_commission = (comm_row["total_comm"] if comm_row and comm_row["total_comm"] else 0.0)
    net_salary = (base_salary + total_commission) - deductions

    try:
        execute_query(
            """
            INSERT INTO staff_salary (staff_id, month_year, base_salary, total_commission, deductions, net_salary, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, 'Pending', ?);
            """,
            (staff_id, month_year, base_salary, total_commission, deductions, net_salary, notes)
        )
        return True, f"Salary generated for {month_year}. Net payable: ₹{net_salary:.2f}"
    except Exception as e:
        return False, f"Salary generation failed: {str(e)}"


def get_all_salaries(month_year: str = "") -> List[Dict[str, Any]]:
    """Retrieve salary records across staff."""
    sql = """
        SELECT ss.*, s.staff_code, s.full_name as staff_name, s.role
        FROM staff_salary ss
        JOIN staff s ON ss.staff_id = s.id
    """
    params = []
    if month_year:
        sql += " WHERE ss.month_year = ?"
        params.append(month_year)
    sql += " ORDER BY ss.id DESC;"
    return fetch_all(sql, tuple(params))