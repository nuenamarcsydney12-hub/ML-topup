"""
User models demonstrating OOP concepts:
- ENCAPSULATION: private attributes (__password, __email) with getters/setters
- INHERITANCE: Customer, Staff, Admin all inherit from User
- POLYMORPHISM: get_dashboard_title(), get_permissions(), describe_role()
  are overridden differently in each subclass
"""
from werkzeug.security import generate_password_hash, check_password_hash


class User:
    """Base User class. Never instantiated directly in the app - use a subclass."""

    def __init__(self, user_id, name, email, password, role="user"):
        self.id = user_id
        self.name = name
        self.__email = email          # ENCAPSULATION: private attribute
        self.__password = None        # ENCAPSULATION: private attribute
        self.set_password(password)
        self.role = role

    # ---------- Encapsulation: getters / setters ----------
    def get_email(self):
        """Getter for the private __email attribute."""
        return self.__email

    def set_email(self, new_email):
        """Setter for the private __email attribute."""
        self.__email = new_email

    def set_password(self, plain_password):
        """Hashes and stores the password. The plain password is never kept."""
        self.__password = generate_password_hash(plain_password)

    def check_password(self, plain_password):
        """Checks a plain password against the stored hash."""
        return check_password_hash(self.__password, plain_password)

    # ---------- Polymorphism: overridden in subclasses ----------
    def get_dashboard_title(self):
        """Overridden by each subclass. Base implementation is generic."""
        return "User Dashboard"

    def get_permissions(self):
        """Overridden by each subclass. Base implementation grants nothing."""
        return []

    def describe_role(self):
        """Overridden by each subclass to describe what the role can do."""
        return "Generic user with no special permissions."

    # ---------- Shared functions ----------
    def to_public_dict(self):
        """Returns a dict safe to display (never includes the password)."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.get_email(),
            "role": self.role,
        }

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.id} email={self.get_email()}>"


class Customer(User):
    """Customer role - INHERITANCE from User."""

    def __init__(self, user_id, name, email, password):
        super().__init__(user_id, name, email, password, role="customer")

    # ---------- Polymorphism overrides ----------
    def get_dashboard_title(self):
        return "Customer Dashboard"

    def get_permissions(self):
        return [
            "browse_products",
            "create_order",
            "view_own_orders",
            "view_profile",
        ]

    def describe_role(self):
        return "Customer: can browse Mobile Legends products and place top-up orders."


class Staff(User):
    """Staff role - INHERITANCE from User."""

    def __init__(self, user_id, name, email, password):
        super().__init__(user_id, name, email, password, role="staff")

    # ---------- Polymorphism overrides ----------
    def get_dashboard_title(self):
        return "Staff Dashboard"

    def get_permissions(self):
        return [
            "view_all_orders",
            "search_orders",
            "update_order_status",
        ]

    def describe_role(self):
        return "Staff: can view all orders, search orders, and update order status."


class Admin(User):
    """Admin role - INHERITANCE from User."""

    def __init__(self, user_id, name, email, password):
        super().__init__(user_id, name, email, password, role="admin")

    # ---------- Polymorphism overrides ----------
    def get_dashboard_title(self):
        return "Admin Dashboard"

    def get_permissions(self):
        return [
            "manage_users",
            "manage_products",
            "view_all_orders",
            "search_orders",
            "update_order_status",
            "view_statistics",
        ]

    def describe_role(self):
        return "Admin: full system access - manages users, products, and orders."
