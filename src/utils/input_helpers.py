def input_non_empty(prompt: str) -> str:
    """Get non-empty input from user."""
    while True:
        s = input(prompt).strip()
        if s:
            return s
        print("Input cannot be empty. Please try again.")

def input_int(prompt: str, min_val: int = None, max_val: int = None) -> int:
    """Get integer input from user with optional range validation."""
    while True:
        try:
            value = int(input(prompt).strip())
            if (min_val is not None and value < min_val) or (max_val is not None and value > max_val):
                print(f"Value must be between {min_val} and {max_val}.")
                continue
            return value
        except ValueError:
            print("Invalid integer. Please try again.")

def input_float(prompt: str, min_val: float = None, max_val: float = None) -> float:
    """Get float input from user with optional range validation."""
    while True:
        try:
            value = float(input(prompt).strip())
            if (min_val is not None and value < min_val) or (max_val is not None and value > max_val):
                print(f"Value must be between {min_val} and {max_val}.")
                continue
            return value
        except ValueError:
            print("Invalid number. Please try again.")

def input_date(prompt: str) -> str:
    """Get a date in YYYY-MM-DD format."""
    while True:
        date_str = input(prompt).strip()
        if not date_str:
            return ""
        try:
            # Basic validation - doesn't check for valid dates like Feb 30
            parts = date_str.split('-')
            if len(parts) == 3 and len(parts[0]) == 4 and len(parts[1]) == 2 and len(parts[2]) == 2:
                return date_str
            print("Invalid date format. Please use YYYY-MM-DD.")
        except:
            print("Invalid date format. Please use YYYY-MM-DD.")