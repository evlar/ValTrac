import bittensor as bt
import re
import json
import logging
from decimal import Decimal
import os

logger = logging.getLogger(__name__)

# Get the absolute path of the current script
current_script_path = os.path.dirname(__file__)

# Construct the relative paths
delegate_info_log_path = os.path.join(current_script_path, '../../logs/delegate_info(test).log')
payout_log_path = os.path.join(current_script_path, '../../logs/payment_history.log')


# Mock transfer function
def mock_transfer(wallet, dest, amount, **kwargs):
    print(f"Mock transfer: {amount} to {dest} from {wallet.name}")
    return True  # Simulate a successful transfer

def read_last_processed_block(payment_log_path):
    if not os.path.exists(payment_log_path) or os.path.getsize(payment_log_path) == 0:
        return None  # Indicates no previous payments

    with open(payment_log_path, 'r') as file:
        last_line = file.readlines()[-1]
        last_processed_block = int(last_line.split(',')[1])  # Assuming CSV format: payment_date, last_block, ...
        return last_processed_block

def update_payment_log(payment_log_path, start_block, end_block, payout_details):
    with open(payment_log_path, 'a') as file:
        for address, payout in payout_details.items():
            file.write(f"{start_block},{end_block},{address},{payout}\n")  # CSV format

def parse_log_file(file_path, start_block=None):
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
        block_number = int(block)
        if start_block is not None and block_number <= start_block:
            continue  # Skip blocks that have been processed

        try:
            delegate_info_json = json.loads(delegate_info)
            nominators_percent = delegate_info_json.get('nominators_percent', [])
            parsed_data.append({
                'timestamp': timestamp,
                'block': block_number,
                'nominators_percent': nominators_percent
            })
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON data at block {block}: {e}")

    return parsed_data

def calculate_payouts(parsed_data, payout_pool):
    address_sums = {}
    count = 0

    for entry in parsed_data:
        nominators_percent = entry['nominators_percent']
        count += 1

        for address, percent in nominators_percent:
            address_sums[address] = address_sums.get(address, Decimal('0')) + Decimal(str(percent))

    address_averages = {address: sum_val / count for address, sum_val in address_sums.items()}
    payouts = {address: (average * Decimal(str(payout_pool))).quantize(Decimal('1.000000000')) for address, average in address_averages.items()}

    return payouts

# Initialize subtensor connection
config = bt.subtensor.config()
network = "ws://127.0.0.1:9944"  # Update the network address if necessary

try:
    sub = bt.subtensor(config=config, network=network)
except Exception as e:
    print(f"Failed to connect to the Subtensor: {e}")
    exit(1)

# Prompt for wallet name
wallet_name = input("Enter your wallet name: ")

# Initialize user's sending wallet
try:
    user_wallet = bt.wallet(name=wallet_name)
except Exception as e:
    print(f"Failed to initialize wallet: {e}")
    exit(1)

# Main Script
# Main Script
payment_log_path = payout_log_path  # Use the variable defined above
last_processed_block = read_last_processed_block(payment_log_path)

file_path = delegate_info_log_path  # Use the variable defined above
parsed_data = parse_log_file(file_path, start_block=last_processed_block)

# Prompt for the payout pool amount
while True:
    try:
        payout_pool = Decimal(input("Enter the total payout pool amount: "))
        if payout_pool >= 0:
            break
        else:
            print("Please enter a non-negative number.")
    except (ValueError, decimal.InvalidOperation):
        print("Invalid input. Please enter a valid number.")

payouts = calculate_payouts(parsed_data, payout_pool)

# Display the payouts
print("\nCalculated Payouts:")
for address, payout in payouts.items():
    print(f"Address: {address}, Payout: {payout}")

# User confirmation
confirmation = input("\nDo you want to proceed with these transfers? (yes/no): ").lower()
if confirmation != 'yes':
    print("Transfer process aborted.")
    exit(0)

# Normal Transfer loop
#for address, payout in payouts.items():
 #   adjusted_payout = payout - Decimal('0.000000144')
  #  if adjusted_payout <= 0:
   #     print(f"Skipping transfer to address {address} due to non-positive payout after fee subtraction.")
    #    continue
#
 #   try:
  #      success = sub.transfer(
   #         wallet=user_wallet,
    #        dest=address,
     #       amount=adjusted_payout,
      #      wait_for_inclusion=True,
       #     wait_for_finalization=False,
        #    prompt=False
#        )
#
 #       if success:
  #          print(f"Successfully transferred to {address}")
   #     else:
    #        print(f"Failed to transfer to {address}")
#    except Exception as e:
 #       print(f"An error occurred while transferring to {address}: {e}")

# Add a dry run flag
dry_run = input("Is this a dry run? (yes/no): ").lower() == 'yes'

# Dry Run Transfer loop
for address, payout in payouts.items():
    adjusted_payout = payout - Decimal('0.000000144')
    if adjusted_payout <= 0:
        print(f"Skipping transfer to address {address} due to non-positive payout after fee subtraction.")
        continue

    try:
        if dry_run:
            # Perform mock transfer
            success = mock_transfer(user_wallet, address, adjusted_payout)
        else:
            # Perform actual transfer
            success = sub.transfer(
                wallet=user_wallet,
                dest=address,
                amount=adjusted_payout,
                wait_for_inclusion=True,
                wait_for_finalization=False,
                prompt=False
            )

        if success:
            print(f"{'Mock ' if dry_run else ''}Successfully transferred to {address}")
        else:
            print(f"Failed to transfer to {address}")
    except Exception as e:
        print(f"An error occurred while transferring to {address}: {e}")

# Assuming end_block is the last block in parsed_data
end_block = parsed_data[-1]['block'] if parsed_data else last_processed_block
update_payment_log(payment_log_path, last_processed_block or 0, end_block, payouts)