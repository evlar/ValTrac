import pandas as pd
import os

def load_referral_data(file_path):
    """Load referral data from a CSV file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Referral data file not found: {file_path}")

    return pd.read_csv(file_path)

def save_referral_data(data, file_path):
    """Save referral data to a CSV file."""
    data.to_csv(file_path, index=False)

# Example usage:
# try:
#     referrals = load_referral_data('path/to/referral_layers.csv')
#     # Process referrals...
#     save_referral_data(referrals, 'path/to/referral_layers.csv')
# except Exception as e:
#     print(f"Error: {e}")
