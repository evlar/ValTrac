import csv
import os
from ..utils.validators import is_valid_address
from ..data_management.user_data import load_user_data, save_user_data

def append_data(existing_data, new_data):
    for username, addresses in new_data.items():
        if username in existing_data:
            # Add only new and valid addresses
            existing_data[username] = list(set(existing_data[username] + [a for a in addresses if is_valid_address(a)]))
        else:
            existing_data[username] = [a for a in addresses if is_valid_address(a)]
    return existing_data

def convert_csv_to_json(csv_file_path, json_file_path):
    new_data = {}
    invalid_entries = {}

    with open(csv_file_path, mode='r', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile)
        next(csv_reader, None)  # Skip the header row
        for row in csv_reader:
            username = row[0]
            identifiers = [i for i in row[1:] if i and is_valid_address(i)]
            if username:
                new_data[username] = identifiers
                invalid_addresses = [i for i in row[1:] if i and not is_valid_address(i)]
                if invalid_addresses:
                    invalid_entries[username] = invalid_addresses

    if invalid_entries:
        print("Invalid address or addresses. Please make corrections and try again.")
        for user, addresses in invalid_entries.items():
            print(f"User: {user}, Invalid Addresses: {addresses}")
        return

    existing_data = load_user_data(json_file_path)

    if existing_data:
        choice = input("Would you like to append or replace the existing user data? (append/replace): ").lower()
        if choice == 'append':
            data_to_save = append_data(existing_data, new_data)
        else:
            data_to_save = new_data
    else:
        data_to_save = new_data

    save_user_data(data_to_save, json_file_path)

def main():
    csv_file_name = input("Enter the full path of the CSV file: ")
    csv_file_path = csv_file_name
    json_file_name = os.path.basename(csv_file_name).replace('.csv', '.json')
    json_file_path = os.path.join(os.path.dirname(csv_file_name), json_file_name)

    convert_csv_to_json(csv_file_path, json_file_path)

if __name__ == "__main__":
    main()


