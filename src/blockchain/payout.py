import os
import time
import json
import pandas as pd
import bittensor as bt
import re
import csv
from ..utils.logger import setup_logger
from ..data_management.user_data import load_user_data

# Correct paths for script directory and log file
base_directory = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
log_file_path = os.path.join(base_directory, 'logs', 'payout_logger.log')
delegate_info_log_path = os.path.join(base_directory, 'logs', 'delegate_info.log')
payout_log_path = os.path.join(base_directory, 'logs', 'payout_log.csv')
user_data_path = os.path.join(base_directory, 'data', 'user_data.json')
referral_csv_path = os.path.join(base_directory, 'data', 'referral_layers.csv')

logger = setup_logger('payout_logger', log_file_path)

# Function to print text in green
def print_green(text, end='\n'):
    print("\033[92m" + text + "\033[0m", end=end)

def parse_log_file(file_path):
    log_pattern = re.compile(
        r"Timestamp: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}), Block: (\d+), "
        r"Delegate info for [\w\d]+: ({.*?})", 
        re.DOTALL
    )
    
    with open(file_path, 'r') as file:
        log_content = file.read()
    
    matches = log_pattern.findall(log_content)
    
    parsed_data = []
    for timestamp, block, delegate_info in matches:
        try:
            delegate_info_json = json.loads(delegate_info)
            nominators_percent = delegate_info_json.get('nominators_percent', [])
            parsed_data.append({
                'timestamp': timestamp,
                'block': int(block),
                'nominators_percent': nominators_percent
            })
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON data at block {block}: {e}")
    
    return parsed_data

def calculate_user_sums_and_averages(user_addresses, parsed_log_data, start_block, end_block):
    user_sums = {user: 0.0 for user in user_addresses}
    
    for entry in parsed_log_data:
        if start_block <= entry['block'] <= end_block:
            for nominator in entry['nominators_percent']:
                for user, addresses in user_addresses.items():
                    if nominator[0] in addresses:
                        user_sums[user] += nominator[1]
    
    block_count = 0
    for entry in parsed_log_data:
        if start_block <= entry['block'] <= end_block:
            block_count += 1
    user_averages = {
    user: ((user_sums[user] / block_count) if block_count > 0 else 0)
        for user in user_sums
    }
    
    return user_averages

def process_referral_structure(referral_data):
    referral_structure = {}
    for row in referral_data.itertuples(index=False):
        layer, referrer, tax, *referees = row
        tax = float(tax)
        referees = [r for r in referees if r]
        if layer not in referral_structure:
            referral_structure[layer] = {}
        referral_structure[layer][referrer] = {'Tax': tax, 'Referees': referees}
    return referral_structure

def calculate_payouts(referral_structure, base_percents, payout_pool_total):
    for layer in sorted(referral_structure.keys(), reverse=True):
        for referrer, data in referral_structure[layer].items():
            if referrer not in base_percents:
                continue
            referrer_tax = data['Tax']
            total_tax_collected = 0
            for referee in data['Referees']:
                if referee not in base_percents:
                    continue
                tax_amount = base_percents[referee] * referrer_tax
                base_percents[referee] -= tax_amount
                total_tax_collected += tax_amount
            base_percents[referrer] += total_tax_collected

    payouts = {user: round((base_percent * payout_pool_total) - 0.000000144, 9) for user, base_percent in base_percents.items()}
    return payouts

def log_payout_details(payouts, start_block, end_block, users_data, payout_pool_total):
    log_file_path = os.path.join(base_directory, 'logs', 'payout_log.csv')  # Use base_directory instead of script_dir
    mode = 'a' if os.path.exists(log_file_path) else 'w'
    
    with open(log_file_path, mode) as file:
        writer = csv.writer(file)
        if mode == 'w':
            writer.writerow(['Username', 'Address', 'Amount Paid', 'Start Block', 'End Block', 'Total Payout Pool'])
        
        for username, amount in payouts.items():
            address = users_data[username][0]
            writer.writerow([username, address, amount, start_block, end_block, payout_pool_total])

def get_new_start_block(log_file_path):
    if not os.path.exists(log_file_path):
        return None

    try:
        with open(log_file_path, 'r') as file:
            lines = file.readlines()
            if not lines:
                return None
            last_line = lines[-1]
            last_end_block = int(last_line.split(',')[-2])
            return last_end_block + 1
    except Exception as e:
        logger.error(f"Error reading payout log: {e}")
        return None

def main():
    # Initialize subtensor connection
    config = bt.subtensor.config()
    network = "ws://127.0.0.1:9944"  # Replace with your actual network address
    try:
        sub = bt.subtensor(config=config, network=network)
    except Exception as e:
        logger.error(f"Failed to connect to the Subtensor: {e}")
        return

    # Rest of your script logic
    new_start_block = get_new_start_block(payout_log_path)
    parsed_log_data = parse_log_file(delegate_info_log_path)
    latest_block = parsed_log_data[-1]['block'] if parsed_log_data else None

    start_block = new_start_block if new_start_block is not None else (parsed_log_data[0]['block'] if parsed_log_data else 0)
    end_block = latest_block if latest_block is not None else 0

    users_data = load_user_data(user_data_path)
    user_averages = calculate_user_sums_and_averages(users_data, parsed_log_data, start_block, end_block)

    payout_pool_total = float(input("Enter the total payout pool: "))

    referral_data = pd.read_csv(referral_csv_path)
    referral_structure = process_referral_structure(referral_data)

    payouts = calculate_payouts(referral_structure, user_averages, payout_pool_total)

    print("Calculated Payouts:")
    for user, payout in payouts.items():
        print_green(f"{user}: {payout}")

    # Error handling and transactions
    wallet_name = input("Please enter your wallet name to proceed with transactions: ")
    try:
        user_wallet = bt.wallet(name=wallet_name)
    except Exception as e:
        logger.error(f"Failed to initialize wallet: {e}")
        return

    all_transactions_successful = True
    for username, payout in payouts.items():
        address = users_data[username][0]
        if payout == 0:
            print(f"Skipping transfer to {username} due to zero amount.")
            continue

        try:
            success = sub.transfer(
                wallet=user_wallet,
                dest=address,
                amount=payout,
                wait_for_inclusion=True,
                wait_for_finalization=False,
                prompt=False
            )

            if success:
                print_green(f"Successfully transferred to {username}")
            else:
                all_transactions_successful = False
                logger.error(f"Failed to transfer to {username}")
        except Exception as e:
            all_transactions_successful = False
            logger.error(f"An error occurred while transferring to {username}: {e}")

    if all_transactions_successful:
        log_payout_details(payouts, start_block, end_block, users_data, payout_pool_total)
        print_green("Payout details logged successfully.")

if __name__ == "__main__":
    main()
