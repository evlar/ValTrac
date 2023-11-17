import re

def is_valid_address(address):
    """Validate an address with a specific pattern."""
    pattern = r'^[A-Za-z0-9]{48}$'
    return re.match(pattern, address) is not None

# Example usage:
# address = "someAddress123"
# if is_valid_address(address):
#     print("Valid address")
# else:
#     print("Invalid address")
