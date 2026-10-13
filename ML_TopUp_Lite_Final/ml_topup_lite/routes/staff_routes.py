from flask import Blueprint, render_template, request, redirect, url_for, flash

from services import storage, auth_service, order_service
from models import VALID_STATUSES

staff_bp = Blueprint("staff", __name__, url_prefix="/staff")


@staff_bp.route("/dashboard")
@auth_service.role_required("staff", "admin")
def dashboard():
    user = auth_service.current_user()
    stats = order_service.get_staff_stats()
    return render_template("staff/dashboard.html", user=user, stats=stats)


@staff_bp.route("/orders")
@auth_service.role_required("staff", "admin")
def orders():
    user = auth_service.current_user()
    query = request.args.get("q", "").strip()
    all_orders = storage.get_all_orders()
    if query:
        all_orders = storage.search_orders(query, order_list=all_orders)
    all_orders = sorted(all_orders, key=lambda o: o.created_at, reverse=True)
    return render_template("staff/orders.html", user=user, orders=all_orders, query=query)


@staff_bp.route("/orders/<int:order_id>", methods=["GET", "POST"])
@auth_service.role_required("staff", "admin")
def order_detail(order_id):
    user = auth_service.current_user()
    order = storage.find_order_by_id(order_id)
    if order is None:
        flash("Order not found.", "error")
        return redirect(url_for("staff.orders"))

    if request.method == "POST":
        new_status = request.form.get("status", "")
        if new_status not in VALID_STATUSES:
            flash("Invalid order status selected.", "error")
        else:
            order.update_status(new_status)
            flash(f"Order {order.order_number} status updated to {new_status}.", "success")
        return redirect(url_for("staff.order_detail", order_id=order.id))

    return render_template("staff/order_detail.html", user=user, order=order,
                            statuses=VALID_STATUSES)
