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
    "CustomerID": range(1, num_customers + 1),
    "CustomerName": [fake.name() for _ in range(num_customers)],
    "Gender": np.random.choice(['Male', 'Female'], num_customers),
    "DOB": [fake.date_of_birth(minimum_age=18, maximum_age=85) for _ in range(num_customers)],
    "Email": [fake.email() for _ in range(num_customers)],
    "Phone": [fake.phone_number() for _ in range(num_customers)],
    "Address": [fake.address() for _ in range(num_customers)]
})

# Account Dimension
accounts = pd.DataFrame({
    "AccountID": range(1, num_accounts + 1),
    "CustomerID": np.random.randint(1, num_customers + 1, num_accounts),
    "AccountType": np.random.choice(['Savings', 'Checking'], num_accounts),
    "AccountStatus": np.random.choice(['Active', 'Dormant'], num_accounts),
    "OpenDate": [fake.date_between(start_date='-10y', end_date='today') for _ in range(num_accounts)],
    "CloseDate": [None if np.random.rand() > 0.9 else fake.date_between(start_date='today') for _ in range(num_accounts)]
})

# Transaction Type Dimension
transaction_type_dim = pd.DataFrame({
    "TransactionTypeID": range(1, len(transaction_types) + 1),
    "TransactionType": transaction_types,
    "Description": ["Transaction of type " + t for t in transaction_types]
})

# Branch Dimension
branches = pd.DataFrame({
    "BranchID": range(1, num_branches + 1),
    "BranchName": [fake.company() for _ in range(num_branches)],
    "Location": [fake.city() for _ in range(num_branches)],
    "Manager": [fake.name() for _ in range(num_branches)],
    "ContactNumber": [fake.phone_number() for _ in range(num_branches)]
})

# Date Dimension
dates = pd.DataFrame({
    "DateID": range(1, len(date_range) + 1),
    "Date": date_range,
    "Year": date_range.year,
    "Month": date_range.month,
    "Quarter": date_range.quarter,
    "DayOfWeek": date_range.dayofweek
})

# Convert OpenDate and CloseDate in accounts DataFrame to datetime64[ns]
accounts["OpenDate"] = pd.to_datetime(accounts["OpenDate"])
accounts["CloseDate"] = pd.to_datetime(accounts["CloseDate"])

# Fact Table: Transaction Fact
num_transactions = 100000
transaction_records = []  # List to hold transaction records

for i in range(1, num_transactions + 1):
    # Select random customer and account
    customer_id = np.random.randint(1, num_customers + 1)
    account_id = np.random.randint(1, num_accounts + 1)
    
    # Retrieve account details
    account_info = accounts.loc[accounts["AccountID"] == account_id].iloc[0]
    account_open_date = account_info["OpenDate"]
    account_close_date = account_info["CloseDate"]
    
    # Filter valid transaction dates based on account status
    valid_dates = date_range[(date_range >= account_open_date)]
    if pd.notna(account_close_date):  # Account is dormant
        valid_dates = valid_dates[valid_dates <= account_close_date]
    
    # Skip if no valid dates available
    if len(valid_dates) == 0:
        continue
    
    # Choose a transaction date from the valid range
    transaction_date = np.random.choice(valid_dates)
    date_id = dates.loc[dates["Date"] == transaction_date, "DateID"].iloc[0]
    
    # Generate transaction details
    transaction_type_id = np.random.randint(1, len(transaction_types) + 1)
    branch_id = np.random.randint(1, num_branches + 1)
    amount = np.round(np.random.uniform(50, 5000), 2)
    balance_after_transaction = np.round(np.random.uniform(500, 20000), 2)
    
    # Append transaction record to the list
    transaction_records.append({
        "TransactionID": i,
        "CustomerID": customer_id,
        "AccountID": account_id,
        "TransactionTypeID": transaction_type_id,
        "BranchID": branch_id,
        "DateID": date_id,
        "Amount": amount,
        "BalanceAfterTransaction": balance_after_transaction
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
