# Import necessary modules from graph_generator and dashboard_data
import os
import json
import pandas as pd
# from graph_generator import plot_apr_over_time, plot_user_stake_and_value, plot_user_apr_over_time
from .graph_generator import plot_apr_over_time, plot_user_stake_and_value, plot_user_apr_over_time
from .dashboard_data import calculate_user_base_and_adjusted_percent, process_referral_structure, parse_delegate_info
from .dashboard_data import get_apr_and_take, get_latest_user_stakes, fetch_price

current_script_dir = os.path.dirname(os.path.abspath(__file__))

def display_user_balance():
    # Paths to your log and JSON data files
    log_file_path = os.path.join(current_script_dir, '../../logs/delegate_info.log')
    json_file_path = os.path.join(current_script_dir, '../../data/user_data.json')

    user_name = input("Enter the user name: ")

    # Fetch the latest stakes and prices
    latest_stakes = get_latest_user_stakes(log_file_path, json_file_path, user_name)
    current_price = fetch_price()

    if current_price is None:
        print("Failed to fetch the current price. Please try again later.")
        return

    # Ensure total_stake is calculated as a float
    total_stake = sum(float(stake_info['stake']) for stake_info in latest_stakes.values() if stake_info)

    # Convert current_price to float if it's not already
    try:
        current_price = float(current_price)
    except ValueError:
        print("Error: Invalid price format.")
        return

    total_balance_in_dollars = total_stake * current_price

    print(f"User: {user_name}")
    print(f"Total Stake: {total_stake}")
    print(f"Dollar Balance: ${total_balance_in_dollars:.2f}")
   # print("Debug - Latest Stakes in Display Function:", latest_stakes)

def calculate_user_apr(user_name, log_file_path, user_data_path, referral_data_path):
    # Get APR and take from the log file
    apr, take = get_apr_and_take(log_file_path)

    # Load user data from JSON file
    with open(user_data_path, 'r') as file:
        user_data = json.load(file)

    # Load referral structure from CSV
    referral_data = pd.read_csv(referral_data_path)
    referral_structure = process_referral_structure(referral_data)

    # Parse delegate info log file
    with open(log_file_path, 'r') as file:
        log_content = file.read()
    parsed_delegate_info = parse_delegate_info(log_content)

    # Calculate base and adjusted percent
    base_percent, adjusted_percent = calculate_user_base_and_adjusted_percent(user_name, user_data, parsed_delegate_info, referral_structure)

    # Calculate user APR
    if base_percent > 0:
        user_apr = apr * (take * (adjusted_percent - base_percent) / base_percent + 1)
    else:
        user_apr = 0

    return user_apr


def main_menu():
    while True:
        print("\nMain Menu:")
        print("1. Plot Global APR Over Time")
        print("2. Plot User APR Over Time")
        print("3. Plot User Tao Balance and Dollar Value")
        print("4. Display User Balance")
        print("5. Calculate User Base and Adjusted Percent")
        print("6. User APR")
        print("7. Exit")

        choice = input("Enter your choice (1/2/3/4/5/6): ")

        if choice == '1':
            log_file_path = os.path.join(current_script_dir, '../../logs/delegate_info.log')
            plot_apr_over_time(log_file_path)

        elif choice == '2':
            user_name = input("Enter the user name: ")
            delegate_info_log_path = os.path.join(current_script_dir, '../../logs/delegate_info.log')
            user_data_path = os.path.join(current_script_dir, '../../data/user_data.json')
            referral_data_path = os.path.join(current_script_dir, '../../data/referral_layers.csv')

            plot_user_apr_over_time(user_name, delegate_info_log_path, user_data_path, referral_data_path)

        elif choice == '3':
            user_name = input("Enter the user name: ")
            delegate_info_log_path = os.path.join(current_script_dir, '../../logs/delegate_info.log')
            user_data_path = os.path.join(current_script_dir, '../../data/user_data.json')
            plot_user_stake_and_value(user_name, delegate_info_log_path, user_data_path)

        elif choice == '4':
            display_user_balance()

        elif choice == '5':
            user_name = input("Enter the user name for base and adjusted percent calculation: ")
            delegate_info_log_path = os.path.join(current_script_dir, '../../logs/delegate_info.log')
            user_data_path = os.path.join(current_script_dir, '../../data/user_data.json')
            referral_data_path = os.path.join(current_script_dir, '../../data/referral_layers.csv')

            # Load user data from JSON
            with open(user_data_path, 'r') as file:
                user_data = json.load(file)

            # Load referral structure from CSV
            referral_data = pd.read_csv(referral_data_path)
            referral_structure = process_referral_structure(referral_data)

            # Parse delegate info log file
            with open(delegate_info_log_path, 'r') as file:
                log_content = file.read()
            parsed_delegate_info = parse_delegate_info(log_content)

            # Calculate base and adjusted percent
            base_percent, adjusted_percent = calculate_user_base_and_adjusted_percent(user_name, user_data, parsed_delegate_info, referral_structure)
            print(f"Base Percent for {user_name}: {base_percent}")
            print(f"Adjusted Percent for {user_name}: {adjusted_percent}")

        elif choice == '6':
            user_name = input("Enter the user name for APR calculation: ")
            delegate_info_log_path = os.path.join(current_script_dir, '../../logs/delegate_info.log')
            user_data_path = os.path.join(current_script_dir, '../../data/user_data.json')
            referral_data_path = os.path.join(current_script_dir, '../../data/referral_layers.csv')
    
            user_apr = calculate_user_apr(user_name, delegate_info_log_path, user_data_path, referral_data_path)
            print(f"APR for {user_name}: {user_apr}")


        elif choice == '7':
            print("Exiting the program.")
            break

        else:
            print("Invalid choice. Please select a valid option (1/2/3/4).")

if __name__ == "__main__":
    main_menu()
