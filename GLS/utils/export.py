"""
Data export utility.
Exports database records to Excel (.xlsx) using pandas and openpyxl.
"""

import io
import pandas as pd
from typing import List, Dict, Any


def export_to_excel(data: List[Dict[str, Any]], sheet_name: str = "Sheet1") -> bytes:
    """Convert a list of dictionary records to in-memory Excel bytes."""
    if not data:
        df = pd.DataFrame([{"Info": "No records found."}])
    else:
        df = pd.DataFrame(data)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    
    return output.getvalue()