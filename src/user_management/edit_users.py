from ..data_management.user_data import load_user_data, save_user_data
import os

def display_users(data):
    for i, user in enumerate(data, start=1):
        print(f"{i}. {user}")
    print("Enter 'exit' to quit the program.")

def delete_address(data, user):
    if len(data[user]) == 1:
        confirm = input(f"Warning, deleting {user}'s only address will delete the user. Would you like to delete '{user}'? (yes/no): ")
        if confirm.lower() == 'yes':
            del data[user]
            print(f"User '{user}' deleted.")
    else:
        for i, address in enumerate(data[user], start=1):
            print(f"{i}. {address}")
        index = int(input("Enter the number of the address you want to delete: ")) - 1
        if 0 <= index < len(data[user]):
            del data[user][index]
            print(f"Address deleted from user '{user}'.")
        else:
            print("Invalid selection.")


def edit_users(file_path):
    data = load_user_data(file_path)

    while True:
        if not data:
            print("No users found.")
            break

        print("Select a user to edit:")
        display_users(data)
        selection = input("Enter the number or the name of the user, or 'exit' to quit: ")

        if selection.lower() == 'exit':
            break

        user_keys = list(data.keys())

        if selection.isdigit():
            user_selection = int(selection) - 1
            if 0 <= user_selection < len(user_keys):
                user_to_edit = user_keys[user_selection]
            else:
                print("Invalid user selection.")
                continue
        elif selection in user_keys:
            user_to_edit = selection
        else:
            print("User not found.")
            continue

        delete_address(data, user_to_edit)
        save_user_data(data, file_path)

def main():
    # Correct the path to point to the project root's 'data' directory
    base_directory = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_path = os.path.join(base_directory, 'data', 'user_data.json')
    edit_users(file_path)

if __name__ == "__main__":
    main()
