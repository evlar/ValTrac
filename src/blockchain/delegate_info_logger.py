import os
import sys
import time
import json
import requests
import bittensor as bt

# Navigate two levels up to the src directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import setup_logger

# Set up custom logging
log_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs', 'delegate_info.log')
logger = setup_logger('delegate_info_logger', log_file_path)

# Print the current working directory for debugging
print("Current working directory:", os.getcwd())

# Initialize subtensor connection
config = bt.subtensor.config()
network = "ws://127.0.0.1:9944"

try:
    sub = bt.subtensor(config=config, network=network)
    logger.info("Connected to Subtensor.")
except Exception as e:
    logger.error(f"Failed to connect to the Subtensor: {e}")
    exit(1)

# Function to fetch the price from the given URL
def fetch_price(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        price = data[0]['price']
        return price
    except requests.RequestException as e:
        logger.error(f"Failed to fetch price from {url}: {e}")
        return None

# Define the function get_delegate_info
def get_delegate_by_hotkey(hotkey_ss58_address, block=None):
    try:
        delegate_info = sub.get_delegate_by_hotkey(hotkey_ss58_address, block=block)
        if delegate_info is not None:
            # Find the delegate_stake by searching for the nominator that matches the owner_ss58 address
            delegate_stake = next((float(nominator[1]) for nominator in delegate_info.nominators if nominator[0] == delegate_info.owner_ss58), 0)

            # Calculate the remaining stake after removing the delegate stake
            remaining_stake = float(delegate_info.total_stake) - delegate_stake

            # Calculate the percentage stake for each nominator
            nominators_percent = [
                (nominator[0], (float(nominator[1]) / remaining_stake) if remaining_stake > 0 else 0)
                for nominator in delegate_info.nominators
            ]

            # Structure delegate_info into a dictionary, including 'nominators_percent', 'delegate_take', and 'price'.
            delegate_info_dict = {
                'hotkey_ss58': delegate_info.hotkey_ss58,
                'total_stake': float(delegate_info.total_stake),
                'nominators': [(nominator[0], float(nominator[1])) for nominator in delegate_info.nominators],
                'nominators_percent': nominators_percent,
                'owner_ss58': delegate_info.owner_ss58,
                'delegate_stake': delegate_stake,
                'take': float(delegate_info.take),
                'validator_permits': delegate_info.validator_permits,
                'registrations': delegate_info.registrations,
                'return_per_1000': f'{delegate_info.return_per_1000:.6f}',
                #'return_per_1000': f"{float(delegate_info.return_per_1000):.9f}",
                #'return_per_1000': f'{delegate[0].return_per_1000!s:6.6}'
                'total_daily_return': float(delegate_info.total_daily_return)
            }
            
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
            logger.info(f"Timestamp: {timestamp}, Block: {block if block is not None else 'latest'}, Delegate info for {hotkey_ss58_address}: {json.dumps(delegate_info_dict, ensure_ascii=False)}")
        else:
            logger.info(f"No delegate info found for {hotkey_ss58_address} at block {block if block is not None else 'latest'}.")
    except Exception as e:
        logger.error(f"Failed to get the delegate info for {hotkey_ss58_address}: {e}")

def get_current_block_number():
    try:
        current_block = sub.get_current_block()
        return current_block
    except Exception as e:
        logger.error(f"Failed to get the current block number: {e}")
        return None

def listen_to_chain_and_report(hotkey_ss58_address, report_every_n_blocks=300):
    last_reported_block = None
    price_url = 'https://taostats.io/data.json'

    while True:
        current_block = get_current_block_number()
        price = fetch_price(price_url)
        if current_block is not None and price is not None:
            if last_reported_block is None or current_block >= last_reported_block + report_every_n_blocks:
                logger.info(f"Reporting for block number: {current_block}, Price: {price}")
                get_delegate_by_hotkey(hotkey_ss58_address, current_block)
                last_reported_block = current_block
        else:
            time.sleep(60)
            continue
        time.sleep(10)


def main():
    # Ensure enough arguments are provided (script name, hotkey address, and network)
    if len(sys.argv) < 3:
        logger.error("Insufficient arguments provided. Exiting.")
        return

    # Extract the hotkey address and network address from the command-line arguments
    hotkey_ss58_address = sys.argv[1]
    network = sys.argv[2]

    # Initialize subtensor connection
    try:
        config = bt.subtensor.config()
        sub = bt.subtensor(config=config, network=network)
        logger.info(f"Connected to Subtensor at {network}.")
    except Exception as e:
        logger.error(f"Failed to connect to the Subtensor at {network}: {e}")
        exit(1)

    # Check the current block number
    current_block = get_current_block_number()
    if current_block is None:
        logger.error("Cannot obtain the current block number, terminating.")
        return

    logger.info("Script is starting logging immediately.")

    # Continue with the main logic of the script
    listen_to_chain_and_report(hotkey_ss58_address)

if __name__ == "__main__":
    main()