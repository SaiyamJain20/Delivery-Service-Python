from models.order import Order

class Customer:
    def __init__(self, username: str, password: str, name: str):
        """
        Initialize a new customer.
        """
        if not username or not password or not name:
            raise ValueError("Username, password, and name are required for registration.")
        self.username = username
        self.password = password
        self.name = name
        self.orders = []  # List of Order objects
        self.address = ""
        self.notifications_enabled = True

    def place_order(self, order: Order) -> None:
        """Add an order to the customer's order history."""
        self.orders.append(order)
        
    def get_order_history(self) -> list:
        """Return the customer's order history."""
        return self.orders