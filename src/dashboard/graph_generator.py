import pandas as pd
import matplotlib.pyplot as plt
import datetime
import re
import json
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import matplotlib.ticker as mticker

def parse_log_file(file_path):
    """
    Parses the log file to extract timestamp, total_stake, and total_daily_return.
    """
    data_with_timestamps = []
    with open(file_path, 'r') as file:
        for line in file:
            timestamp_match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', line)
            json_match = re.search(r'\{.*\}', line)
            
            if timestamp_match and json_match:
                timestamp = datetime.datetime.strptime(timestamp_match.group(), '%Y-%m-%d %H:%M:%S')
                json_data = json.loads(json_match.group())
                
                if 'total_stake' in json_data and 'total_daily_return' in json_data:
                    data_with_timestamps.append({
                        'timestamp': timestamp,
                        'total_stake': json_data['total_stake'],
                        'total_daily_return': json_data['total_daily_return']
                    })
    return data_with_timestamps

def plot_apr_over_time(file_path):
    """
    Plots the APR over time from a log file.
    """
    log_data = parse_log_file(file_path)
    df = pd.DataFrame(log_data)
    df['APR'] = (df['total_daily_return'] / df['total_stake']) * 365

    plt.figure(figsize=(15, 7))
    plt.plot(df['timestamp'], df['APR'], label='APR', color='blue')
    plt.title('APR Over Time')
    plt.xlabel('Timestamp')
    plt.ylabel('APR (%)')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_user_stake_and_value(user_name, delegate_info_log_path, user_data_path):
    def parse_delegate_info_log_for_user(file_path, user_addresses):
        parsed_data = []
        with open(file_path, 'r') as file:
            for line in file:
                # Extracting the price from the log message
                price_match = re.search(r'Price: (\d+(\.\d+)?)', line)
                if price_match:
                    price = float(price_match.group(1))

                    # Extract JSON data and additional info from the next line
                    json_line = next(file, '')
                    json_match = re.search(r'Timestamp: (.*), Block: (\d+), Delegate info for .+: (\{.*\})', json_line)
                    if json_match:
                        timestamp, block_number, json_data = json_match.groups()
                        json_data = json.loads(json_data)

                        # Extract nominators
                        nominators = json_data.get('nominators', [])

                        # Calculate the user's total stake
                        user_stake = sum(stake for addr, stake in nominators if addr in user_addresses)

                        # Calculate dollar value
                        dollar_value = user_stake * price

                        parsed_data.append({
                            'timestamp': timestamp,
                            'block_number': int(block_number),
                            'user_stake': user_stake,
                            'dollar_value': dollar_value
                        })

        return parsed_data

    # Load user data
    with open(user_data_path, 'r') as file:
        user_data = json.load(file)
    user_addresses = user_data.get(user_name, [])

    # Parse the delegate_info.log file for the given user
    user_data = parse_delegate_info_log_for_user(delegate_info_log_path, user_addresses)

    # Convert timestamps to datetime objects and prepare data for plotting
    timestamps = [datetime.datetime.strptime(entry['timestamp'], '%Y-%m-%d %H:%M:%S') for entry in user_data]
    user_stakes = [entry['user_stake'] for entry in user_data]
    dollar_values = [entry['dollar_value'] for entry in user_data]

    # Create a plot with two y-axes
    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.plot(timestamps, user_stakes, 'b-', label='User Stake')
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Stake', color='b')
    ax1.tick_params(axis='y', labelcolor='b')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.xticks(rotation=45)

    # Set the formatter for the dollar values
    formatter = ticker.FormatStrFormatter('$%1.2f')
    ax2 = ax1.twinx()
    ax2.yaxis.set_major_formatter(formatter)

    ax2.plot(timestamps, dollar_values, 'g-', label='Dollar Value')
    ax2.set_ylabel('Dollar Value', color='g')
    ax2.tick_params(axis='y', labelcolor='g')

    # Format the y-axis labels to avoid scientific notation and set a fixed number of decimal places
    ax2.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.2f'))  # Adjust the number of decimals as needed

    # If the y-axis labels are too small or too large, adjust their size like this:
    ax2.tick_params(axis='y', labelsize='medium')  # options include small, medium, large, etc.

    plt.title(f'User Stake and Dollar Value Over Time for {user_name}')
    fig.tight_layout()

    plt.show()

def plot_user_apr_over_time(user_name, delegate_info_log_path, user_data_path, referral_data_path):
    # Process the referral structure from the CSV
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
    # Function to calculate base and adjusted percent
    def calculate_base_and_adjusted_percent(username, user_data, delegate_info, referral_structure):
        def calculate_base_percent(user, nominators_percent):
            user_addresses = user_data.get(user, [])
            return sum(percent for address, percent in nominators_percent if address in user_addresses)

        nominators_percent = delegate_info.get('nominators_percent', [])
        all_base_percents = {user: calculate_base_percent(user, nominators_percent) for user in user_data}

        def calculate_adjusted_percent(user, referral_structure):
            if user not in referral_structure['L1']:
                return all_base_percents.get(user, 0.0)
            else:
                tax = referral_structure['L1'][user]['Tax']
                total_tax_collected = sum(calculate_adjusted_percent(referee, referral_structure) * tax for referee in referral_structure['L1'][user]['Referees'])
                return all_base_percents.get(user, 0.0) + total_tax_collected

        adjusted_percent = calculate_adjusted_percent(username, referral_structure)
        base_percent = all_base_percents.get(username, 0.0)

        return base_percent, adjusted_percent

    # Function to parse the delegate info log and extract necessary data
    def parse_delegate_info_log_for_user(file_path, user_addresses, referral_structure):
        parsed_data = []
        with open(file_path, 'r') as file:
            for line in file:
                json_match = re.search(r'\{.*\}', line)
                timestamp_match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', line)
                
                if json_match and timestamp_match:
                    timestamp = datetime.datetime.strptime(timestamp_match.group(), '%Y-%m-%d %H:%M:%S')
                    json_data = json.loads(json_match.group())

                    total_stake = json_data.get('total_stake', 0)
                    total_daily_return = json_data.get('total_daily_return', 0)
                    apr = (total_daily_return / total_stake) * 365 if total_stake else 0
                    take = json_data.get('take', 0)

                    # Calculate base_percent and adjusted_percent for each log entry
                    base_percent, adjusted_percent = calculate_base_and_adjusted_percent(user_name, user_data, json_data, referral_structure)

                    # Calculate user APR based on the formula
                    if base_percent > 0:
                        user_apr = apr * (take * (adjusted_percent - base_percent) / base_percent + 1)
                    else:
                        user_apr = 0

                    parsed_data.append({
                        'timestamp': timestamp,
                        'user_apr': user_apr
                    })

        return parsed_data

    # Load user data and referral structure
    with open(user_data_path, 'r') as file:
        user_data = json.load(file)
    user_addresses = user_data.get(user_name, [])

    referral_data = pd.read_csv(referral_data_path)
    referral_structure = process_referral_structure(referral_data)

    # Parse the delegate_info.log file for the given user
    user_apr_data = parse_delegate_info_log_for_user(delegate_info_log_path, user_addresses, referral_structure)

    # Convert data for plotting
    timestamps = [entry['timestamp'] for entry in user_apr_data]
    user_aprs = [entry['user_apr'] for entry in user_apr_data]

    # Plotting
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, user_aprs, label='User APR', color='blue')
    plt.title(f'APR Over Time for {user_name}')
    plt.xlabel('Timestamp')
    plt.ylabel('APR (%)')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

