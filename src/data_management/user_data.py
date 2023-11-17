import json
import os

def load_user_data(file_path):
    """Load user data from a JSON file. Return empty dict if file doesn't exist."""
    if not os.path.exists(file_path):
        return {}  # Return an empty dict if file doesn't exist

    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def save_user_data(data, file_path):
    """Save user data to a JSON file."""
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)

# The example usage commented out below is for demonstration
# on how other scripts would use these functions.
# Example usage:
# try:
#     users = load_user_data('path/to/user_data.json')
#     # Process users...
#     save_user_data(users, 'path/to/user_data.json')
# except Exception as e:
#     print(f"Error: {e}")
