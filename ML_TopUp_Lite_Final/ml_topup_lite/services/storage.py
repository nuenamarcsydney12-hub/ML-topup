"""
In-memory storage using PYTHON LISTS ONLY.
NO DATABASE of any kind is used (no SQLite, MySQL, MongoDB, SQLAlchemy, etc).
All data lives in Python lists and is lost when the Flask app restarts.
This is intentional and required for the school project.
"""
from datetime import datetime
from werkzeug.security import generate_password_hash

from models import Customer, Staff, Admin, Product, Order

# ---------------------------------------------------------------------------
# TEMPORARY STORAGE - PYTHON LISTS ONLY (no database of any kind)
# ---------------------------------------------------------------------------
users = []      # list of User/Customer/Staff/Admin objects
products = []   # list of Product objects
orders = []     # list of Order objects

# Simple counters to generate unique, incrementing IDs
_next_user_id = 1
_next_product_id = 1
_next_order_id = 1
_order_sequence_today = 0
_order_sequence_date = None


def _get_next_user_id():
    global _next_user_id
    value = _next_user_id
    _next_user_id += 1
    return value


def _get_next_product_id():
    global _next_product_id
    value = _next_product_id
    _next_product_id += 1
    return value


def _get_next_order_id():
    global _next_order_id
    value = _next_order_id
    _next_order_id += 1
    return value


def generate_order_number():
    """Generates a unique order number like ML-20260913-0001."""
    global _order_sequence_today, _order_sequence_date
    today_str = datetime.now().strftime("%Y%m%d")
    if _order_sequence_date != today_str:
        _order_sequence_date = today_str
        _order_sequence_today = 0
    _order_sequence_today += 1
    return f"ML-{today_str}-{_order_sequence_today:04d}"


# ---------------------------------------------------------------------------
# USER STORAGE FUNCTIONS
# ---------------------------------------------------------------------------
def find_user_by_email(email):
    if not email:
        return None
    email_lower = email.strip().lower()
    for user in users:
        if user.get_email().strip().lower() == email_lower:
            return user
    return None


def find_user_by_id(user_id):
    for user in users:
        if user.id == user_id:
            return user
    return None


def create_user(name, email, password, role):
    """Creates a user of the correct subclass based on role. Returns the new user."""
    user_id = _get_next_user_id()
    if role == "admin":
        user = Admin(user_id, name, email, password)
    elif role == "staff":
        user = Staff(user_id, name, email, password)
    else:
        user = Customer(user_id, name, email, password)
    users.append(user)
    return user


def update_user(user_id, name, email, password=None):
    """Updates a user's name and email. The password is changed only if a new
    one is given. The role is never changed here. Returns the user, or None."""
    user = find_user_by_id(user_id)
    if user is None:
        return None
    user.name = name
    user.set_email(email)          # private attribute -> use the setter
    if password:
        user.set_password(password)  # hashed again inside the model
    return user


def delete_user(user_id):
    global users
    user = find_user_by_id(user_id)
    if user is None:
        return False
    users = [u for u in users if u.id != user_id]
    return True


def get_all_users():
    return users


def count_users_by_role(role):
    return len([u for u in users if u.role == role])


# ---------------------------------------------------------------------------
# PRODUCT STORAGE FUNCTIONS
# ---------------------------------------------------------------------------
def find_product_by_id(product_id):
    for product in products:
        if product.id == product_id:
            return product
    return None


def create_product(name, diamonds, bonus, price, old_price=None):
    product_id = _get_next_product_id()
    product = Product(product_id, name, diamonds, bonus, price, old_price)
    products.append(product)
    return product


def update_product(product_id, name, diamonds, bonus, price, old_price=None):
    product = find_product_by_id(product_id)
    if product is None:
        return None
    product.name = name
    product.diamonds = diamonds
    product.bonus = bonus
    product.set_price(price)
    product.set_old_price(old_price)
    return product


def delete_product(product_id):
    global products
    product = find_product_by_id(product_id)
    if product is None:
        return False
    products = [p for p in products if p.id != product_id]
    return True


def get_all_products():
    return products


# ---------------------------------------------------------------------------
# ORDER STORAGE FUNCTIONS
# ---------------------------------------------------------------------------
def find_order_by_id(order_id):
    for order in orders:
        if order.id == order_id:
            return order
    return None


def find_order_by_number(order_number):
    for order in orders:
        if order.order_number == order_number:
            return order
    return None


def create_order(customer_id, game_id, server_id, product_id, product_name,
                  price, payment_method, email):
    order_id = _get_next_order_id()
    order_number = generate_order_number()
    order = Order(
        order_id=order_id,
        order_number=order_number,
        customer_id=customer_id,
        game_id=game_id,
        server_id=server_id,
        product_id=product_id,
        product_name=product_name,
        price=price,
        payment_method=payment_method,
        email=email,
        created_at=datetime.now(),
        status="Pending",
    )
    orders.append(order)
    return order


def get_all_orders():
    return orders


def get_orders_by_customer(customer_id):
    return [o for o in orders if o.customer_id == customer_id]


def search_orders(query, order_list=None):
    """Searches by order number, game id, server id, or email (case-insensitive)."""
    source = order_list if order_list is not None else orders
    if not query:
        return source
    query_lower = query.strip().lower()
    results = []
    for order in source:
        haystack = " ".join([
            order.order_number.lower(),
            str(order.game_id).lower(),
            str(order.server_id).lower(),
            order.email.lower(),
            order.product_name.lower(),
        ])
        if query_lower in haystack:
            results.append(order)
    return results


def count_orders_by_status(status, order_list=None):
    source = order_list if order_list is not None else orders
    return len([o for o in source if o.status == status])


def total_sales():
    """Sums price of Completed orders only (demo sales total)."""
    return sum(o.price for o in orders if o.status == "Completed")


# ---------------------------------------------------------------------------
# SEED DATA - demo accounts and demo products
# ---------------------------------------------------------------------------
def seed_data():
    """Populates the in-memory lists with demo accounts and demo products.
    Safe to call once at app startup. Passwords are hashed, never stored plain.
    """
    if not users:
        create_user("System Admin", "admin@mltopup.local", "Admin123!", "admin")
        create_user("Support Staff", "staff@mltopup.local", "Staff123!", "staff")
        create_user("Demo Customer", "customer@mltopup.local", "Customer123!", "customer")

    if not products:
        demo_products = [
            ("5 Diamonds", 5, 0, 15.00, None),
            ("11 Diamonds", 11, 0, 30.00, None),
            ("22 Diamonds", 22, 0, 60.00, None),
            ("56 Diamonds", 56, 5, 62.00, 75.00),
            ("112 Diamonds", 112, 10, 124.00, 150.00),
            ("223 Diamonds", 223, 20, 248.00, 300.00),
            ("336 Diamonds", 336, 35, 372.00, 450.00),
            ("570 Diamonds", 570, 60, 620.00, 750.00),
            ("1163 Diamonds", 1163, 130, 1240.00, 1500.00),
            ("Weekly Diamond Pass", 0, 0, 55.00, None),
        ]
        for name, diamonds, bonus, price, old_price in demo_products:
            create_product(name, diamonds, bonus, price, old_price)
