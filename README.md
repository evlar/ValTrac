# ValTrac
Bittensor Validator User and Referral Management System

## Description
This project is a practical application to be used by a Bittensor Validator Owner to turn their validator into a referral rewards sytem. Its main functionalities include managing user data, handling referrals, logging blockchain-related activities, and processing payouts. It connects to a subtensor node to manage user information and referrals, ensuring efficient and accurate data handling.

## Features
- User management including adding, editing, and validating user coldkey addresses.
- Referral system for tracking and managing referrals.
- Logging of blockchain activities for record-keeping.
- Processing payouts based on referral structure.
- Integration with a running subtensor node.
- Use of `pm2` for managing background processes.

## Getting Started

### Dependencies
- Python 3.8 or later
- Pandas
- Bittensor
- Requests
- A running subtensor node (see Bittensor's subtensor [subtensor GitHub page](https://github.com/opentensor/subtensor) for setup instructions)
- `pm2` for process management (see [pm2 GitHub page](https://github.com/Unitech/pm2) for installation)

### Installing
- Clone the repository: `git clone [https://github.com/evlar/batch_delegator.git]`
- Install required packages: `pip install -r requirements.txt`
- Ensure a subtensor node is active (details in Bittensor's subtensor `README.md`).
- Install `pm2` following instructions on its GitHub page.

### Validator setup
- For this system to work as intended the validator owner must unstake all of their tao from the validator hotkey (delegate_stake) and restake from a separate personal coldkey, thereby converting the 'delegate_stake' into a payout pool which accumulates the 18% take from all of the nominator addresses.
- This program allows for the input of a layered referral system where each referrer may set a referral for their referees. Those referees may act as referrers and do the same. The referral tax is the percentage take of a user's base percentage allocation of the payout pool. Base percentage equals a user's average stake/(total_validator_stake - delegate_stake) over a range defined by the number of block snapshots between the last payout and the current payout. If a user has no tax imposed on them they will receive 100% payback of their base percentage of the payout pool. A referee with a 100% tax imposed upon them will receive no payout. 


### Executing Program
- Make sure that local subtensor is running 
- Run `run.py` to start the application and view the main menu:

1. Begin logging delegate info:
    - This will launch a pm2 instance to run in the background taking a snapshot every 300 blocks (1 hour).
2. Send payout:
    - Calculates user payout amounts for the time range since the beginning of 'delegate_info.log', or since the last payout block. 
    - Executes a batch transfer from the payout pool
    - Apends payout pool total and user balances to 'payout_log.csv'
3. Add users:
    - Multiple addresses are permitted per user
    - First entered address will be used for payout
    1. Load users from CSV:
        - Loads users into the database by upload from a CSV file, or manual entry
        - CSV file must have the following column header format: Name,Address1,Address2,Address3,,,
        - Option to append to or replace existing user database.
    2. Manual entry:
        - Allows manual entry of username, and multiple addresses.
        - Appends to existing database.
4. Edit users:
    - Allows the deletion of users, or user addresses from the database.
5. Add referral:
    - Enter the name of a referrer, their referee, and their referral tax rate in the database
6. Edit referrals:
    - Change a referrers set tax rate and/or remove a referee.
7. Charts and Statistics:
    - Opens a menu of charts and select user statistics.
8. Exit:
    - Go on! Get!!!