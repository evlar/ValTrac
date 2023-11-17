import pandas as pd
from ..data_management.referral_data import load_referral_data, save_referral_data
import os

def display_data(df):
    print(df.fillna(''))

def choose_referrer(df):
    referrer = input("Choose a referrer to edit: ")
    while referrer not in df['Referrer'].values:
        print("Referrer not found. Please try again.")
        referrer = input("Choose a referrer to edit: ")
    return referrer

def edit_tax_rate(df, referrer):
    new_tax_rate = float(input("Enter the new tax rate: "))
    df.loc[df['Referrer'] == referrer, 'Tax'] = new_tax_rate

def remove_referee(df, referrer):
    print(df.loc[df['Referrer'] == referrer, df.columns[3:]].fillna(''))
    referee = input("Enter the name of the referee to remove: ")
    referrer_index = df[df['Referrer'] == referrer].index[0]

    # Count the non-null referees for this referrer
    non_null_referees = df.loc[referrer_index, df.columns[3:]].notnull().sum()

    # If only one referee exists, remove the entire row
    if non_null_referees <= 1:
        df.drop(referrer_index, inplace=True)
    else:
        # Remove the specified referee and re-sort the remaining referees
        for col in df.columns[3:]:
            if df.at[referrer_index, col] == referee:
                df.at[referrer_index, col] = None
                break

        referees = [ref for ref in df.loc[referrer_index, df.columns[3:]] if not pd.isna(ref)]
        referees.sort()
        # Update the DataFrame
        for i, ref in enumerate(referees):
            df.at[referrer_index, f'Referee {i+1}'] = ref
        # Clear out remaining old referee entries
        for j in range(i+1, len(df.columns[3:])):
            df.at[referrer_index, f'Referee {j+1}'] = None

def main():
    # Correct the path to point to the project root's 'data' directory
    base_directory = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    referral_csv_path = os.path.join(base_directory, 'data', 'referral_layers.csv')

    try:
        df = load_referral_data(referral_csv_path)
    except FileNotFoundError:
        print("File not found. Exiting.")
        return

    while True:
        display_data(df)
        referrer = choose_referrer(df)

        choice = input("Choose an option:\n1. Change tax rate\n2. Remove referee\n")
        if choice == '1':
            edit_tax_rate(df, referrer)
        elif choice == '2':
            remove_referee(df, referrer)
        else:
            print("Invalid choice. Please try again.")

        save_referral_data(df, referral_csv_path)

        another_edit = input("Would you like to make another edit? (yes/no): ").lower()
        if another_edit not in ['yes', 'y']:
            break

if __name__ == "__main__":
    main()
