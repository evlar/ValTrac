import pandas as pd
from ..data_management.user_data import load_user_data
from ..data_management.referral_data import load_referral_data, save_referral_data
import os

def is_user_in_system(user_name, users_data):
    return user_name in users_data

def add_entry(df, users_data):
    while True:
        referrer = input("Enter the name of the referrer: ")
        if is_user_in_system(referrer, users_data):
            break
        else:
            print("User not in the system.")

    referrer_layer = get_layer(referrer, df)

    while True:
        referee = input("Enter the name of the referee: ")
        if referee not in df[df.columns[3:]].values and is_user_in_system(referee, users_data):
            if referee in df['Referrer'].values:  # Check if referee is already a referrer
                referee_layer = get_layer(referee, df)
                if int(referee_layer[1:]) <= int(referrer_layer[1:]):
                    print("A referee cannot be a referrer of the same layer or higher.")
                    continue
            break
        else:
            print("This referee already exists or is not in the system. Please enter a different referee.")

    tax = input(f"Enter tax rate for {referrer}: ") if referrer not in df['Referrer'].values else df.loc[df['Referrer'] == referrer, 'Tax'].values[0]

    if referrer not in df['Referrer'].values:
        new_row = {'Layer': referrer_layer, 'Referrer': referrer, 'Tax': tax, 'Referee 1': referee}
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    else:
        referrer_row_index = df[df['Referrer'] == referrer].index[0]
        for i in range(1, 25):  # Assuming a max of 24 referees
            col_name = f'Referee {i}'
            if col_name not in df.columns:
                df[col_name] = None
            if pd.isna(df.at[referrer_row_index, col_name]):
                df.at[referrer_row_index, col_name] = referee
                break

    print(f"Layer: {referrer_layer}, Referrer: {referrer}, Tax: {tax}, Referee: {referee}")
    confirmation = input("Is this entry correct? (yes/no): ")

    if confirmation.lower() == 'yes':
        return df
    else:
        print("Entry discarded.")
        return df



def get_layer(referrer, df):
    for col in df.columns[3:]:  # Iterate over referee columns
        if referrer in df[col].values:
            referrer_row = df[df[col] == referrer].iloc[0]
            referrer_layer = referrer_row['Layer']
            new_layer = 'L' + str(int(referrer_layer[1:]) + 1)
            return new_layer
    return 'L1'  # Default layer if not found

def get_tax_rate(referrer, df):
    if referrer in df['Referrer'].values:
        return df[df['Referrer'] == referrer].iloc[0]['Tax']
    else:
        return input(f"Enter tax rate for {referrer}: ")

def sort_referees(row):
    # Extract referee columns
    referees = [row[col] for col in row.index if 'Referee' in col]
    # Filter out NaN values and sort
    referees = sorted([ref for ref in referees if not pd.isna(ref)])
    # Add NaNs to fill the missing values
    referees += [None] * (len(row.index) - len(referees))
    return pd.Series(referees, index=row.index)

def main():
    # Correct the path to point to the project root's 'data' directory
    base_directory = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    referral_csv_path = os.path.join(base_directory, 'data', 'referral_layers.csv')
    user_json_path = os.path.join(base_directory, 'data', 'user_data.json')

    try:
        df = load_referral_data(referral_csv_path)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['Layer', 'Referrer', 'Tax', 'Referee 1'])

    users_data = load_user_data(user_json_path)

    while True:
        df = add_entry(df, users_data)

        df['Layer'] = df['Layer'].str.extract('(\d+)').astype(int)  # Convert Layer to numeric for sorting
        df = df.sort_values(by='Layer')
        df['Layer'] = 'L' + df['Layer'].astype(str)  # Convert Layer back to original format

        referee_columns = [col for col in df.columns if 'Referee' in col]
        df[referee_columns] = df[referee_columns].apply(sort_referees, axis=1)

        save_referral_data(df, referral_csv_path)
        print("Data saved.")

        add_another = input("Would you like to add another referral? (yes/no): ").lower()
        if add_another not in ['yes', 'y']:
            break

if __name__ == "__main__":
    main()
