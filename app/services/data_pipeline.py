import pandas as pd
from sqlalchemy.orm import Session
from app.db.models import Transaction

def clean_and_load_csv(file_path: str, job_id: int, db: Session) -> int:
    """
    Reads a dirty CSV, cleans the data, flags anomalies,
    and bulk inserts the records into the database.
    """
    # 1. Read the CSV file
    df = pd.read_csv(file_path)

    # 2. Remove exact duplicate rows
    df = df.drop_duplicates()

    # 3. Clean the 'amount' column
    df['amount'] = df['amount'].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False)
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

    # 4. Clean the 'date' column
    df['date'] = pd.to_datetime(df['date'], format='mixed', dayfirst=True).dt.strftime('%Y-%m-%dT%H:%M:%SZ')

    # 5. Clean text fields
    df['status'] = df['status'].astype(str).str.upper()
    df['currency'] = df['currency'].astype(str).str.upper()
    df['category'] = df['category'].fillna('Uncategorised')

    # --- PHASE 7: ANOMALY DETECTION ---
    
    # Calculate the median transaction amount for each specific account
    # transform() keeps the data the same length as the original dataframe
    df['account_median'] = df.groupby('account_id')['amount'].transform('median')
    
    domestic_merchants = ['SWIGGY', 'OLA', 'IRCTC']
    
    df['is_anomaly'] = False
    df['anomaly_reason'] = None

    for index, row in df.iterrows():
        reasons = []
        
        # Rule 1: Amount exceeds 3x the account's median
        if pd.notna(row['amount']) and pd.notna(row['account_median']):
            if row['amount'] > (3 * row['account_median']):
                reasons.append("Amount exceeds 3x account median")
                
        # Rule 2: Domestic merchant billed in USD
        merchant_upper = str(row['merchant']).upper() if pd.notna(row['merchant']) else ""
        if row['currency'] == 'USD' and merchant_upper in domestic_merchants:
            reasons.append("Domestic merchant billed in USD")
            
        # If any rules were triggered, flag the row
        if reasons:
            df.at[index, 'is_anomaly'] = True
            df.at[index, 'anomaly_reason'] = " | ".join(reasons)

    # 6. Bulk Insert into PostgreSQL
    transactions_to_insert = []
    
    for index, row in df.iterrows():
        txn = Transaction(
            job_id=job_id,
            txn_id=row.get('txn_id') if pd.notna(row.get('txn_id')) else None,
            date=row.get('date'),
            merchant=row.get('merchant') if pd.notna(row.get('merchant')) else None,
            amount=row.get('amount') if pd.notna(row.get('amount')) else 0.0,
            currency=row.get('currency') if pd.notna(row.get('currency')) else None,
            status=row.get('status') if pd.notna(row.get('status')) else None,
            category=row.get('category'),
            account_id=row.get('account_id') if pd.notna(row.get('account_id')) else None,
            is_anomaly=row.get('is_anomaly'),
            anomaly_reason=row.get('anomaly_reason'),
            llm_failed=False
        )
        transactions_to_insert.append(txn)
    
    db.bulk_save_objects(transactions_to_insert)
    db.commit()

    return len(transactions_to_insert)