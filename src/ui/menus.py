from utils.input_helpers import input_non_empty, input_int
from utils.constants import MENU, ORDER_TYPES

def customer_menu(system, customer):
    """Display and handle the customer menu."""
    while True:
        print(f"\nCustomer Menu ({customer.username})")
        print("1. Place Order")
        print("2. View My Orders")
        print("3. Logout")
        
        choice = input_non_empty("Enter your choice: ")
        
        if choice == "1":
            handle_place_order(system, customer)
        elif choice == "2":
            handle_view_orders(customer)
        elif choice == "3":
            print("Logging out...")
            break
        else:
            print("Invalid choice. Try again.")

def handle_place_order(system, customer):
    """Handle the order placement process."""
    print("\n--- Menu Items ---")
    for item, price in MENU.items():
        print(f"{item}: ${price:.2f}")
    
    # Collect order items
    order_items = {}
    while True:
        item_name = input_non_empty("Enter item name to add (or type 'done' to finish): ")
        if item_name.lower() == "done":
            break
        if item_name not in MENU:
            print("Item not available. Try again.")
            continue
        quantity = input_int(f"Enter quantity for {item_name}: ", 1)
        order_items[item_name] = order_items.get(item_name, 0) + quantity
    
    if not order_items:
        print("No items added. Order cancelled.")
        return
    
    # Select order type
    order_type = ""
    while order_type not in ["1", "2"]:
        print("Select Order Type:")
        print("1. Home Delivery")
        print("2. Takeaway")
        order_type = input_non_empty("Enter 1 or 2: ")
    
    order_type = "Home Delivery" if order_type == "1" else "Takeaway"
    
    try:
        order = system.place_order(customer, order_type, order_items)
        print("\nOrder placed successfully!")
        print(order)
    except ValueError as ve:
        print("Error placing order:", ve)

def handle_view_orders(customer):
    """Display the customer's order history."""
    orders = customer.get_order_history()
    if not orders:
        print("You have no orders.")
    else:
        for order in orders:
            print("\n" + str(order))
            if order.order_type == "Home Delivery":
                print("Time left for delivery:", order.time_left())

def handle_cancel_order(system, customer):
    """Handle cancellation of an order."""
    orders = customer.get_order_history()
    if not orders:
        print("You have no orders to cancel.")
        return
        
    # Get all orders that are not completed or already cancelled
    active_orders = [o for o in orders if o.status not in ["Delivered", "Completed", "Cancelled"]]
    if not active_orders:
        print("You have no active orders that can be cancelled.")
        return
        
    print("\n--- Active Orders ---")
    for i, order in enumerate(active_orders, 1):
        print(f"{i}. Order ID: {order.order_id}")
        print(f"   Type: {order.order_type}")
        print(f"   Items: {order.items}")
        print(f"   Status: {order.status}")
        print(f"   Placed: {order.order_time.strftime('%Y-%m-%d %H:%M')}")
        print()
        
    try:
        index = input_int("Enter order number to cancel (0 to go back): ", 0, len(active_orders))
        if index == 0:
            return
            
        order_id = active_orders[index-1].order_id
        
        # Add confirmation
        confirm = input(f"Are you sure you want to cancel order {order_id}? (y/n): ").lower()
        if confirm != 'y':
            print("Cancellation aborted.")
            return
            
        try:
            if system.cancel_order(customer, order_id):
                print(f"Order {order_id} has been cancelled successfully.")
        except ValueError as ve:
            print(f"Error: {ve}")
            
    except ValueError as ve:
        print("Error selecting order:", ve)

def manager_menu(system):
    """Display and handle the manager menu."""
    while True:
        print("\nManager Menu")
        print("1. View Restaurant POV")
        print("2. Logout")
        
        choice = input_non_empty("Enter your choice: ")
        
        if choice == "1":
            report = system.manager.view_restaurant_pov(system.all_orders)
            print("\n--- Restaurant Dashboard ---")
            print(report)
        elif choice == "2":
            print("Logging out of Manager Mode...")
            break
        else:
            print("Invalid choice. Try again.")