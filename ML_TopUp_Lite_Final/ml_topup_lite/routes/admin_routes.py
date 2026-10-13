from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from services import storage, auth_service, order_service, product_service
from models import VALID_STATUSES

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard")
@auth_service.role_required("admin")
def dashboard():
    user = auth_service.current_user()
    stats = order_service.get_admin_stats()
    return render_template("admin/dashboard.html", user=user, stats=stats)


# ---------------------------------------------------------------------------
# PRODUCT MANAGEMENT (CRUD)
# ---------------------------------------------------------------------------
@admin_bp.route("/products")
@auth_service.role_required("admin")
def products():
    user = auth_service.current_user()
    all_products = storage.get_all_products()
    return render_template("admin/products.html", user=user, products=all_products)


@admin_bp.route("/products/new", methods=["GET", "POST"])
@auth_service.role_required("admin")
def product_create():
    user = auth_service.current_user()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        diamonds = request.form.get("diamonds", "")
        bonus = request.form.get("bonus", "0")
        price = request.form.get("price", "")
        old_price = request.form.get("old_price", "")

        errors = product_service.validate_product_form(name, diamonds, bonus, price, old_price)
        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("admin/product_form.html", user=user, product=None,
                                    form_action=url_for("admin.product_create"))

        storage.create_product(
            name=name,
            diamonds=int(diamonds),
            bonus=int(bonus or 0),
            price=float(price),
            old_price=float(old_price) if old_price else None,
        )
        flash("Product created successfully.", "success")
        return redirect(url_for("admin.products"))

    return render_template("admin/product_form.html", user=user, product=None,
                            form_action=url_for("admin.product_create"))


@admin_bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
@auth_service.role_required("admin")
def product_edit(product_id):
    user = auth_service.current_user()
    product = storage.find_product_by_id(product_id)
    if product is None:
        flash("Product not found.", "error")
        return redirect(url_for("admin.products"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        diamonds = request.form.get("diamonds", "")
        bonus = request.form.get("bonus", "0")
        price = request.form.get("price", "")
        old_price = request.form.get("old_price", "")

        errors = product_service.validate_product_form(name, diamonds, bonus, price, old_price)
        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("admin/product_form.html", user=user, product=product,
                                    form_action=url_for("admin.product_edit", product_id=product.id))

        storage.update_product(
            product_id=product.id,
            name=name,
            diamonds=int(diamonds),
            bonus=int(bonus or 0),
            price=float(price),
            old_price=float(old_price) if old_price else None,
        )
        flash("Product updated successfully.", "success")
        return redirect(url_for("admin.products"))

    return render_template("admin/product_form.html", user=user, product=product,
                            form_action=url_for("admin.product_edit", product_id=product.id))


@admin_bp.route("/products/<int:product_id>/delete", methods=["POST"])
@auth_service.role_required("admin")
def product_delete(product_id):
    product = storage.find_product_by_id(product_id)
    if product is None:
        flash("Product not found.", "error")
    else:
        storage.delete_product(product_id)
        flash("Product deleted successfully.", "success")
    return redirect(url_for("admin.products"))


# ---------------------------------------------------------------------------
# USER MANAGEMENT
# ---------------------------------------------------------------------------
@admin_bp.route("/users")
@auth_service.role_required("admin")
def users():
    user = auth_service.current_user()
    all_users = storage.get_all_users()
    return render_template("admin/users.html", user=user, users=all_users)


# Roles an admin is allowed to create from the "New User" form
CREATABLE_ROLES = ("staff", "customer")


@admin_bp.route("/users/new", methods=["GET", "POST"])
@auth_service.role_required("admin")
def user_create():
    user = auth_service.current_user()
    form_action = url_for("admin.user_create")

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        role = request.form.get("role", "")
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        errors = auth_service.validate_user_form(name, email, password, confirm)
        if role not in CREATABLE_ROLES:
            errors.append("Please choose a role: Staff or Customer.")
        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("admin/user_form.html", user=user, target=None,
                                   editing_self=False, form_action=form_action,
                                   form_values={"name": name, "email": email, "role": role})

        storage.create_user(name, email, password, role)
        flash(f"{role.capitalize()} account created successfully.", "success")
        return redirect(url_for("admin.users"))

    return render_template("admin/user_form.html", user=user, target=None,
                           editing_self=False, form_action=form_action,
                           form_values={"name": "", "email": "", "role": "customer"})


@admin_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@auth_service.role_required("admin")
def user_edit(user_id):
    user = auth_service.current_user()
    target = storage.find_user_by_id(user_id)
    if target is None:
        flash("User not found.", "error")
        return redirect(url_for("admin.users"))

    editing_self = (target.id == user.id)
    # An admin may edit staff, customers and THEIR OWN account (not other admins)
    if target.role == "admin" and not editing_self:
        flash("You can only edit your own admin account.", "error")
        return redirect(url_for("admin.users"))

    form_action = url_for("admin.user_edit", user_id=target.id)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        errors = auth_service.validate_user_form(name, email, password, confirm,
                                                 editing_user=target)
        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("admin/user_form.html", user=user, target=target,
                                   editing_self=editing_self, form_action=form_action,
                                   form_values={"name": name, "email": email,
                                                "role": target.role})

        storage.update_user(target.id, name, email, password or None)
        if editing_self:
            session["name"] = name   # keep the session in sync with the new name
            flash("Your profile was updated successfully.", "success")
        else:
            flash(f"{target.role.capitalize()} account updated successfully.", "success")
        return redirect(url_for("admin.users"))

    return render_template("admin/user_form.html", user=user, target=target,
                           editing_self=editing_self, form_action=form_action,
                           form_values={"name": target.name, "email": target.get_email(),
                                        "role": target.role})


@admin_bp.route("/profile")
@auth_service.role_required("admin")
def my_profile():
    """Shortcut: opens the edit form for the logged-in admin's own account."""
    user = auth_service.current_user()
    return redirect(url_for("admin.user_edit", user_id=user.id))


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@auth_service.role_required("admin")
def user_delete(user_id):
    current = auth_service.current_user()
    if user_id == current.id:
        flash("You cannot delete your own account while logged in.", "error")
        return redirect(url_for("admin.users"))

    target = storage.find_user_by_id(user_id)
    if target is None:
        flash("User not found.", "error")
    else:
        storage.delete_user(user_id)
        flash("User deleted successfully.", "success")
    return redirect(url_for("admin.users"))


# ---------------------------------------------------------------------------
# ORDER MANAGEMENT
# ---------------------------------------------------------------------------
@admin_bp.route("/orders")
@auth_service.role_required("admin")
def orders():
    user = auth_service.current_user()
    query = request.args.get("q", "").strip()
    all_orders = storage.get_all_orders()
    if query:
        all_orders = storage.search_orders(query, order_list=all_orders)
    all_orders = sorted(all_orders, key=lambda o: o.created_at, reverse=True)
    return render_template("admin/orders.html", user=user, orders=all_orders, query=query)


@admin_bp.route("/orders/<int:order_id>", methods=["GET", "POST"])
@auth_service.role_required("admin")
def order_detail(order_id):
    user = auth_service.current_user()
    order = storage.find_order_by_id(order_id)
    if order is None:
        flash("Order not found.", "error")
        return redirect(url_for("admin.orders"))

    if request.method == "POST":
        new_status = request.form.get("status", "")
        if new_status not in VALID_STATUSES:
            flash("Invalid order status selected.", "error")
        else:
            order.update_status(new_status)
            flash(f"Order {order.order_number} status updated to {new_status}.", "success")
        return redirect(url_for("admin.order_detail", order_id=order.id))

    return render_template("admin/order_detail.html", user=user, order=order,
                            statuses=VALID_STATUSES)
