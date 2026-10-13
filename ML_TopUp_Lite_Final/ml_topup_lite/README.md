# ML TopUp Lite

A lightweight, demo Mobile Legends: Bang Bang top-up and order management website, built as a **school final project** using Flask, Python OOP, and in-memory Python list storage (no database).

> ⚠️ **This is a school project / demo only.** All prices are fictional DEMO PRICES. No real payment processing occurs. This project is not affiliated with Moonton or MobaPay, and its visual design was only loosely inspired by public top-up sites — no source code, assets, or branding were copied.

---

## 1. Project Description

ML TopUp Lite lets customers simulate topping up Mobile Legends: Bang Bang diamonds. It has three user roles (Admin, Staff, Customer), full CRUD for products/users/orders, and demonstrates core Python OOP concepts (encapsulation, inheritance, polymorphism) — all without using any database.

## 2. Features

- Customer registration & login (secure password hashing)
- Role-based dashboards for Admin, Staff, and Customer
- Mobile Legends top-up flow: Game ID/Server ID → select package → demo payment → email → confirmation
- Unique order number generation (e.g. `ML-20260913-0001`)
- Admin product CRUD (create/edit/delete diamond packages)
- Admin user management (view/delete users)
- Staff & Admin order management with search and status updates
- Server-side authorization on every protected route
- Friendly flash messages and custom 403/404/500 error pages
- Fully responsive UI (desktop, tablet, mobile)

## 3. Technologies

- **Backend:** Python 3, Flask
- **Frontend:** HTML5, CSS3 (custom, no framework), Vanilla JavaScript, Jinja2 templates
- **Storage:** Python lists and dictionaries only (NO DATABASE)
- **Security:** Werkzeug's `generate_password_hash` / `check_password_hash`

## 4. Installation

```bash
# 1. Clone or unzip the project
cd ml_topup_lite

# 2. (Recommended) Create a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

## 5. How to Run

```bash
python app.py
```

Then open your browser to: **http://127.0.0.1:5000**

## 6. Demo Accounts

Seeded automatically every time the app starts.

| Role     | Email                     | Password     |
|----------|---------------------------|--------------|
| Admin    | admin@mltopup.local       | Admin123!    |
| Staff    | staff@mltopup.local       | Staff123!    |
| Customer | customer@mltopup.local    | Customer123! |

## 7. Three User Roles

- **Admin** — full access: manage users, manage products, view/search/update all orders, view statistics.
- **Staff** — view/search all orders and update order status. Cannot manage users or products.
- **Customer** — browse products, place top-up orders, view their own order history and profile. Cannot see other customers' orders or access staff/admin pages.

Role checks are enforced **server-side** with the `@role_required(...)` decorator in `services/auth_service.py` — not just by hiding buttons in the UI.

## 8. CRUD Explanation

| Operation | Where it happens |
|-----------|-------------------|
| **Create** | Admin creates products (`admin/product_create`); Customer creates orders (`customer/checkout`); Registration creates users |
| **Read**   | Product browsing, order lists, order details, user lists, search |
| **Update** | Admin edits products (`admin/product_edit`); Staff/Admin update order status |
| **Delete** | Admin deletes products; Admin deletes users |

All CRUD operates on Python lists in `services/storage.py` (`users`, `products`, `orders`).

## 9. Python OOP Explanation

### Functions
Reusable functions are used throughout `services/` for validation, statistics, price formatting, order searching, and order-number generation.

### Encapsulation
See `models/user.py` and `models/product.py`. Passwords and prices are stored as **private attributes** (`self.__password`, `self.__price`) and only accessed through getter/setter methods (`get_email()`, `set_password()`, `get_price()`, etc). Passwords are never exposed directly, and are always hashed.

### Inheritance
See `models/user.py`:

```
User
├── Customer
├── Staff
└── Admin
```

`Customer`, `Staff`, and `Admin` all inherit from the base `User` class and call `super().__init__(...)`.

### Polymorphism
Each subclass **overrides** the same three methods with role-specific behavior:

- `get_dashboard_title()`
- `get_permissions()`
- `describe_role()`

For example, calling `user.get_dashboard_title()` returns `"Customer Dashboard"`, `"Staff Dashboard"`, or `"Admin Dashboard"` depending on the actual object type — the calling code doesn't need to know which subclass it has.

## 10. Python List Storage — Why No Database?

Per the project requirements, **no database of any kind** is used (no SQLite, MySQL, PostgreSQL, MongoDB, SQLAlchemy, etc). All data — users, products, and orders — lives in plain Python lists inside `services/storage.py`:

```python
users = []
products = []
orders = []
```

**Known limitation:** because data is only stored in memory, all data (new registrations, new orders, new products) is **lost whenever the Flask app restarts**. The three demo accounts and the demo product catalog are automatically re-seeded on every restart via `storage.seed_data()`.

## 11. How to Test — Customer

1. Go to `/register` and create an account, or log in with the demo customer account.
2. From the Customer Dashboard, click **Mobile Legends Top Up**.
3. Enter a numeric Game ID and Server ID.
4. Select a diamond package, continue to payment.
5. Choose a demo payment method, enter an email, and place the order.
6. View the order confirmation, then check **My Orders**.
7. Try visiting another customer's order URL directly (e.g. change the order id in the address bar) — it should be denied (403).

## 12. How to Test — Staff

1. Log in with the demo staff account.
2. View the Staff Dashboard stats.
3. Go to **Orders**, search by order number/email/Game ID.
4. Open an order and change its status (Pending → Processing → Completed).
5. Try visiting `/admin/products` directly — it should be denied (403), since Staff cannot manage products.

## 13. How to Test — Admin

1. Log in with the demo admin account.
2. View the Admin Dashboard statistics (users, products, orders, demo sales total).
3. Go to **Products** → create a new diamond package → edit it → delete it.
4. Go to **Users** → view the user list → delete a non-admin user.
5. Go to **Orders** → search and update an order's status.

## 14. How to Test CRUD

- **Create:** Admin → Products → New Product.
- **Read:** Admin → Products (list view) or click into any order.
- **Update:** Admin → Products → Edit; or Staff/Admin → Order → change status.
- **Delete:** Admin → Products → Delete button (confirmation prompt appears).

## 15. How to Demonstrate OOP During Presentation

1. Open `models/user.py` and point to the `User`, `Customer`, `Staff`, `Admin` classes — show the inheritance (`class Customer(User):`).
2. Point to `self.__password` and `self.__email` — explain encapsulation and the getter/setter methods below them.
3. In the terminal or a Python shell, show polymorphism live:
   ```python
   from services import storage
   storage.seed_data()
   for u in storage.get_all_users():
       print(u.name, "->", u.get_dashboard_title())
   ```
   Notice each role prints a different title from the *same* method call.
4. Open `models/product.py` to show a second example of encapsulation (`__price`, `__old_price`).

## 16. Deployment Instructions

This app is deployment-ready for any platform that runs a standard Flask app (Render, Railway, PythonAnywhere, etc).

1. Set a real `SECRET_KEY` environment variable in your hosting platform (do not use the default demo key in production):
   ```bash
   export SECRET_KEY="your-own-random-secret-key"
   ```
2. Use a production WSGI server (e.g. `gunicorn app:app`) instead of the Flask development server for real deployments.
3. Remember: because storage is in-memory Python lists, data resets on every restart/deploy. This is expected and documented behavior for this school project.

## 17. GitHub Instructions

```bash
git init
git add .
git commit -m "Initial commit - ML TopUp Lite"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

The included `.gitignore` excludes virtual environments, `__pycache__`, and other local files.

## 18. Known Limitation

**Data does not persist.** Since this project intentionally uses only Python lists (no database), any registered users, created products, or placed orders will be lost when the Flask application restarts. Demo accounts and demo products are automatically re-seeded on every startup so the app is always ready to test.

## 19. Project Structure

```
ml_topup_lite/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── models/
│   ├── __init__.py
│   ├── user.py        (User, Customer, Staff, Admin - inheritance/encapsulation/polymorphism)
│   ├── product.py
│   └── order.py
├── services/
│   ├── __init__.py
│   ├── storage.py      (Python list storage - NO DATABASE)
│   ├── auth_service.py (validation, login/role decorators)
│   ├── product_service.py
│   └── order_service.py
├── routes/
│   ├── __init__.py
│   ├── auth_routes.py
│   ├── customer_routes.py
│   ├── staff_routes.py
│   └── admin_routes.py
├── templates/
│   ├── base.html, index.html, login.html, register.html
│   ├── errors/ (403.html, 404.html, 500.html)
│   ├── customer/ (dashboard, topup, checkout, orders, order_detail, profile)
│   ├── staff/ (dashboard, orders, order_detail)
│   └── admin/ (dashboard, products, product_form, users, orders, order_detail)
└── static/
    ├── css/style.css
    └── js/app.js
```
