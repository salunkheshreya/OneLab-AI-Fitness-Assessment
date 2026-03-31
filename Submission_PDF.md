## Onelab AI Fitness Assessment: Submission Summary

# Name = Shreya Sudhakar Salunkhe 
# College name = Indira College Of Engineering And Managment Pune 

## 1. Brainstorming Thread
Our discussion focused on creating a robust payment reconciliation engine. I identified key gap categories (Timing, Rounding, Duplicates, Orphans) and discussed the data structures required:
- **Platform Data:** `tx_id`, `amount`, `date`, `status`
- **Bank Data:** `bank_ref`, `tx_id`, `amount`, `date`

I chose **Pandas** for its vectorization capabilities and efficiency in identifying missing subsets between datasets.

## 2. Distilled Prompt
> "Act as a Senior AI-Native Logistics/Fintech Engineer. Create a Python-based reconciliation engine that identifies gaps between two datasets: Platform Transactions and Bank Settlements. 1. Generate synthetic CSV data with specific edge cases: delayed settlement to following month, cumulative rounding error, bank duplicate entries, and a refund without an original record. 2. Write a pandas-based script to reconcile these, flag discrepancies, and generate a 'Gap Analysis Report'. Ensure the code is production-grade and modular."

## 3. Claude Code / Execution Thread
The terminal outputs below confirm the successful execution of the reconciliation logic:
```
--- INITIATING RECONCILIATION REPORT ---

[GAP 1] UNSETTLED TRANSACTIONS (Likely timing differences):
     tx_id  amount        date
4  TXN_005   150.0  2024-01-31

[GAP 2] ORPHAN BANK ENTRIES (Refunds or untracked settle):
  bank_ref        tx_id  amount        date
6  BNK_007  UNKNOWN_REF   -75.0  2024-01-25

[GAP 3] DUPLICATE BANK ENTRIES (System errors):
  bank_ref    tx_id  amount
4  BNK_005  TXN_006   300.0
5  BNK_006  TXN_006   300.0

[GAP 4] AMOUNT DISCREPANCIES (Rounding issues):
     tx_id  amount_p  amount_b   diff
2  TXN_003    50.758     50.75  0.008
3  TXN_004    50.758     50.75  0.008

--- FINAL SUMMARY ---
Platform Total: 902.016
Bank Total:     977.000
Total Variance: -74.984
```

## 4. Test Cases & Verification
The `generate_test_data()` function in `reconcile.py` verifies the solution by planting specific known errors and then ensuring the reconciliation logic flags them as gaps. 
- **Verification:** The sum of internal platform records vs. bank totals matches the manually injected variances.

## 5. Working Output & Final Observations
**3 Sentences on Production Mismatches:**
1.  **Stale Data/Race Conditions:** Real-time production environments can lead to "false mismatch" reports if a transaction settles exactly as the reconciliation script executes.
2.  **ID Truncation:** Real-world bank data often has "fuzzy" reference fields that don't match exactly with the platform's transaction keys, necessitating LLM-based entity matching.
3.  **High-Volume Ingestion:** While NumPy/Pandas handles moderate volumes efficiently, a production-level system would use an incremental processing buffer or a Spark-based architecture for million-scale transaction batches.
