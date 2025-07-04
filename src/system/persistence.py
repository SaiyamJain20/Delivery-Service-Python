import os
import pickle
from utils.constants import PERSISTENCE_FILE

def save_system(system_instance) -> None:
    """
    Save the system state to a file.
    """
    with open(PERSISTENCE_FILE, "wb") as f:
        pickle.dump(system_instance, f)

def load_system(system_class):
    """
    Load the system state from a file if it exists.
    """
    if os.path.exists(PERSISTENCE_FILE):
        try:
            with open(PERSISTENCE_FILE, "rb") as f:
                return pickle.load(f)
        except (pickle.PickleError, EOFError, AttributeError):
            # If there's an error loading the file, create a new instance
            print("Error loading system state. Creating new system.")
            return system_class()
    return system_class()