from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort

from services import storage, auth_service, product_service, order_service

customer_bp = Blueprint("customer", __name__, url_prefix="/customer")


@customer_bp.route("/dashboard")
@auth_service.role_required("customer")
def dashboard():
    user = auth_service.current_user()
    stats = order_service.get_customer_stats(user.id)
    return render_template("customer/dashboard.html", user=user, stats=stats)


@customer_bp.route("/topup", methods=["GET", "POST"])
@auth_service.role_required("customer")
def topup():
    """STEP 1 & 2: game account + product selection, shown on one page."""
    user = auth_service.current_user()
    products = storage.get_all_products()

    if request.method == "POST":
        game_id = request.form.get("game_id", "").strip()
        server_id = request.form.get("server_id", "").strip()
        product_id_str = request.form.get("product_id", "")

        errors = auth_service.validate_game_account(game_id, server_id)
        product = product_service.get_product_or_none(product_id_str)
        if product is None:
            errors.append("Please select a valid top-up product.")

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("customer/topup.html", user=user, products=products,
                                    game_id=game_id, server_id=server_id)

        # Stash selections in session for the checkout step
        session["pending_order"] = {
            "game_id": game_id,
            "server_id": server_id,
            "product_id": product.id,
        }
        return redirect(url_for("customer.checkout"))

    return render_template("customer/topup.html", user=user, products=products,
                            game_id="", server_id="")


@customer_bp.route("/checkout", methods=["GET", "POST"])
@auth_service.role_required("customer")
def checkout():
    """STEP 3 & 4: payment method + email, then creates the order."""
    user = auth_service.current_user()
    pending = session.get("pending_order")
    if not pending:
        flash("Please start your top-up from the beginning.", "error")
        return redirect(url_for("customer.topup"))

    product = storage.find_product_by_id(pending["product_id"])
    if product is None:
        flash("The selected product is no longer available.", "error")
        session.pop("pending_order", None)
        return redirect(url_for("customer.topup"))

    if request.method == "POST":
        payment_method = request.form.get("payment_method", "")
        email = request.form.get("email", "").strip()

        errors = auth_service.validate_checkout(product.id, payment_method, email)
        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("customer/checkout.html", user=user, product=product,
                                    pending=pending, email=email)

        order = storage.create_order(
            customer_id=user.id,
            game_id=pending["game_id"],
            server_id=pending["server_id"],
            product_id=product.id,
            product_name=product.name,
            price=product.get_price(),
            payment_method=payment_method,
            email=email,
        )
        session.pop("pending_order", None)
        flash(f"Order {order.order_number} created successfully!", "success")
        return redirect(url_for("customer.order_detail", order_id=order.id))

    return render_template("customer/checkout.html", user=user, product=product,
                            pending=pending, email=user.get_email())


@customer_bp.route("/orders")
@auth_service.role_required("customer")
def orders():
    user = auth_service.current_user()
    query = request.args.get("q", "").strip()
    my_orders = storage.get_orders_by_customer(user.id)
    if query:
        my_orders = storage.search_orders(query, order_list=my_orders)
    my_orders = sorted(my_orders, key=lambda o: o.created_at, reverse=True)
    return render_template("customer/orders.html", user=user, orders=my_orders, query=query)


@customer_bp.route("/orders/<int:order_id>")
@auth_service.role_required("customer")
def order_detail(order_id):
    user = auth_service.current_user()
    order = storage.find_order_by_id(order_id)
    if order is None:
        flash("Order not found.", "error")
        return redirect(url_for("customer.orders"))
    # Authorization: customers may only view their own orders
    if order.customer_id != user.id:
        flash("You are not authorized to view that order.", "error")
        abort(403)
    return render_template("customer/order_detail.html", user=user, order=order)


@customer_bp.route("/profile")
@auth_service.role_required("customer")
def profile():
    user = auth_service.current_user()
    return render_template("customer/profile.html", user=user)
