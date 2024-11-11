import pandas as pd
import numpy as np
from faker import Faker

# Initialize Faker
fake = Faker()

# Dimension parameters
num_customers = 15000
num_accounts = 15000
num_branches = 100
transaction_types = ['Deposit', 'Withdrawal', 'Transfer', 'Payment']
date_range = pd.date_range(start="2021-01-01", end="2023-12-31")

# Customer Dimension
customers = pd.DataFrame({
    "CUSTOMERID": range(1, num_customers + 1),
    "CUSTOMERNAME": [fake.name() for _ in range(num_customers)],
    "GENDER": np.random.choice(['Male', 'Female'], num_customers),
    "DOB": [fake.date_of_birth(minimum_age=18, maximum_age=85) for _ in range(num_customers)],
    "EMAIL": [fake.email() for _ in range(num_customers)],
    "PHONE": [fake.phone_number() for _ in range(num_customers)],
    # "Address": [fake.address() for _ in range(num_customers)]
})

# Account Dimension
accounts = pd.DataFrame({
    "ACCOUNTID": range(1, num_accounts + 1),
    "CUSTOMERID": np.random.randint(1, num_customers + 1, num_accounts),
    "ACCOUNTTYPE": np.random.choice(['Savings', 'Checking'], num_accounts),
    "ACCOUNTSTATUS": np.random.choice(['Active', 'Dormant'], num_accounts),
    "OPENDATE": [fake.date_between(start_date='-10y', end_date='today') for _ in range(num_accounts)],
    "CLOSEDATE": [None if np.random.rand() > 0.9 else fake.date_between(start_date='today') for _ in range(num_accounts)]
})

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
    # Select random customer and account
    customer_id = np.random.randint(1, num_customers + 1)
    account_id = np.random.randint(1, num_accounts + 1)
    
    # Retrieve account details
    account_info = accounts.loc[accounts["ACCOUNTID"] == account_id].iloc[0]
    account_open_date = account_info["OPENDATE"]
    account_close_date = account_info["CLOSEDATE"]
    
    # Filter valid transaction dates based on account status
    valid_dates = date_range[(date_range >= account_open_date)]
    if pd.notna(account_close_date):  # Account is dormant
        valid_dates = valid_dates[valid_dates <= account_close_date]
    
    # Skip if no valid dates available
    if len(valid_dates) == 0:
        continue
    
    # Choose a transaction date from the valid range
    transaction_date = np.random.choice(valid_dates)
    date_id = dates.loc[dates["DATE"] == transaction_date, "DATEID"].iloc[0]
    
    # Generate transaction details
    transaction_type_id = np.random.randint(1, len(transaction_types) + 1)
    branch_id = np.random.randint(1, num_branches + 1)
    amount = np.round(np.random.uniform(50, 5000), 2)
    balance_after_transaction = np.round(np.random.uniform(500, 20000), 2)
    
    # Append transaction record to the list
    transaction_records.append({
        "TRANSACTIONID": i,
        "CUSTOMERID": customer_id,
        "ACCOUNTID": account_id,
        "TRANSACTIONTYPEID": transaction_type_id,
        "BRANCHID": branch_id,
        "DATEID": date_id,
        "AMOUNT": amount,
        "BALANCEAFTERTRANSACTION": balance_after_transaction
    })

# Convert the list of transaction records to a DataFrame
transactions = pd.DataFrame(transaction_records)

# Save all dataframes to CSV files
customers.to_csv("CUSTOMERS.csv", index=False)
accounts.to_csv("ACCOUNTS.csv", index=False)
transaction_type_dim.to_csv("TRANSACTION_TYPES.csv", index=False)
branches.to_csv("BRANCH.csv", index=False)
dates.to_csv("DATE.csv", index=False)
transactions.to_csv("TRANSACTIONS.csv", index=False)
