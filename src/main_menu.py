import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import json

def run_delegate_info_logger():
    python_interpreter = sys.executable
    script_dir = os.path.dirname(os.path.abspath(__file__))
    delegate_logger_path = os.path.join(script_dir, 'blockchain', 'delegate_info_logger.py')

    # Prompt for PM2 instance name and hotkey address
    pm2_instance_name = input("Enter PM2 instance name for the delegate info logger: ")
    hotkey_address = input("Enter the hotkey_ss58_address: ")

    # Ask if the user is running a local or remote Subtensor network
    subtensor_network_choice = input("Connect to local Subtensor network? (yes/no): ").strip().lower()
    if subtensor_network_choice == 'yes':
        network_address = "ws://127.0.0.1:9944"
    elif subtensor_network_choice == 'no':
        network_address = input("Enter the remote Subtensor network address: ").strip()
    else:
        print("Invalid response. Please enter 'yes' or 'no'.")
        return

    print(f"Starting delegate info logger with PM2 instance name '{pm2_instance_name}'...")
    os.system(f'pm2 start {python_interpreter} --name="{pm2_instance_name}" -- {delegate_logger_path} {hotkey_address} {network_address}')
    print("Delegate info logger is now running in the background.")

def run_payout():
    python_interpreter = sys.executable
    script_dir = os.path.dirname(os.path.abspath(__file__))
    payout_script_path = os.path.join(script_dir, 'blockchain', 'payout.py')

    # Ask if the user is running a local or remote Subtensor network
    subtensor_network_choice = input("Connect to local Subtensor network for payout? (yes/no): ").strip().lower()
    if subtensor_network_choice == 'yes':
        network_address = "ws://127.0.0.1:9944"
    elif subtensor_network_choice == 'no':
        network_address = input("Enter the remote Subtensor network address for payout: ").strip()
    else:
        print("Invalid response. Please enter 'yes' or 'no'.")
        return

    print("Starting payout process...")
    # os.system(f'{python_interpreter} {payout_script_path} {network_address}')
    os.system(f'{python_interpreter} -m src.blockchain.payout {network_address}')
    print("Payout process completed.")

def stop_delegate_info_logger():
    print("Stopping delegate info logger...")
    os.system('pm2 stop delegate_info_logger')
    print("Delegate info logger has been stopped.")

def main_menu():
    while True:
        print("\nMain Menu:")
        print("1. Begin logging delegate info")
        print("2. Send payout")
        print("3. Add users")
        print("4. Edit users")
        print("5. Add referral")
        print("6. Edit referrals")
        print("7. Charts and Statistics")
        print("8. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            run_delegate_info_logger()
        elif choice == '2':
            run_payout()
        elif choice == '3':
            add_users_submenu()
        elif choice == '4':
            os.system('python3 -m src.user_management.edit_users')
        elif choice == '5':
            os.system('python3 -m src.referral_management.add_referrals')
        elif choice == '6':
            os.system('python3 -m src.referral_management.edit_referrals')
        elif choice == '7':
            os.system('python3 -m src.dashboard.dashboard_menu')
        elif choice == '8':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

def add_users_submenu():
    while True:
        print("\nAdd Users Submenu:")
        print("1. Load users from CSV")
        print("2. Manual entry")
        print("3. Back to Main Menu")

        choice = input("Enter your choice: ")

        if choice == '1':
            os.system('python3 -m src.user_management.load_users')
        elif choice == '2':
            os.system('python3 -m src.user_management.manual_entry')
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main_menu()
