import datetime
from utils.constants import MENU, ORDER_TYPES

class Order:
    def __init__(self, customer_username: str, order_type: str, items: dict, special_instructions: str = "", discount: float = 0):
        """
        Initialize a new order.
        """
        if order_type not in ORDER_TYPES:
            raise ValueError(f"Order type must be one of {ORDER_TYPES}.")
        if not items or not isinstance(items, dict):
            raise ValueError("Order must contain at least one item.")
        for item, qty in items.items():
            if qty <= 0:
                raise ValueError(f"Quantity for {item} must be positive.")
            if item not in MENU:
                raise ValueError(f"Item '{item}' is not available in the menu.")
        if discount < 0 or discount > 100:
            raise ValueError("Discount must be between 0 and 100 percent.")

        self.order_id = f"O-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{customer_username}"
        self.customer = customer_username
        self.order_type = order_type
        self.items = items
        self.order_time = datetime.datetime.now()
        self.estimated_time = self.calculate_estimated_time()
        self.status = "Placed"
        self.special_instructions = special_instructions
        self.discount = discount
        self.rating = None
        self.feedback = None

    def calculate_estimated_time(self) -> datetime.datetime:
        """Calculate the estimated delivery/pickup time based on order type."""
        delta = datetime.timedelta(minutes=2) if self.order_type == "Home Delivery" else datetime.timedelta(minutes=10)
        return self.order_time + delta

    def time_left(self) -> str:
        """Return the time left for the order to be ready or indicate it's ready."""
        if self.status in ["Picked Up", "Delivered", "Cancelled"]:
            if self.status == "Picked Up":
                return "Order has been picked up."
            elif self.status == "Delivered":
                return "Order has been delivered."
            else:
                return "Order was cancelled."
                
        remaining = self.estimated_time - datetime.datetime.now()
        if remaining.total_seconds() <= 0:
            return "Order ready for pickup/delivery."
        
        minutes, seconds = divmod(remaining.seconds, 60)
        hours, minutes = divmod(minutes, 60)
        
        if hours > 0:
            return f"{hours} hours, {minutes} minutes"
        else:
            return f"{minutes} minutes, {seconds} seconds"
            
    def is_ready_for_pickup(self) -> bool:
        """Check if an order is ready for pickup or delivery."""
        if self.status in ["Picked Up", "Delivered", "Cancelled"]:
            return False
            
        return datetime.datetime.now() >= self.estimated_time
    
    def calculate_total(self) -> float:
        """Calculate the total price of the order."""
        subtotal = sum(MENU.get(item, 0) * qty for item, qty in self.items.items())
        if self.discount > 0:
            subtotal *= (1 - self.discount / 100)
        return subtotal

    def __repr__(self) -> str:
        """String representation of the order."""
        return (f"OrderID: {self.order_id}\nType: {self.order_type}\nItems: {self.items}\n"
                f"Placed at: {self.order_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Estimated time: {self.estimated_time.strftime('%H:%M:%S')}\n"
                f"Status: {self.status}"
                + (f"\nSpecial Instructions: {self.special_instructions}" if self.special_instructions else "")
                + (f"\nDiscount: {self.discount}%" if self.discount > 0 else "")
                + (f"\nRating: {self.rating}/5" if self.rating is not None else ""))