import pandas as pd
import numpy as np
from faker import Faker

# Initialize Faker
fake = Faker()

# Dimension parameters
num_customers = 15000
num_branches = 100
transaction_types = ['Deposit', 'Withdrawal', 'Transfer']
date_range = pd.date_range(start="2021-01-01", end="2023-12-31")

# Customer Dimension
customers = pd.DataFrame({
    "CUSTOMERID": range(1, num_customers + 1),
    "CUSTOMERNAME": [fake.name() for _ in range(num_customers)],
    "GENDER": np.random.choice(['Male', 'Female'], num_customers),
    "DOB": [fake.date_of_birth(minimum_age=18, maximum_age=85) for _ in range(num_customers)],
    "EMAIL": [fake.email() for _ in range(num_customers)],
    "PHONE": [fake.phone_number() for _ in range(num_customers)],
})

# Account Dimension - Each customer initially has exactly one account
accounts = pd.DataFrame({
    "ACCOUNTID": range(10001, 10001 + num_customers),
    "CUSTOMERID": customers["CUSTOMERID"],  # Directly assign each customer an account
    "ACCOUNTTYPE": np.random.choice(['Savings', 'Checking'], num_customers),
    "ACCOUNTSTATUS": np.random.choice(['Active', 'Dormant'], num_customers),
    "OPENDATE": [fake.date_between(start_date='-10y', end_date='today') for _ in range(num_customers)],
    "CLOSEDATE": [None if np.random.rand() > 0.9 else fake.date_between(start_date='today') for _ in range(num_customers)]
})

# Add a second account for a random subset of 1,000 customers
additional_accounts_customers = np.random.choice(customers["CUSTOMERID"], size=1000, replace=False)

additional_accounts = pd.DataFrame({
    "ACCOUNTID": range(10001 + num_customers, 10001 + num_customers + 1000),
    "CUSTOMERID": additional_accounts_customers,
    "ACCOUNTTYPE": np.random.choice(['Savings', 'Checking'], 1000),
    "ACCOUNTSTATUS": np.random.choice(['Active', 'Dormant'], 1000),
    "OPENDATE": [fake.date_between(start_date='-10y', end_date='today') for _ in range(1000)],
    "CLOSEDATE": [None if np.random.rand() > 0.9 else fake.date_between(start_date='today') for _ in range(1000)]
})

# Concatenate the original and additional accounts into one DataFrame
accounts = pd.concat([accounts, additional_accounts], ignore_index=True)

# Transaction Type Dimension
transaction_type_dim = pd.DataFrame({
    "TRANSACTIONTYPEID": range(1, len(transaction_types) + 1),
    "TRANSACTIONTYPE": transaction_types,
    "DESCRIPTION": ["Transaction of type " + t for t in transaction_types]
})

# Branch Dimension
branches = pd.DataFrame({
    "BRANCHID": range(1, num_branches + 1),
    "BRANCHNAME": [fake.company() for _ in range(num_branches)],
    "LOCATION": [fake.city() for _ in range(num_branches)],
    "MANAGER": [fake.name() for _ in range(num_branches)],
    "CONTACTNUMBER": [fake.phone_number() for _ in range(num_branches)]
})

# Date Dimension
dates = pd.DataFrame({
    "DATEID": range(1, len(date_range) + 1),
    "DATE": date_range,
    "YEAR": date_range.year,
    "MONTH": date_range.month,
    "QUARTER": date_range.quarter,
    "DAYOFWEEK": date_range.dayofweek
})

# Convert OpenDate and CloseDate in accounts DataFrame to datetime64[ns]
accounts["OPENDATE"] = pd.to_datetime(accounts["OPENDATE"])
accounts["CLOSEDATE"] = pd.to_datetime(accounts["CLOSEDATE"])

# Fact Table: Transaction Fact
num_transactions = 100000
transaction_records = []  # List to hold transaction records

for i in range(1, num_transactions + 1):
    # Select a random customer and one of their accounts
    customer_id = np.random.randint(1, num_customers + 1)
    account_ids = accounts.loc[accounts["CUSTOMERID"] == customer_id, "ACCOUNTID"].values
    account_id = np.random.choice(account_ids)

    # Retrieve account details
    account_info = accounts.loc[accounts["ACCOUNTID"] == account_id].iloc[0]
    account_open_date = account_info["OPENDATE"]
    account_close_date = account_info["CLOSEDATE"]

    # Filter valid transaction dates based on account status
    valid_dates = date_range[(date_range >= account_open_date)]
    if pd.notna(account_close_date):  # Account is closed
        valid_dates = valid_dates[valid_dates <= account_close_date]
    
    # Skip if no valid dates available
    if len(valid_dates) == 0:
        continue

    # Choose a transaction date from the valid range
    transaction_date = np.random.choice(valid_dates)
    date_id = dates.loc[dates["DATE"] == transaction_date, "DATEID"].iloc[0]

    # Determine transaction type
    transaction_type = np.random.choice(transaction_types)

    if transaction_type == 'Transfer':
        # Ensure transfer goes to a different customer account and the account_id for the transaction is between 1 and 9999
        while True:
            target_account_id = np.random.randint(10001, accounts["ACCOUNTID"].max() + 1)  # Random target account from 10001 to max
            target_account = accounts.loc[accounts["ACCOUNTID"] == target_account_id]
            target_customer_id = target_account["CUSTOMERID"].iloc[0]
            if target_customer_id != customer_id:  # Ensure target account belongs to a different customer
                break
        
        transaction_type_id = 3
        transaction_record = {
            "TRANSACTIONID": i,
            "CUSTOMERID": customer_id,
            "ACCOUNTID": np.random.randint(1, 10000),  # For Transfer, the account_id is between 1 and 9999
            "TRANSACTIONTYPEID": transaction_type_id,
            "BRANCHID": np.random.randint(1, num_branches + 1),
            "DATEID": date_id,
            "AMOUNT": np.round(np.random.uniform(50, 5000), 2),
            "BALANCEAFTERTRANSACTION": np.round(np.random.uniform(500, 20000), 2)
        }
    else:
        # Deposit or Withdrawal within the same customer's account
        transaction_type_id = 1 if transaction_type == 'Deposit' else 2
        transaction_record = {
            "TRANSACTIONID": i,
            "CUSTOMERID": customer_id,
            "ACCOUNTID": account_id,
            "TRANSACTIONTYPEID": transaction_type_id,
            "BRANCHID": np.random.randint(1, num_branches + 1),
            "DATEID": date_id,
            "AMOUNT": np.round(np.random.uniform(50, 5000), 2),
            "BALANCEAFTERTRANSACTION": np.round(np.random.uniform(500, 20000), 2)
        }
    
    # Append transaction record to the list
    transaction_records.append(transaction_record)

# Convert the list of transaction records to a DataFrame
transactions = pd.DataFrame(transaction_records)

# Save all dataframes to CSV files
customers.to_csv("CUSTOMERS.csv", index=False)
accounts.to_csv("ACCOUNTS.csv", index=False)
transaction_type_dim.to_csv("TRANSACTION_TYPES.csv", index=False)
branches.to_csv("BRANCH.csv", index=False)
dates.to_csv("DATE.csv", index=False)
transactions.to_csv("TRANSACTIONS.csv", index=False)
