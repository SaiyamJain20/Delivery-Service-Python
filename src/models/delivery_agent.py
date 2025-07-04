from models.order import Order
import datetime

class DeliveryAgent:
    def __init__(self, agent_id: str, name: str):
        """
        Initialize a new delivery agent.
        """
        self.agent_id = agent_id
        self.name = name
        self.order_time_left = None
        self.current_order = None  # Order assigned

    def assign_order(self, order: Order) -> None:
        """Assign an order to this delivery agent."""
        if order.estimated_time < datetime.datetime.now():
            self.current_order = order
            self.order_time_left = datetime.datetime.now() + datetime.timedelta(minutes=2)
            order.status = "Delivering"
    
    def complete_order(self) -> None:
        """Complete the current order."""
        if self.current_order: 
            # print(f"Order {self.current_order.order_id} completed by {self.name} - {self.order_time_left}.")
            if (self.order_time_left - datetime.datetime.now()).total_seconds() <= 0:
                self.current_order.status = "Completed"
                self.current_order = None
                self.order_time_left = None

    def update_order_status(self, status: str) -> None:
        """Update the status of the current order."""
        if self.current_order:
            self.current_order.status = status
            
    def is_available(self) -> bool:
        """Check if the agent is available to take a new order."""
        return self.current_order is None