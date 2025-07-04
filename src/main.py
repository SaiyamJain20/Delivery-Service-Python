from system.food_delivery_system import FoodDeliverySystem
from ui.cli import main_menu

def main():
    """Entry point of the application."""
    system = FoodDeliverySystem.get_instance()
    main_menu(system)

if __name__ == "__main__":
    main()