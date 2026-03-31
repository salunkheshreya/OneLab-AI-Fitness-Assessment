import streamlit as st
import pandas as pd
import io

# --- PART 1: CORE RECONCILIATION ENGINE ---
def reconcile_logic(df_p, df_b):
    """Core logic extracted for web use."""
    # 1. Find Unsettled Transactions
    unsettled = df_p[~df_p['tx_id'].isin(df_b['tx_id'])]
    
    # 2. Find Orphan Bank Entries
    orphans = df_b[~df_b['tx_id'].isin(df_p['tx_id'])]
    
    # 3. Detect Duplicates in Bank
    duplicates = df_b[df_b.duplicated(subset=['tx_id'], keep=False)]
    
    # 4. Detect Amount Discrepancies
    merged = pd.merge(df_p, df_b, on='tx_id', suffixes=('_p', '_b'))
    merged['diff'] = merged['amount_p'] - merged['amount_b']
    discrepancies = merged[abs(merged['diff']) > 0.001]
    
    return unsettled, orphans, duplicates, discrepancies

# --- PART 2: STREAMLIT UI ---
def main():
    st.set_page_config(page_title="Onelab Reconciliation Engine", page_icon="💳", layout="wide")
    
    st.title("🚀 Onelab AI-Native Reconciliation Engine")
    st.write("Upload your Platform and Bank CSVs to identify accounting gaps.")
    
    # Layout Columns
    col1, col2 = st.sidebar.columns(2)
    
    st.sidebar.header("📂 Data Upload")
    p_file = st.sidebar.file_uploader("Upload Platform CSV", type="csv")
    b_file = st.sidebar.file_uploader("Upload Bank CSV", type="csv")

    if p_file is not None and b_file is not None:
        df_p = pd.read_csv(p_file)
        df_b = pd.read_csv(b_file)
        
        # Performance Reconciliation
        unsettled, orphans, duplicates, discrepancies = reconcile_logic(df_p, df_b)
        
        # --- TABULAR REPORT ---
        tab1, tab2, tab3, tab4 = st.tabs(["Timing Gaps", "Orphan Entries", "Duplicates", "Amount Variances"])
        
        with tab1:
            st.subheader("⚠️ Unsettled Transactions (Timing Differences)")
            st.write("Transactions recorded on the platform but not found in the bank statement.")
            st.dataframe(unsettled, use_container_width=True)
            
        with tab2:
            st.subheader("🔍 Orphan Bank Entries")
            st.write("Bank entries that do not have a matching platform record.")
            st.dataframe(orphans, use_container_width=True)
            
        with tab3:
            st.subheader("👯 Duplicate Settlements")
            st.write("Multiple settlement records found for a single platform transaction.")
            st.dataframe(duplicates, use_container_width=True)
            
        with tab4:
            st.subheader("⚖️ Amount Discrepancies (Rounding)")
            st.write("Records where the IDs match but the amounts differ.")
            st.dataframe(discrepancies, use_container_width=True)

        # --- STATS DASHBOARD ---
        st.divider()
        st.subheader("📊 Reconciliation Summary")
        c1, c2, c3 = st.columns(3)
        p_total = df_p['amount'].sum()
        b_total = df_b['amount'].sum()
        
        c1.metric("Platform Total", f"${p_total:,.2f}")
        c2.metric("Bank Total", f"${b_total:,.2f}")
        c3.metric("Total Variance", f"${(p_total - b_total):,.2f}", delta_color="inverse")

    else:
        st.info("💡 Please upload both CSV files in the sidebar to begin.")
        st.write("Don't have files? You can use the `platform_data.csv` and `bank_data.csv` created by the script.")

if __name__ == "__main__":
    main()
