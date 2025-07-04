import os
import sys
import datetime
import unittest
import pickle

# Adjust path to import from src folder
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from system.food_delivery_system import FoodDeliverySystem
from models.order import Order
from models.customer import Customer
from utils.constants import PERSISTENCE_FILE

class TestFoodDeliverySystem(unittest.TestCase):
    def setUp(self):
        # Remove persistence file to ensure tests start fresh
        if os.path.exists(PERSISTENCE_FILE):
            os.remove(PERSISTENCE_FILE)
        # Reset singleton instance
        FoodDeliverySystem._instance = None
        self.system = FoodDeliverySystem.get_instance()

    def test_customer_registration_success(self):
        customer = self.system.register_customer("alice", "pass123", "Alice Smith")
        self.assertEqual(customer.username, "alice")
        self.assertEqual(customer.name, "Alice Smith")
        self.assertEqual(len(self.system.customers), 1)

    def test_duplicate_registration(self):
        self.system.register_customer("bob", "pass456", "Bob Johnson")
        with self.assertRaises(ValueError):
            self.system.register_customer("bob", "anotherpass", "Robert Johnson")

    def test_customer_login_success(self):
        self.system.register_customer("charlie", "pass789", "Charlie Brown")
        customer = self.system.login_customer("charlie", "pass789")
        self.assertEqual(customer.username, "charlie")

    def test_customer_login_wrong_password(self):
        self.system.register_customer("dave", "pass000", "Dave Matthews")
        with self.assertRaises(ValueError):
            self.system.login_customer("dave", "wrongpass")

    def test_customer_login_nonexistent(self):
        with self.assertRaises(ValueError):
            self.system.login_customer("nonuser", "nopass")

    def test_place_home_delivery_order_success(self):
        customer = self.system.register_customer("eve", "pass111", "Eve Adams")
        items = {"Pizza": 2, "Burger": 1}
        order = self.system.place_order(customer, "Home Delivery", items)
        self.assertEqual(order.order_type, "Home Delivery")
        self.assertIn(order, self.system.all_orders)
        # Test that the order is added to the customer's order history
        self.assertIn(order, customer.orders)

    def test_place_takeaway_order_success(self):
        customer = self.system.register_customer("frank", "pass222", "Frank Ocean")
        items = {"Salad": 1}
        order = self.system.place_order(customer, "Takeaway", items)
        self.assertEqual(order.order_type, "Takeaway")
        # Test that order is accessible through customer's get_order_history method
        self.assertIn(order, customer.get_order_history())

    def test_place_order_empty_items(self):
        customer = self.system.register_customer("grace", "pass333", "Grace Hopper")
        with self.assertRaises(ValueError):
            self.system.place_order(customer, "Home Delivery", {})

    def test_place_order_invalid_order_type(self):
        customer = self.system.register_customer("heidi", "pass444", "Heidi Klum")
        items = {"Sushi": 1}
        with self.assertRaises(ValueError):
            self.system.place_order(customer, "Delivery", items)  # "Delivery" is not valid, should be "Home Delivery"

    def test_order_estimated_time_home_delivery(self):
        customer = self.system.register_customer("ivan", "pass555", "Ivan Ivanov")
        items = {"Pasta": 1}
        order = self.system.place_order(customer, "Home Delivery", items)
        expected = order.order_time + datetime.timedelta(minutes=2)
        self.assertAlmostEqual(order.estimated_time.timestamp(), expected.timestamp(), delta=5)

    def test_order_estimated_time_takeaway(self):
        customer = self.system.register_customer("judy", "pass666", "Judy Garland")
        items = {"Burger": 1}
        order = self.system.place_order(customer, "Takeaway", items)
        expected = order.order_time + datetime.timedelta(minutes=10)
        self.assertAlmostEqual(order.estimated_time.timestamp(), expected.timestamp(), delta=5)

    def test_time_left_format(self):
        customer = self.system.register_customer("kate", "pass777", "Kate Winslet")
        items = {"Salad": 1}
        order = self.system.place_order(customer, "Takeaway", items)
        time_left = order.time_left()
        self.assertIsInstance(time_left, str)
        self.assertNotEqual(time_left, "")

    def test_manager_dashboard_report(self):
        cust1 = self.system.register_customer("leo", "pass888", "Leonardo DiCaprio")
        cust2 = self.system.register_customer("mia", "pass999", "Mia Wallace")
        self.system.place_order(cust1, "Home Delivery", {"Pizza": 1})
        self.system.place_order(cust2, "Takeaway", {"Burger": 2})
        # Updated to pass all_orders directly since we changed the view_restaurant_pov function
        report = self.system.manager.view_restaurant_pov(self.system.all_orders)
        self.assertIn("Total Orders:", report)
        self.assertIn("Home Delivery Orders:", report)
        self.assertIn("Revenue:", report)

    def test_multiple_orders_same_customer(self):
        customer = self.system.register_customer("nick", "passaaa", "Nick Cave")
        items1 = {"Pizza": 1}
        items2 = {"Sushi": 2}
        order1 = self.system.place_order(customer, "Home Delivery", items1)
        order2 = self.system.place_order(customer, "Takeaway", items2)
        self.assertEqual(len(customer.orders), 2)
        # Test the get_customer_orders method
        orders = self.system.get_customer_orders(customer)
        self.assertEqual(len(orders), 2)

    def test_delivery_agent_assignment(self):
        customer = self.system.register_customer("olivia", "passbbb", "Olivia Newton")
        order = self.system.place_order(customer, "Home Delivery", {"Burger": 1})
        assigned = False
        for agent in self.system.delivery_agents.values():
            if agent.current_order and agent.current_order.order_id == order.order_id:
                assigned = True
                break
        self.assertTrue(assigned)

    def test_persistence_after_order(self):
        customer = self.system.register_customer("peter", "passccc", "Peter Parker")
        self.system.place_order(customer, "Takeaway", {"Pasta": 1})
        # Force reloading by resetting singleton
        FoodDeliverySystem._instance = None
        new_system = FoodDeliverySystem.get_instance()
        self.assertIn("peter", new_system.customers)
        self.assertGreater(len(new_system.all_orders), 0)

    def test_order_with_negative_quantity(self):
        customer = self.system.register_customer("quinn", "passddd", "Quinn Fabray")
        with self.assertRaises(ValueError):
            self.system.place_order(customer, "Home Delivery", {"Pizza": -1})

    def test_invalid_menu_item_in_order(self):
        customer = self.system.register_customer("rachel", "passeee", "Rachel Green")
        with self.assertRaises(ValueError):
            self.system.place_order(customer, "Takeaway", {"Ice Cream": 1})

    def test_manager_login_credentials(self):
        # Check that manager credentials are fixed
        self.assertEqual(self.system.manager.username, "manager")
        self.assertEqual(self.system.manager.password, "manager123")

    def test_registration_invalid_parameters(self):
        with self.assertRaises(ValueError):
            # Empty username should raise error
            self.system.register_customer("", "pass", "NoName")
        with self.assertRaises(ValueError):
            # Empty password
            self.system.register_customer("sam", "", "Sam Smith")
        with self.assertRaises(ValueError):
            # Empty name
            self.system.register_customer("tom", "pass", "")
    
    def test_order_calculate_total(self):
        customer = self.system.register_customer("victor", "passxyz", "Victor Hugo")
        items = {"Pizza": 2, "Burger": 1}  # 2*12.99 + 1*8.99 = 34.97
        order = self.system.place_order(customer, "Home Delivery", items)
        total = order.calculate_total()
        self.assertAlmostEqual(total, 34.97, places=2)
    
    def test_delivery_agent_is_available(self):
        # Initially all agents should be available
        for agent in self.system.delivery_agents.values():
            self.assertTrue(agent.is_available())
        
        # Assign an order to the first agent
        customer = self.system.register_customer("walter", "passzzz", "Walter White")
        order = self.system.place_order(customer, "Home Delivery", {"Pizza": 1})
        
        # At least one agent should now be unavailable
        unavailable_found = False
        for agent in self.system.delivery_agents.values():
            if not agent.is_available():
                unavailable_found = True
                break
        self.assertTrue(unavailable_found)
    
    def test_delivery_agent_update_status(self):
        customer = self.system.register_customer("xavier", "passqwe", "Xavier Charles")
        order = self.system.place_order(customer, "Home Delivery", {"Pasta": 1})
        
        # Find the agent assigned to this order
        assigned_agent = None
        for agent in self.system.delivery_agents.values():
            if agent.current_order and agent.current_order.order_id == order.order_id:
                assigned_agent = agent
                break
        
        self.assertIsNotNone(assigned_agent)
        assigned_agent.update_order_status("Out for Delivery")
        self.assertEqual(order.status, "Out for Delivery")

    def test_cancel_order_already_delivered(self):
        customer = self.system.register_customer("zack", "pass456", "Zack Morris")
        items = {"Burger": 1}
        order = self.system.place_order(customer, "Home Delivery", items)
        # Manually change order status to delivered
        order.status = "Delivered"
        with self.assertRaises(ValueError):
            self.system.cancel_order(customer, order.order_id)

    def test_order_history_by_date_range(self):
        customer = self.system.register_customer("aaron", "pass789", "Aaron Paul")
        # Create orders with different dates
        items = {"Pizza": 1}
        # Create an order with a past date
        order1 = Order(customer, "Takeaway", items)
        order1.order_time = datetime.datetime.now() - datetime.timedelta(days=10)
        customer.orders.append(order1)
        self.system.all_orders.append(order1)
        
        # Add a recent order
        order2 = self.system.place_order(customer, "Home Delivery", items)
        
        # Get orders from last 7 days
        recent_orders = self.system.get_orders_by_date_range(
            customer, 
            datetime.datetime.now() - datetime.timedelta(days=7),
            datetime.datetime.now()
        )
        self.assertEqual(len(recent_orders), 1)
        self.assertEqual(recent_orders[0].order_id, order2.order_id)

    def test_add_special_instructions_to_order(self):
        customer = self.system.register_customer("betty", "passabc", "Betty White")
        items = {"Pasta": 1}
        instructions = "Extra cheese please, no garlic"
        order = self.system.place_order(customer, "Home Delivery", items, special_instructions=instructions)
        self.assertEqual(order.special_instructions, instructions)

    def test_order_with_discount(self):
        customer = self.system.register_customer("carlos", "passdef", "Carlos Santana")
        items = {"Pizza": 2, "Burger": 1}  # 2*12.99 + 1*8.99 = 34.97
        discount_percentage = 10  # 10% discount
        order = self.system.place_order(customer, "Takeaway", items, discount=discount_percentage)
        total = order.calculate_total()
        expected_total = 34.97 * 0.9  # 10% off
        self.assertAlmostEqual(total, expected_total, places=2)

    def test_order_with_invalid_discount(self):
        customer = self.system.register_customer("diana", "passghi", "Diana Ross")
        items = {"Burger": 1}
        with self.assertRaises(ValueError):
            self.system.place_order(customer, "Takeaway", items, discount=101)  # Invalid discount percentage

    def test_customer_update_profile(self):
        customer = self.system.register_customer("edward", "passjkl", "Edward Norton")
        new_name = "Edward James Norton"
        new_address = "123 Main St, New York"
        self.system.update_customer_profile(customer.username, new_name, new_address)
        updated_customer = self.system.customers.get("edward")
        self.assertEqual(updated_customer.name, new_name)
        self.assertEqual(updated_customer.address, new_address)

    def test_get_order_details(self):
        customer = self.system.register_customer("felicia", "passmno", "Felicia Day")
        items = {"Pizza": 1, "Burger": 2}
        order = self.system.place_order(customer, "Home Delivery", items)
        order_details = self.system.get_order_details(order.order_id)
        self.assertEqual(order_details["customer_name"], "Felicia Day")
        self.assertEqual(order_details["order_type"], "Home Delivery")
        self.assertEqual(order_details["items"]["Pizza"], 1)
        self.assertEqual(order_details["items"]["Burger"], 2)

    def test_rate_order(self):
        customer = self.system.register_customer("george", "passpqr", "George Clooney")
        items = {"Pasta": 1}
        order = self.system.place_order(customer, "Takeaway", items)
        # Set order to delivered
        order.status = "Delivered"
        rating = 4
        feedback = "Food was great but slightly cold"
        self.system.rate_order(customer, order.order_id, rating, feedback)
        self.assertEqual(order.rating, rating)
        self.assertEqual(order.feedback, feedback)

    def test_apply_promo_code(self):
        # Add a valid promo code to the system
        self.system.promo_codes = {"WELCOME50": 50}
        customer = self.system.register_customer("isaiah", "passvwx", "Isaiah Thomas")
        items = {"Pizza": 1}  # 12.99
        order = self.system.place_order(customer, "Takeaway", items, promo_code="WELCOME50")
        total = order.calculate_total()
        expected_total = 12.99 * 0.5  # 50% off
        self.assertAlmostEqual(total, expected_total, places=2)

    def test_invalid_promo_code(self):
        customer = self.system.register_customer("jasmine", "passyz1", "Jasmine Rice")
        items = {"Burger": 1}
        with self.assertRaises(ValueError):
            self.system.place_order(customer, "Takeaway", items, promo_code="INVALID")

    def test_customer_notification_setting(self):
        customer = self.system.register_customer("kevin", "pass234", "Kevin Hart")
        # Default should be True
        self.assertTrue(customer.notifications_enabled)
        # Update notification preferences
        self.system.update_notification_preferences(customer.username, False)
        self.assertFalse(customer.notifications_enabled)

    def test_manager_generate_popular_items_report(self):
        # Register customers and place orders with various items
        customer1 = self.system.register_customer("michael", "pass890", "Michael Scott")
        customer2 = self.system.register_customer("nina", "passabc", "Nina Dobrev")
        
        self.system.place_order(customer1, "Home Delivery", {"Pizza": 2, "Burger": 1})
        self.system.place_order(customer2, "Takeaway", {"Pizza": 1, "Pasta": 1})
        self.system.place_order(customer1, "Takeaway", {"Pizza": 1})
        
        # Generate popularity report
        report = self.system.manager.generate_popular_items_report(self.system.all_orders)
        self.assertIn("Pizza", report)
        self.assertIn("4", report)  # 4 pizzas ordered in total
        self.assertIn("Most Popular Item", report)

if __name__ == '__main__':
    unittest.main()