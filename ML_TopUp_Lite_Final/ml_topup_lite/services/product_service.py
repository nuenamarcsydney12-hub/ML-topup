"""
Product service - functions for validating and formatting product data.
"""
from services import storage


def validate_product_form(name, diamonds, bonus, price, old_price):
    """Validates admin product form input. Returns list of error strings."""
    errors = []
    if not name or len(name.strip()) < 2:
        errors.append("Product name is required.")

    try:
        diamonds_val = int(diamonds)
        if diamonds_val < 0:
            errors.append("Diamonds must be zero or a positive number.")
    except (TypeError, ValueError):
        errors.append("Diamonds must be a valid whole number.")

    try:
        bonus_val = int(bonus)
        if bonus_val < 0:
            errors.append("Bonus must be zero or a positive number.")
    except (TypeError, ValueError):
        errors.append("Bonus must be a valid whole number.")

    try:
        price_val = float(price)
        if price_val <= 0:
            errors.append("Price must be greater than zero.")
    except (TypeError, ValueError):
        errors.append("Price must be a valid number.")

    if old_price not in (None, "", "0"):
        try:
            old_price_val = float(old_price)
            if old_price_val < 0:
                errors.append("Old price cannot be negative.")
        except (TypeError, ValueError):
            errors.append("Old price must be a valid number if provided.")

    return errors


def format_price(amount):
    """Formats a number as a demo PHP price string."""
    return f"\u20b1{amount:,.2f}"


def get_product_or_none(product_id_str):
    """Safely converts a string product id and looks it up."""
    try:
        product_id = int(product_id_str)
    except (TypeError, ValueError):
        return None
    return storage.find_product_by_id(product_id)
