import os
from ..utils.validators import is_valid_address
from ..data_management.user_data import load_user_data, save_user_data

def address_exists(data, address):
    return any(address in addresses for addresses in data.values())

def update_user_addresses(file_path):
    data = load_user_data(file_path)

    while True:
        username = input("Enter a user name: ")

        if username in data:
            print(f"Username '{username}' already exists.")
            add_more = input(f"Would you like to add another address to '{username}'? (yes/no): ")
            if add_more.lower() != 'yes':
                continue
        else:
            data[username] = []

        while True:
            address = input("Enter an address for the user (in the correct format): ")
            if is_valid_address(address):
                if address_exists(data, address):
                    print("This address already exists. Please enter a different address.")
                    continue
                else:
                    data[username].append(address)
            else:
                print("Invalid address format. Please enter a valid address.")
                continue

            more = input("Would you like to add another address? (yes/no): ")
            if more.lower() != 'yes':
                break

        another = input("Would you like to update another user? (yes/no): ")
        if another.lower() != 'yes':
            break

    sorted_data = dict(sorted(data.items(), key=lambda item: item[0].lower()))
    save_user_data(sorted_data, file_path)

def main():
    # This should navigate up to the project root from the script's location
    base_directory = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    json_file_path = os.path.join(base_directory, 'data', 'user_data.json')
    update_user_addresses(json_file_path)

if __name__ == "__main__":
    main()
