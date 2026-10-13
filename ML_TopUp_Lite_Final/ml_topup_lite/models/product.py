"""
Product model representing a Mobile Legends: Bang Bang diamond top-up package.
Demonstrates ENCAPSULATION via private price attributes with getters.
All prices are FICTIONAL / DEMO PRICES ONLY.
"""


class Product:
    def __init__(self, product_id, name, diamonds, bonus, price, old_price=None):
        self.id = product_id
        self.name = name
        self.diamonds = diamonds
        self.bonus = bonus
        self.__price = price          # ENCAPSULATION: private, demo price only
        self.__old_price = old_price  # ENCAPSULATION: private

    # ---------- Encapsulation: getters / setters ----------
    def get_price(self):
        return self.__price

    def set_price(self, new_price):
        self.__price = new_price

    def get_old_price(self):
        return self.__old_price

    def set_old_price(self, new_old_price):
        self.__old_price = new_old_price

    # ---------- Functions ----------
    def get_discount_percent(self):
        """Calculates the discount percentage vs the old price, if any."""
        if self.__old_price and self.__old_price > self.__price:
            discount = (self.__old_price - self.__price) / self.__old_price * 100
            return round(discount)
        return 0

    def total_diamonds(self):
        """Total diamonds including bonus."""
        return self.diamonds + self.bonus

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "diamonds": self.diamonds,
            "bonus": self.bonus,
            "price": self.get_price(),
            "old_price": self.get_old_price(),
            "discount_percent": self.get_discount_percent(),
            "total_diamonds": self.total_diamonds(),
        }

    def __repr__(self):
        return f"<Product id={self.id} name={self.name} price={self.get_price()}>"
