"""
Order service - functions for order statistics used across dashboards.
"""
from services import storage


def get_customer_stats(customer_id):
    customer_orders = storage.get_orders_by_customer(customer_id)
    return {
        "total": len(customer_orders),
        "pending": len([o for o in customer_orders if o.status == "Pending"]),
        "completed": len([o for o in customer_orders if o.status == "Completed"]),
        "recent": sorted(customer_orders, key=lambda o: o.created_at, reverse=True)[:5],
    }


def get_staff_stats():
    all_orders = storage.get_all_orders()
    return {
        "total": len(all_orders),
        "pending": storage.count_orders_by_status("Pending"),
        "processing": storage.count_orders_by_status("Processing"),
        "completed": storage.count_orders_by_status("Completed"),
        "recent": sorted(all_orders, key=lambda o: o.created_at, reverse=True)[:10],
    }


def get_admin_stats():
    all_orders = storage.get_all_orders()
    return {
        "total_users": len(storage.get_all_users()),
        "total_customers": storage.count_users_by_role("customer"),
        "total_staff": storage.count_users_by_role("staff"),
        "total_products": len(storage.get_all_products()),
        "total_orders": len(all_orders),
        "pending": storage.count_orders_by_status("Pending"),
        "processing": storage.count_orders_by_status("Processing"),
        "completed": storage.count_orders_by_status("Completed"),
        "demo_sales_total": storage.total_sales(),
    }
