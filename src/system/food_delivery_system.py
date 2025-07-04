from models.customer import Customer
from models.order import Order
from models.delivery_agent import DeliveryAgent
from models.manager import Manager
from system.persistence import save_system, load_system
import datetime

class FoodDeliverySystem:
    _instance = None

    def __init__(self):
        """Initialize the food delivery system with default data."""
        self.customers = {}         # username -> Customer
        self.all_orders = []        # List of Order objects
        self.delivery_agents = {}   # agent_id -> DeliveryAgent
        self.promo_codes = {}       # promo_code -> discount percentage
        
        # Add some default promo codes
        self.promo_codes["WELCOME50"] = 50
        self.promo_codes["SAVE10"] = 10
        self.promo_codes["FREESHIP"] = 15
        
        # Pre-populate delivery agents
        self.delivery_agents["DA1"] = DeliveryAgent("DA1", "Agent A")
        self.delivery_agents["DA2"] = DeliveryAgent("DA2", "Agent B")
        
        # Manager with fixed credentials
        self.manager = Manager("manager", "manager123")

    @classmethod
    def get_instance(cls):
        """Get or create the singleton instance of the system."""
        if cls._instance is None:
            cls._instance = load_system(cls)
        return cls._instance

    def save_state(self) -> None:
        """Save the current state of the system."""
        save_system(self)

    def register_customer(self, username: str, password: str, name: str) -> Customer:
        """
        Register a new customer.
        """
        if username in self.customers:
            raise ValueError("Username already exists.")
        customer = Customer(username, password, name)
        self.customers[username] = customer
        self.save_state()
        return customer

    def login_customer(self, username: str, password: str) -> Customer:
        """
        Authenticate a customer.
        """
        if username not in self.customers:
            raise ValueError("Username not found. Please register first.")
        customer = self.customers[username]
        if customer.password != password:
            raise ValueError("Incorrect password.")
        return customer

    # Update the place_order method to better handle delivery agent assignment
    def place_order(self, customer: Customer, order_type: str, items: dict, 
                    special_instructions: str = "", discount: float = 0, 
                    promo_code: str = None) -> Order:
        """
        Place a new order.
        """
        # Apply promo code if provided
        if promo_code:
            if promo_code not in self.promo_codes:
                raise ValueError(f"Invalid promo code: {promo_code}")
            discount = self.promo_codes[promo_code]
            
        order = Order(customer.username, order_type, items, 
                      special_instructions=special_instructions, 
                      discount=discount)
        customer.place_order(order)
        self.all_orders.append(order)
        
        # Assign delivery agent for home delivery orders
        if order_type == "Home Delivery":
            assigned = False
            for agent in self.delivery_agents.values():
                if agent.is_available():
                    agent.assign_order(order)
                    assigned = True
                    break
                    
            if not assigned:
                # Mark the order as awaiting assignment
                order.status = "Awaiting Delivery Agent"
        
        self.save_state()
        return order

    # Add a method to check for unassigned orders and try to assign them
    def check_unassigned_orders(self) -> int:
        """
        Check for unassigned home delivery orders and try to assign them to available agents.
        """
        assigned_count = 0
        
        for agent in self.delivery_agents.values():
            agent.complete_order()
            assigned_count += 1
                    
        # Find all home delivery orders awaiting assignment
        unassigned_orders = [o for o in self.all_orders 
                            if o.order_type == "Home Delivery" 
                            and ((o.time_left() == "Order ready for pickup/delivery." and o.status == "Placed"))]
        
        # Try to assign them to available agents
        for order in unassigned_orders:
            for agent in self.delivery_agents.values():
                if agent.is_available() and order.status != "Delivering":
                    agent.assign_order(order)
                    assigned_count += 1
                    break
                    
        if assigned_count > 0:
            self.save_state()
            
        return assigned_count

    def get_customer_orders(self, customer: Customer) -> list:
        """Get all orders for a specific customer."""
        return customer.get_order_history()
    
    # Update the cancel_order method to check driver status
    def cancel_order(self, customer: Customer, order_id: str) -> bool:
        """
        Cancel an order if it hasn't been delivered yet.
        """
        for order in customer.get_order_history():
            if order.order_id == order_id:
                if order.status in ["Delivered", "Completed"]:
                    raise ValueError("Cannot cancel an order that has already been delivered.")
                    
                # Check if the order has a delivery agent and the status indicates they're on the way
                for agent in self.delivery_agents.values():
                    if agent.current_order and agent.current_order.order_id == order_id:
                        if order.status in ["Out for Delivery", "On the Way"]:
                            raise ValueError("Cannot cancel order as delivery agent is already on the way.")
                        # Free up the delivery agent
                        agent.current_order = None
                        break
                        
                order.status = "Cancelled"
                self.save_state()
                
                # After cancelling an order, check if we can assign agents to other orders
                self.check_unassigned_orders()
                
                return True
        
        raise ValueError(f"Order {order_id} not found.")
    
    def get_orders_by_date_range(self, customer: Customer, start_date: datetime.datetime, 
                                end_date: datetime.datetime) -> list:
        """
        Get orders within a date range.
        """
        filtered_orders = []
        for order in customer.get_order_history():
            if start_date <= order.order_time <= end_date:
                filtered_orders.append(order)
        return filtered_orders
    
    def update_customer_profile(self, username: str, name: str = None, address: str = None) -> None:
        """
        Update customer profile information.
        """
        if username not in self.customers:
            raise ValueError(f"Customer {username} not found.")
            
        customer = self.customers[username]
        if name:
            customer.name = name
        if address:
            customer.address = address
        
        self.save_state()
    
    def get_order_details(self, order_id: str) -> dict:
        """
        Get detailed information about an order.
        """
        for order in self.all_orders:
            if order.order_id == order_id:
                customer = self.customers.get(order.customer)
                details = {
                    "order_id": order.order_id,
                    "customer_username": order.customer,
                    "customer_name": customer.name if customer else "Unknown",
                    "order_type": order.order_type,
                    "items": order.items,
                    "status": order.status,
                    "order_time": order.order_time,
                    "estimated_time": order.estimated_time,
                    "special_instructions": order.special_instructions,
                    "discount": order.discount,
                    "total": order.calculate_total()
                }
                return details
        
        raise ValueError(f"Order {order_id} not found.")
    
    def rate_order(self, customer: Customer, order_id: str, rating: int, feedback: str = "") -> None:
        """
        Add rating and feedback to a delivered order.
        """
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5.")
            
        for order in customer.get_order_history():
            if order.order_id == order_id:
                if order.status != "Delivered":
                    raise ValueError("Can only rate orders that have been delivered.")
                order.rating = rating
                order.feedback = feedback
                self.save_state()
                return
                
        raise ValueError(f"Order {order_id} not found.")
    
    def update_notification_preferences(self, username: str, enabled: bool) -> None:
        """
        Update notification preferences for a customer.
        """
        if username not in self.customers:
            raise ValueError(f"Customer {username} not found.")
        
        self.customers[username].notifications_enabled = enabled
        self.save_state()
    
    def reorder_previous(self, customer: Customer, order_id: str) -> Order:
        """
        Create a new order with the same items as a previous order.
        """
        original_order = None
        for order in customer.get_order_history():
            if order.order_id == order_id:
                original_order = order
                break
                
        if not original_order:
            raise ValueError(f"Order {order_id} not found.")
        
        self.save_state()
            
        return self.place_order(
            customer,
            original_order.order_type,
            original_order.items.copy(),
            special_instructions=original_order.special_instructions
        )
        
    def mark_order_received(self, customer: Customer, order_id: str) -> bool:
        """
        Mark an order as received/picked up by the customer.
        """
        for order in customer.get_order_history():
            if order.order_id == order_id:
                # Check if the order is ready for pickup/delivery
                if order.estimated_time > datetime.datetime.now():
                    raise ValueError("This order is not ready for pickup/delivery yet.")
                    
                # For takeaway orders, we can mark it as completed directly
                if order.order_type == "Takeaway":
                    if order.status == "Completed" or order.status == "Picked Up":
                        raise ValueError("This order has already been picked up.")
                    order.status = "Picked Up"
                    self.save_state()
                    return True
                    
                # For home delivery orders, we need to check if it's out for delivery
                elif order.order_type == "Home Delivery":
                    if order.status not in ["Out for Delivery", "On the Way", "Delivered"]:
                        raise ValueError("This order is not out for delivery yet.")
                    if order.status == "Delivered":
                        raise ValueError("This order has already been marked as delivered.")
                        
                    # Find the delivery agent and update the status
                    for agent in self.delivery_agents.values():
                        if agent.current_order and agent.current_order.order_id == order_id:
                            order.status = "Delivered"
                            agent.current_order = None
                            self.save_state()
                            # Check for other unassigned orders
                            self.check_unassigned_orders()
                            return True
                    
                    # If we couldn't find the delivery agent, still mark it as delivered
                    order.status = "Delivered"
                    self.save_state()
                    return True
        
        raise ValueError(f"Order {order_id} not found.")