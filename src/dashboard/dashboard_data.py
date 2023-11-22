import datetime
import re
import json
import requests
import pandas as pd

def get_apr_and_take(log_file_path):
    """
    Parses the log file to extract 'take', 'total_daily_return', and 'total_stake' from the last entry
    and calculates the APR.

    :param log_file_path: Path to the delegate_info.log file.
    :return: A tuple containing the APR and the latest 'take' value.
    """
    total_daily_return = 0
    total_stake = 0
    take = 0

    with open(log_file_path, 'r') as file:
        for line in file:
            # Processing each line in the log file
            json_match = re.search(r'\{.*\}', line)
            if json_match:
                json_data = json.loads(json_match.group())

                # Extracting values if present in json_data
                if 'total_daily_return' in json_data and 'total_stake' in json_data:
                    total_daily_return = json_data['total_daily_return']
                    total_stake = json_data['total_stake']
                    take = json_data.get('take', 0)  # Default to 0 if 'take' is not in json_data

    apr = (total_daily_return / total_stake) * 365 if total_stake else 0
    return apr, take

def get_latest_user_stakes(log_file_path, json_file_path, user_name):
    """
    Finds the latest stake values for all identifiers associated with a given user name.
    
    :param log_file_path: Path to the delegate_info.log file.
    :param json_file_path: Path to the user_data.json file.
    :param user_name: The user name to search for.
    :return: A dictionary with user identifiers as keys and their latest stake information as values.
    """
    # Load user data from JSON file
    with open(json_file_path, 'r') as file:
        user_data = json.load(file)

    # Get identifiers for the given user name
    user_ids = user_data.get(user_name, [])
    
    # Dictionary to hold the latest stake for each user identifier
    latest_stakes = {user_id: None for user_id in user_ids}

    with open(log_file_path, 'r') as file:
        for line in file:
            timestamp_match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', line)
            json_match = re.search(r'\{.*\}', line)

            if timestamp_match and json_match:
                timestamp = datetime.datetime.strptime(timestamp_match.group(), '%Y-%m-%d %H:%M:%S')
                json_data = json.loads(json_match.group())

                nominators = json_data.get('nominators', [])
                for nominator in nominators:
                    nominator_id, stake = nominator
                    if nominator_id in user_ids:
                        current_entry = latest_stakes[nominator_id]
                        if current_entry is None or timestamp > current_entry['timestamp']:
                            latest_stakes[nominator_id] = {
                                'timestamp': timestamp,
                                'stake': stake
                            }

    return latest_stakes

def fetch_price():
    """
    Fetches the price from a hardcoded URL (https://taostats.io/data.json).
    
    :return: The fetched price or None if there's an error.
    """
    url = 'https://taostats.io/data.json'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        price = data[0]['price']
        return price
    except requests.RequestException as e:
        print(f"Failed to fetch price from {url}: {e}")
        return None
    
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

def calculate_user_base_and_adjusted_percent(username, user_data, parsed_delegate_info, referral_structure):
    def calculate_base_percent(user):
        user_addresses = user_data.get(user, [])
        return sum(percent for address, percent in last_block_entry['nominators_percent'] if address in user_addresses)

    last_block_entry = parsed_delegate_info[-1]
    all_base_percents = {user: calculate_base_percent(user) for user in user_data}

    def find_referrer_and_layer(user):
        for layer, refs in referral_structure.items():
            for referrer, data in refs.items():
                if user in data['Referees']:
                    return referrer, layer
        return None, None

    def calculate_adjusted_percent(user, all_base_percents):
        base_percent = all_base_percents.get(user, 0.0)
        referrer, layer = find_referrer_and_layer(user)
        if referrer and layer:
            referrer_tax = referral_structure[layer][referrer]['Tax']
            tax_deducted = base_percent * referrer_tax
            base_percent -= tax_deducted
        
        # Add tax from referees
        for ref_data in referral_structure.values():
            if user in ref_data:
                tax = ref_data[user]['Tax']
                for referee in ref_data[user]['Referees']:
                    if referee in all_base_percents:
                        base_percent += all_base_percents[referee] * tax
        
        return base_percent

    base_percent = all_base_percents.get(username, 0.0)
    adjusted_percent = calculate_adjusted_percent(username, all_base_percents)
    
    return base_percent, adjusted_percent

def parse_delegate_info(log_content):
    log_pattern = re.compile(
        r"Timestamp: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}), Block: (\d+), "
        r"Delegate info for [\w\d]+: ({.*?})", 
        re.DOTALL
    )
    
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
            # Handle error
            print(f"Error parsing JSON data at block {block}: {e}")
    
    return parsed_data

import matplotlib.pyplot as plt

