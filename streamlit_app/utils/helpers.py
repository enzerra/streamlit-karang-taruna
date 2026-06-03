import numpy as np

def format_currency(value):
    """Formats a number as Indonesian Rupiah."""
    try:
        # Cast to float to handle numpy types safely
        val = float(value)
        if val < 0:
            return f"-Rp {abs(val):,.0f}".replace(",", ".")
        return f"Rp {val:,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return "Rp 0"

def get_percentage_change(current, previous):
    """Calculates the percentage change between two values."""
    if previous == 0:
        return 0 if current == 0 else 100
    change = ((current - previous) / previous) * 100
    return round(change, 2)
