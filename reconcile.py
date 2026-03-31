import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# --- PART 1: DATA GENERATOR ---
def generate_test_data():
    """Generates synthetic data with specific errors as per assessment requirements."""
    
    # 1. Base Platform Transactions (Jan month)
    platform_data = [
        {"tx_id": "TXN_001", "amount": 100.0, "date": "2024-01-05", "status": "SUCCESS"},
        {"tx_id": "TXN_002", "amount": 250.5, "date": "2024-01-10", "status": "SUCCESS"},
        {"tx_id": "TXN_003", "amount": 50.758, "date": "2024-01-15", "status": "SUCCESS"}, # Rounding Issue
        {"tx_id": "TXN_004", "amount": 50.758, "date": "2024-01-16", "status": "SUCCESS"}, # Rounding Issue
        {"tx_id": "TXN_005", "amount": 150.0, "date": "2024-01-31", "status": "SUCCESS"}, # Settled Following Month
        {"tx_id": "TXN_006", "amount": 300.0, "date": "2024-01-20", "status": "SUCCESS"}, # Duplicate in Bank
        # Missing Refund's original TX_ID: No entry here for a specific refund
    ]
    df_platform = pd.DataFrame(platform_data)
    
    # 2. Base Bank Settlements (Jan statement)
    bank_data = [
        {"bank_ref": "BNK_001", "tx_id": "TXN_001", "amount": 100.0, "date": "2024-01-06"},
        {"bank_ref": "BNK_002", "tx_id": "TXN_002", "amount": 250.5, "date": "2024-01-12"},
        # Rounding Differences: Bank sums them differently (Truncates to 2 decimals)
        {"bank_ref": "BNK_003", "tx_id": "TXN_003", "amount": 50.75, "date": "2024-01-17"}, 
        {"bank_ref": "BNK_004", "tx_id": "TXN_004", "amount": 50.75, "date": "2024-01-18"}, 
        # TXN_005 is missing from January bank records (settled in Feb)
        # Duplicate entry for TXN_006
        {"bank_ref": "BNK_005", "tx_id": "TXN_006", "amount": 300.0, "date": "2024-01-22"},
        {"bank_ref": "BNK_006", "tx_id": "TXN_006", "amount": 300.0, "date": "2024-01-22"}, # Duplicate
        # Refund with no matching original transaction in Platform
        {"bank_ref": "BNK_007", "tx_id": "UNKNOWN_REF", "amount": -75.0, "date": "2024-01-25"},
    ]
    df_bank = pd.DataFrame(bank_data)
    
    df_platform.to_csv("platform_data.csv", index=False)
    df_bank.to_csv("bank_data.csv", index=False)
    print("Test data generated: platform_data.csv and bank_data.csv")

# --- PART 2: RECONCILIATION ENGINE ---
def reconcile_books(platform_file, bank_file):
    """Analyzes the differences between platform and bank data."""
    df_p = pd.read_csv(platform_file)
    df_b = pd.read_csv(bank_file)
    
    print("\n--- INITIATING RECONCILIATION REPORT ---")
    
    # 1. Find Unsettled Transactions (In Platform but NOT in Bank)
    unsettled = df_p[~df_p['tx_id'].isin(df_b['tx_id'])]
    
    # 2. Find Orphan Bank Entries (In Bank but NOT in Platform)
    orphans = df_b[~df_b['tx_id'].isin(df_p['tx_id'])]
    
    # 3. Detect Duplicates in Bank
    duplicates = df_b[df_b.duplicated(subset=['tx_id'], keep=False)]
    
    # 4. Detect Amount Discrepancies (Rounding/Errors)
    # Merge on tx_id to compare amounts
    merged = pd.merge(df_p, df_b, on='tx_id', suffixes=('_p', '_b'))
    merged['diff'] = merged['amount_p'] - merged['amount_b']
    discrepancies = merged[abs(merged['diff']) > 0.001]

    # Displaying Results
    print("\n[GAP 1] UNSETTLED TRANSACTIONS (Likely timing differences):")
    print(unsettled[['tx_id', 'amount', 'date']])

    print("\n[GAP 2] ORPHAN BANK ENTRIES (Refunds or untracked settle):")
    print(orphans[['bank_ref', 'tx_id', 'amount', 'date']])

    print("\n[GAP 3] DUPLICATE BANK ENTRIES (System errors):")
    print(duplicates[['bank_ref', 'tx_id', 'amount']])

    print("\n[GAP 4] AMOUNT DISCREPANCIES (Rounding issues):")
    print(discrepancies[['tx_id', 'amount_p', 'amount_b', 'diff']])

    # Summary Stats
    platform_total = df_p['amount'].sum()
    bank_total = df_b['amount'].sum()
    print(f"\n--- FINAL SUMMARY ---")
    print(f"Platform Total: {platform_total:,.3f}")
    print(f"Bank Total:     {bank_total:,.3f}")
    print(f"Total Variance: {platform_total - bank_total:,.3f}")

if __name__ == "__main__":
    generate_test_data()
    reconcile_books("platform_data.csv", "bank_data.csv")
