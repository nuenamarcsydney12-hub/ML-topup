"""
Authentication and authorization service.
Contains validation FUNCTIONS and reusable role-checking decorators.
"""
import re
from functools import wraps
from flask import session, redirect, url_for, flash, abort

from services import storage

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ---------------------------------------------------------------------------
# VALIDATION FUNCTIONS
# ---------------------------------------------------------------------------
def is_valid_email(email):
    """Validates a basic email format."""
    if not email:
        return False
    return bool(EMAIL_REGEX.match(email.strip()))


def is_valid_password(password):
    """Requires at least 6 characters."""
    return bool(password) and len(password) >= 6


def is_valid_name(name):
    return bool(name) and len(name.strip()) >= 2


def validate_registration(name, email, password, confirm_password):
    """Returns a list of error strings; empty list means valid."""
    errors = []
    if not is_valid_name(name):
        errors.append("Please enter your full name (at least 2 characters).")
    if not is_valid_email(email):
        errors.append("Please enter a valid email address.")
    if not is_valid_password(password):
        errors.append("Password must be at least 6 characters long.")
    if password != confirm_password:
        errors.append("Passwords do not match.")
    if is_valid_email(email) and storage.find_user_by_email(email):
        errors.append("An account with this email already exists.")
    return errors


def validate_user_form(name, email, password, confirm_password, editing_user=None):
    """Validation for the admin add/edit user form. Returns a list of errors.
    - editing_user=None means a NEW user: the password is required.
    - editing_user=<User> means an EDIT: the password is optional (blank = keep old)."""
    errors = []
    if not is_valid_name(name):
        errors.append("Please enter a name (at least 2 characters).")
    if not is_valid_email(email):
        errors.append("Please enter a valid email address.")
    else:
        existing = storage.find_user_by_email(email)
        # The email may already exist only if it belongs to the user being edited
        if existing and (editing_user is None or existing.id != editing_user.id):
            errors.append("Another account already uses this email.")
    if editing_user is None or password or confirm_password:
        if not is_valid_password(password):
            errors.append("Password must be at least 6 characters long.")
        elif password != confirm_password:
            errors.append("Passwords do not match.")
    return errors


def validate_login(email, password):
    errors = []
    if not is_valid_email(email):
        errors.append("Please enter a valid email address.")
    if not password:
        errors.append("Please enter your password.")
    return errors


def validate_game_account(game_id, server_id):
    errors = []
    if not game_id or not game_id.strip().isdigit():
        errors.append("Please enter a valid numeric Game ID.")
    if not server_id or not server_id.strip().isdigit():
        errors.append("Please enter a valid numeric Server ID.")
    return errors


VALID_PAYMENT_METHODS = ["GCash", "Maya", "Card", "Demo Payment"]


def validate_checkout(product_id, payment_method, email):
    errors = []
    if product_id is None:
        errors.append("Please select a top-up product.")
    if payment_method not in VALID_PAYMENT_METHODS:
        errors.append("Please select a valid payment method.")
    if not is_valid_email(email):
        errors.append("Please enter a valid email address for the order.")
    return errors


# ---------------------------------------------------------------------------
# AUTHENTICATION HELPERS
# ---------------------------------------------------------------------------
def attempt_login(email, password):
    """Returns the user object if credentials are valid, else None."""
    user = storage.find_user_by_email(email)
    if user and user.check_password(password):
        return user
    return None


def current_user():
    """Returns the logged-in user object, or None."""
    user_id = session.get("user_id")
    if user_id is None:
        return None
    return storage.find_user_by_id(user_id)


def login_user_session(user):
    session["user_id"] = user.id
    session["role"] = user.role
    session["name"] = user.name


def logout_user_session():
    session.clear()


# ---------------------------------------------------------------------------
# ROLE-BASED ACCESS DECORATORS (server-side authorization)
# ---------------------------------------------------------------------------
def login_required(view_func):
    """Requires the user to be logged in. Redirects to login otherwise."""
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if session.get("user_id") is None:
            flash("Please log in to continue.", "error")
            return redirect(url_for("auth.login"))
        return view_func(*args, **kwargs)
    return wrapped


def role_required(*allowed_roles):
    """Requires the user to be logged in AND have one of the allowed roles.
    Usage: @role_required("admin") or @role_required("admin", "staff")
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if session.get("user_id") is None:
                flash("Please log in to continue.", "error")
                return redirect(url_for("auth.login"))
            if session.get("role") not in allowed_roles:
                flash("You are not authorized to access that page.", "error")
                abort(403)
            return view_func(*args, **kwargs)
        return wrapped
    return decorator
