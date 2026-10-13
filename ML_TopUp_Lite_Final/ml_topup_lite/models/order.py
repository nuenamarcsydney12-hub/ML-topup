"""
Order model representing a Mobile Legends top-up order (demo only, no real payments).
"""

VALID_STATUSES = ["Pending", "Processing", "Completed", "Cancelled"]


class Order:
    def __init__(self, order_id, order_number, customer_id, game_id, server_id,
                 product_id, product_name, price, payment_method, email,
                 created_at, status="Pending"):
        self.id = order_id
        self.order_number = order_number
        self.customer_id = customer_id
        self.game_id = game_id
        self.server_id = server_id
        self.product_id = product_id
        self.product_name = product_name
        self.price = price
        self.payment_method = payment_method
        self.email = email
        self.status = status
        self.created_at = created_at

    def update_status(self, new_status):
        """Updates the order status if it is a valid status. Returns True/False."""
        if new_status in VALID_STATUSES:
            self.status = new_status
            return True
        return False

    def to_dict(self):
        return {
            "id": self.id,
            "order_number": self.order_number,
            "customer_id": self.customer_id,
            "game_id": self.game_id,
            "server_id": self.server_id,
            "product_id": self.product_id,
            "product_name": self.product_name,
            "price": self.price,
            "payment_method": self.payment_method,
            "email": self.email,
            "status": self.status,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def __repr__(self):
        return f"<Order {self.order_number} status={self.status}>"
