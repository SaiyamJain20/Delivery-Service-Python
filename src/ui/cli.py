from utils.input_helpers import input_non_empty, input_int
from utils.constants import MENU, ORDER_TYPES
from system.persistence import load_system
import datetime
import sys

def main_menu(system):
    """Display and handle the main menu of the application."""
    while True:
        print("\n=== Online Food Delivery System ===")
        print("1. Customer Login")
        print("2. Customer Registration")
        print("3. Manager Login")
        print("4. Quit")
        
        choice = input_non_empty("Enter your choice: ")
        
        if choice == "1":
            handle_customer_login(system)
        elif choice == "2":
            handle_customer_registration(system)
        elif choice == "3":
            handle_manager_login(system)
        elif choice == "4":
            print("Exiting the system. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please try again.")

def handle_customer_login(system):
    """Handle the customer login process."""
    try:
        username = input_non_empty("Username: ")
        password = input_non_empty("Password: ")
        customer = system.login_customer(username, password)
        customer_menu(system, customer)
    except ValueError as ve:
        print("Login error:", ve)

def handle_customer_registration(system):
    """Handle the customer registration process."""
    try:
        username = input_non_empty("Choose a username: ")
        password = input_non_empty("Choose a password: ")
        name = input_non_empty("Your full name: ")
        system.register_customer(username, password, name)
        print("Registration successful. Please login to continue.")
    except ValueError as ve:
        print("Registration error:", ve)

def handle_manager_login(system):
    """Handle the manager login process."""
    username = input_non_empty("Manager Username: ")
    password = input_non_empty("Manager Password: ")
    if username == system.manager.username and password == system.manager.password:
        manager_menu(system)
    else:
        print("Invalid manager credentials.")

def customer_menu(system, customer):
    """Display and handle the customer menu."""
    while True:
        print(f"\nCustomer Menu ({customer.username})")
        print("1. Place Order")
        print("2. View My Orders")
        print("3. Cancel Order")
        print("4. Rate Order")
        print("5. Update Profile")
        print("6. Update Notification Preferences")
        print("7. Reorder Previous")
        print("8. Confirm Order Recieved/Picked Up")
        print("9. Logout")
        
        choice = input_non_empty("Enter your choice: ")
        
        system.check_unassigned_orders()
        if choice == "1":
            handle_place_order(system, customer)
        elif choice == "2":
            handle_view_orders(customer, system)
        elif choice == "3":
            handle_cancel_order(system, customer)
        elif choice == "4":
            handle_rate_order(system, customer)
        elif choice == "5":
            handle_update_profile(system, customer)
        elif choice == "6":
            handle_notification_preferences(system, customer)
        elif choice == "7":
            handle_reorder(system, customer)
        elif choice == "8":
            handle_confirm_order_received(system, customer)
        elif choice == "9":
            print("Logging out...")
            break
        else:
            print("Invalid choice. Please try again.")

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
            print(f"Sorry, {item_name} is not in our menu.")
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
    
    # Get special instructions
    special_instructions = input("Special instructions (optional): ")
    
    # Check for promo code
    promo_code = input("Enter promo code (leave empty if none): ")
    
    try:
        # Place order with special instructions and promo code if provided
        kwargs = {"special_instructions": special_instructions}
        if promo_code:
            kwargs["promo_code"] = promo_code
            
        order = system.place_order(customer, order_type, order_items, **kwargs)
        print("\nOrder placed successfully!")
        print(order)
    except ValueError as ve:
        print("Error placing order:", ve)

def handle_view_orders(customer, system):
    """Display the customer's order history."""
    orders = customer.get_order_history()
    if not orders:
        print("You have no orders.")
        return
        
    print("\n--- Your Order History ---")
    for i, order in enumerate(orders, 1):
        print(f"{i}. Order ID: {order.order_id}")
        print(f"   Type: {order.order_type}")
        print(f"   Items: {order.items}")
        print(f"   Date: {order.order_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"   Status: {order.status}")
        print(f"   Total: ${order.calculate_total():.2f}")
        if order.special_instructions:
            print(f"   Special Instructions: {order.special_instructions}")
            
        time_left = order.time_left()
        if time_left == "Order ready for pickup/delivery.":
            if order.status not in ["Picked Up", "Delivered", "Cancelled"]:
                if order.order_type == "Takeaway":
                    print(f"   Status: Ready for pickup!")
        elif order.status not in ["Picked Up", "Delivered", "Cancelled"]:
            print(f"   Time Left: {time_left}")
            
        print()
        
    # Option to filter by date range
    print("\nDo you want to filter orders by date range?")
    if input("Enter 'y' to filter: ").lower() == 'y':
        try:
            days = input_int("Enter number of days back to search: ", 1)
            start_date = datetime.datetime.now() - datetime.timedelta(days=days)
            end_date = datetime.datetime.now()
            filtered_orders = system.get_orders_by_date_range(customer, start_date, end_date)
            
            print(f"\n--- Orders from the last {days} days ---")
            if not filtered_orders:
                print("No orders found in this date range.")
            else:
                for i, order in enumerate(filtered_orders, 1):
                    print(f"{i}. Order ID: {order.order_id}")
                    print(f"   Date: {order.order_time.strftime('%Y-%m-%d %H:%M')}")
                    print(f"   Items: {order.items}")
                    print()
        except ValueError as ve:
            print("Error filtering orders:", ve)

def handle_cancel_order(system, customer):
    """Handle cancellation of an order."""
    orders = customer.get_order_history()
    if not orders:
        print("You have no orders to cancel.")
        return
        
    # Show only orders that can be cancelled
    cancelable_orders = [o for o in orders if o.status not in ["Delivered", "Completed", "Cancelled"]]
    if not cancelable_orders:
        print("You have no orders that can be cancelled.")
        return
        
    print("\n--- Orders Available for Cancellation ---")
    for i, order in enumerate(cancelable_orders, 1):
        print(f"{i}. Order ID: {order.order_id}")
        print(f"   Items: {order.items}")
        print(f"   Status: {order.status}")
        print()
        
    try:
        index = input_int("Enter order number to cancel (0 to go back): ", 0, len(cancelable_orders))
        if index == 0:
            return
            
        order_id = cancelable_orders[index-1].order_id
        if system.cancel_order(customer, order_id):
            print(f"Order {order_id} has been cancelled successfully.")
        else:
            print("Failed to cancel the order.")
    except ValueError as ve:
        print("Error cancelling order:", ve)

def handle_rate_order(system, customer):
    """Handle rating of a delivered order."""
    orders = customer.get_order_history()
    if not orders:
        print("You have no orders to rate.")
        return
        
    # Show only delivered orders that haven't been rated
    ratable_orders = [o for o in orders if o.status == "Delivered" and o.rating is None]
    if not ratable_orders:
        print("You have no delivered orders that need rating.")
        return
        
    print("\n--- Orders Available for Rating ---")
    for i, order in enumerate(ratable_orders, 1):
        print(f"{i}. Order ID: {order.order_id}")
        print(f"   Items: {order.items}")
        print(f"   Date: {order.order_time.strftime('%Y-%m-%d %H:%M')}")
        print()
        
    try:
        index = input_int("Enter order number to rate (0 to go back): ", 0, len(ratable_orders))
        if index == 0:
            return
            
        order_id = ratable_orders[index-1].order_id
        rating = input_int("Enter rating (1-5): ", 1, 5)
        feedback = input("Enter feedback (optional): ")
        
        system.rate_order(customer, order_id, rating, feedback)
        print(f"Thank you for rating your order!")
    except ValueError as ve:
        print("Error rating order:", ve)

def handle_update_profile(system, customer):
    """Handle updating customer profile information."""
    print("\n--- Update Your Profile ---")
    print(f"Current Name: {customer.name}")
    print(f"Current Address: {customer.address or 'Not set'}")
    
    name = input("Enter new name (leave empty to keep current): ")
    address = input("Enter new address (leave empty to keep current): ")
    
    if name or address:
        try:
            system.update_customer_profile(customer.username, 
                                          name=name if name else None, 
                                          address=address if address else None)
            print("Profile updated successfully.")
        except ValueError as ve:
            print("Error updating profile:", ve)
    else:
        print("No changes made to profile.")

def handle_notification_preferences(system, customer):
    """Handle updating notification preferences."""
    print("\n--- Notification Preferences ---")
    current_status = "Enabled" if customer.notifications_enabled else "Disabled"
    print(f"Current Status: {current_status}")
    
    print("1. Enable Notifications")
    print("2. Disable Notifications")
    print("3. Back")
    
    choice = input_non_empty("Enter your choice: ")
    
    if choice == "1":
        system.update_notification_preferences(customer.username, True)
        print("Notifications have been enabled.")
    elif choice == "2":
        system.update_notification_preferences(customer.username, False)
        print("Notifications have been disabled.")
    elif choice == "3":
        return
    else:
        print("Invalid choice.")

def handle_reorder(system, customer):
    """Handle reordering a previous order."""
    orders = customer.get_order_history()
    if not orders:
        print("You have no previous orders to reorder.")
        return
        
    print("\n--- Your Previous Orders ---")
    for i, order in enumerate(orders, 1):
        print(f"{i}. Order ID: {order.order_id}")
        print(f"   Type: {order.order_type}")
        print(f"   Items: {order.items}")
        print(f"   Date: {order.order_time.strftime('%Y-%m-%d %H:%M')}")
        print()
        
    try:
        index = input_int("Enter order number to reorder (0 to go back): ", 0, len(orders))
        if index == 0:
            return
            
        order_id = orders[index-1].order_id
        new_order = system.reorder_previous(customer, order_id)
        print("\nReorder placed successfully!")
        print(new_order)
    except ValueError as ve:
        print("Error reordering:", ve)

def handle_confirm_order_received(system, customer):
    """Handle confirming that an order has been received or picked up."""
    orders = customer.get_order_history()
    if not orders:
        print("You have no orders.")
        return
        
    ready_orders = []
    current_time = datetime.datetime.now()
    
    for order in orders:
        if order.order_type == "Takeaway" and order.status == "Placed" and order.estimated_time <= current_time:
            ready_orders.append(order)
        elif order.order_type == "Home Delivery" and order.status in ["Out for Delivery", "On the Way", "Ready for delivery!", "Awaiting Delivery Agent"] and order.estimated_time <= current_time:
            ready_orders.append(order)
    
    if not ready_orders:
        print("You have no orders ready for pickup/delivery confirmation.")
        return
        
    print("\n--- Orders Ready for Pickup/Delivery ---")
    for i, order in enumerate(ready_orders, 1):
        print(f"{i}. Order ID: {order.order_id}")
        print(f"   Type: {order.order_type}")
        print(f"   Items: {order.items}")
        print(f"   Status: {order.status}")
        print(f"   Time: {order.time_left()}")
        print()
        
    try:
        index = input_int("Enter order number to confirm received (0 to go back): ", 0, len(ready_orders))
        if index == 0:
            return
            
        order_id = ready_orders[index-1].order_id
        
        try:
            if system.mark_order_received(customer, order_id):
                order_type = ready_orders[index-1].order_type
                if order_type == "Takeaway":
                    print(f"Order {order_id} has been marked as picked up.")
                else:
                    print(f"Order {order_id} has been marked as delivered.")
                print("Thank you for confirming!")
                
                # Ask if they want to rate the order now
                if input("Would you like to rate this order now? (y/n): ").lower() == 'y':
                    rating = input_int("Enter rating (1-5): ", 1, 5)
                    feedback = input("Enter feedback (optional): ")
                    system.rate_order(customer, order_id, rating, feedback)
                    print("Thank you for your feedback!")
        except ValueError as ve:
            print(f"Error: {ve}")
            
    except ValueError as ve:
        print("Error selecting order:", ve)

def manager_menu(system):
    """Display and handle the manager menu."""
    while True:
        print("\nManager Menu")
        print("1. View Restaurant POV")
        print("2. Generate Popular Items Report")
        print("3. Logout")
        
        choice = input_non_empty("Enter your choice: ")
        
        system = load_system(type(system))
        
        if choice == "1":
            report = system.manager.view_restaurant_pov(system.all_orders)
            print("\n--- Restaurant Report ---")
            print(report)
        elif choice == "2":
            report = system.manager.generate_popular_items_report(system.all_orders)
            print("\n--- Popular Items Report ---")
            print(report)
        elif choice == "3":
            print("Logging out...")
            break
        else:
            print("Invalid choice. Please try again.")