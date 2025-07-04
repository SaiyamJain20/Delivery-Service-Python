import datetime
from utils.constants import MENU

class Manager:
    def __init__(self, username: str, password: str):
        """
        Initialize a new manager.
        """
        self.username = username
        self.password = password

    def view_restaurant_pov(self, all_orders: list) -> str:
        """
        Generate a report with restaurant statistics.
        """
        total_orders = len(all_orders)
        home_delivery = sum(1 for order in all_orders if order.order_type == "Home Delivery")
        takeaway = total_orders - home_delivery
        
        # Calculate revenue
        revenue = 0.0
        for order in all_orders:
            for item, qty in order.items.items():
                revenue += MENU.get(item, 0) * qty
                
        avg_delivery_time = self.calculate_avg_delivery_time(all_orders)
        
        report = (f"Total Orders: {total_orders}\n"
                  f"Home Delivery Orders: {home_delivery}\n"
                  f"Takeaway Orders: {takeaway}\n"
                  f"Revenue: ${revenue:.2f}\n"
                  f"Average Estimated Time: {avg_delivery_time}\n")
        return report

    def calculate_avg_delivery_time(self, orders: list) -> str:
        """
        Calculate the average estimated delivery time.
        """
        if not orders:
            return "N/A"
        total_seconds = sum((order.estimated_time - order.order_time).total_seconds() for order in orders)
        avg_seconds = total_seconds / len(orders)
        return str(datetime.timedelta(seconds=int(avg_seconds)))
        
    def generate_popular_items_report(self, all_orders: list) -> str:
        """
        Generate a report of popular items.
        """
        if not all_orders:
            return "No orders to analyze."
            
        # Count item popularity
        item_counts = {}
        for order in all_orders:
            for item, qty in order.items.items():
                if item not in item_counts:
                    item_counts[item] = 0
                item_counts[item] += qty
                
        # Sort items by popularity
        sorted_items = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Generate report
        report = "Popular Items Report:\n"
        report += "-" * 30 + "\n"
        
        for i, (item, count) in enumerate(sorted_items):
            report += f"{i+1}. {item}: {count} orders\n"
            
        if sorted_items:
            most_popular = sorted_items[0][0]
            report += f"\nMost Popular Item: {most_popular} with {sorted_items[0][1]} orders\n"
            
        return report