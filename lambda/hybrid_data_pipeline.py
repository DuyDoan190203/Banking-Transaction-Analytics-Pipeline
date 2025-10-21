"""
Hybrid Data Pipeline: Real API + Synthetic Transactions
Combines real OBP bank/account data with Faker-generated transactions

This demonstrates a production pattern:
- Real API structure and account IDs
- Synthetic transactions for testing
- Clear data lineage tracking
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from faker import Faker
import random
from config import Config

fake = Faker()


def authenticate():
    """Authenticate with OBP API and return token"""
    print("\n" + "=" * 60)
    print("STEP 1: Authentication (REAL API)")
    print("=" * 60)
    
    url = Config.OBP_DIRECTLOGIN_ENDPOINT
    headers = {
        "Authorization": f'DirectLogin username="{Config.OBP_USERNAME}", password="{Config.OBP_PASSWORD}", consumer_key="{Config.OBP_CONSUMER_KEY}"',
        "Accept": "application/json"
    }
    
    response = requests.post(url, headers=headers)
    
    if response.status_code == 201:
        token = response.json()["token"]
        print(f"[SUCCESS] Authentication successful! Token: {token[:20]}...")
        return token
    else:
        raise Exception(f"Authentication failed: {response.status_code}")


def fetch_real_banks(token):
    """Fetch real banks from OBP API"""
    print("\n" + "=" * 60)
    print("STEP 2: Fetching Banks (REAL API)")
    print("=" * 60)
    
    url = f"{Config.OBP_BASE_URL}/obp/{Config.OBP_API_VERSION}/banks"
    headers = {
        "Authorization": f'DirectLogin token="{token}"',
        "Accept": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        banks = response.json()["banks"]
        print(f"[SUCCESS] Found {len(banks)} real banks")
        
        banks_data = []
        for bank in banks[:10]:  # Limit to first 10 banks
            banks_data.append({
                'bank_id': bank['id'],
                'bank_name': bank.get('full_name', bank.get('short_name', 'N/A')),
                'data_source': 'REAL_API',
                'extracted_at': datetime.now().isoformat()
            })
        
        print(f"[SUCCESS] Processed {len(banks_data)} banks")
        return banks_data
    else:
        raise Exception(f"Failed to fetch banks: {response.status_code}")


def fetch_real_accounts(token, bank_ids):
    """Fetch real public accounts from OBP API"""
    print("\n" + "=" * 60)
    print("STEP 3: Fetching Accounts (REAL API)")
    print("=" * 60)
    
    all_accounts = []
    
    for bank_id in bank_ids:
        url = f"{Config.OBP_BASE_URL}/obp/{Config.OBP_API_VERSION}/banks/{bank_id}/accounts/public"
        headers = {
            "Authorization": f'DirectLogin token="{token}"',
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, list):
                accounts = data
            elif isinstance(data, dict):
                accounts = data.get("accounts", [])
            else:
                accounts = []
            
            if accounts:
                print(f"  [SUCCESS] {bank_id}: Found {len(accounts)} accounts")
                
                for account in accounts:
                    all_accounts.append({
                        'account_id': account.get('id', 'N/A'),
                        'bank_id': bank_id,
                        'account_label': account.get('label', account.get('account_label', 'N/A')),
                        'account_type': account.get('account_type', 'N/A'),
                        'data_source': 'REAL_API',
                        'extracted_at': datetime.now().isoformat()
                    })
    
    print(f"\n[SUCCESS] Total accounts fetched: {len(all_accounts)}")
    return all_accounts


def generate_synthetic_transactions(accounts_df, transactions_per_account=100):
    """Generate synthetic transactions linked to real account IDs"""
    print("\n" + "=" * 60)
    print(f"STEP 4: Generating Synthetic Transactions ({transactions_per_account} per account)")
    print("=" * 60)
    
    all_transactions = []
    transaction_types = ['ATM Withdrawal', 'POS Purchase', 'Online Transfer', 'Direct Debit', 
                        'Salary Deposit', 'Refund', 'Bill Payment', 'Cash Deposit']
    
    merchants = ['Amazon', 'Walmart', 'Starbucks', 'Shell Gas', 'Netflix', 'Spotify', 
                'Uber', 'Restaurant', 'Supermarket', 'Pharmacy']
    
    for idx, account_row in accounts_df.iterrows():
        account_id = account_row['account_id']
        bank_id = account_row['bank_id']
        
        # Generate random starting balance
        starting_balance = random.uniform(1000, 50000)
        current_balance = starting_balance
        
        # Generate transactions for the past 90 days
        start_date = datetime.now() - timedelta(days=90)
        
        for i in range(transactions_per_account):
            # Random transaction date within last 90 days
            days_ago = random.randint(0, 90)
            tx_date = datetime.now() - timedelta(days=days_ago)
            
            # Random transaction type
            tx_type = random.choice(transaction_types)
            
            # Generate amount based on transaction type
            if tx_type in ['Salary Deposit', 'Refund', 'Cash Deposit']:
                # Credit transactions
                amount = round(random.uniform(500, 5000), 2)
                is_debit = False
            else:
                # Debit transactions
                amount = round(random.uniform(5, 500), 2)
                is_debit = True
            
            # Update balance
            if is_debit:
                current_balance -= amount
                amount_signed = -amount
            else:
                current_balance += amount
                amount_signed = amount
            
            # Generate description
            if tx_type == 'POS Purchase':
                description = f"{tx_type} at {random.choice(merchants)}"
            elif tx_type == 'Online Transfer':
                description = f"{tx_type} to {fake.name()}"
            elif tx_type == 'Salary Deposit':
                description = f"{tx_type} from {fake.company()}"
            else:
                description = tx_type
            
            # Create transaction record
            all_transactions.append({
                'transaction_id': f"synth_{account_id}_{i:04d}",
                'bank_id': bank_id,
                'account_id': account_id,
                'amount': amount_signed,
                'currency': random.choice(['GBP', 'EUR', 'USD']),
                'transaction_type': tx_type,
                'description': description,
                'merchant': random.choice(merchants) if tx_type == 'POS Purchase' else None,
                'transaction_date': tx_date.isoformat(),
                'transaction_hour': tx_date.hour,
                'day_of_week': tx_date.strftime('%A'),
                'is_weekend': tx_date.weekday() >= 5,
                'balance_after': round(current_balance, 2),
                'counterparty_name': fake.name() if tx_type == 'Online Transfer' else None,
                'data_source': 'SYNTHETIC',
                'generated_at': datetime.now().isoformat()
            })
        
        print(f"  [SUCCESS] Generated {transactions_per_account} transactions for account: {account_id}")
    
    print(f"\n[SUCCESS] Total synthetic transactions: {len(all_transactions)}")
    return all_transactions


def save_hybrid_datasets(banks_df, accounts_df, transactions_df):
    """Save hybrid datasets to CSV files with clear labeling"""
    print("\n" + "=" * 60)
    print("STEP 5: Saving Hybrid Datasets")
    print("=" * 60)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save banks
    banks_file = f"hybrid_banks_{timestamp}.csv"
    banks_df.to_csv(banks_file, index=False)
    print(f"[SUCCESS] Saved {len(banks_df)} banks to: {banks_file}")
    print(f"   Data source: {banks_df['data_source'].iloc[0]}")
    
    # Save accounts
    accounts_file = f"hybrid_accounts_{timestamp}.csv"
    accounts_df.to_csv(accounts_file, index=False)
    print(f"[SUCCESS] Saved {len(accounts_df)} accounts to: {accounts_file}")
    print(f"   Data source: {accounts_df['data_source'].iloc[0]}")
    
    # Save transactions
    transactions_file = f"hybrid_transactions_{timestamp}.csv"
    transactions_df.to_csv(transactions_file, index=False)
    print(f"[SUCCESS] Saved {len(transactions_df)} transactions to: {transactions_file}")
    print(f"   Data source: {transactions_df['data_source'].iloc[0]}")
    
    return banks_file, accounts_file, transactions_file


def display_data_summary(banks_df, accounts_df, transactions_df):
    """Display summary statistics of the hybrid dataset"""
    print("\n" + "=" * 60)
    print("DATA SUMMARY")
    print("=" * 60)
    
    print("\nBANKS (Real API Data)")
    print(f"Total banks: {len(banks_df)}")
    print(f"\nSample banks:")
    print(banks_df[['bank_id', 'bank_name', 'data_source']].head(3).to_string(index=False))
    
    print("\nACCOUNTS (Real API Data)")
    print(f"Total accounts: {len(accounts_df)}")
    print(f"Accounts per bank:")
    print(accounts_df.groupby('bank_id').size().head(5).to_string())
    print(f"\nSample accounts:")
    print(accounts_df[['account_id', 'bank_id', 'account_label', 'data_source']].head(3).to_string(index=False))
    
    print("\nTRANSACTIONS (Synthetic Data)")
    print(f"Total transactions: {len(transactions_df)}")
    print(f"Transactions per account: {len(transactions_df) // len(accounts_df)}")
    print(f"Date range: {transactions_df['transaction_date'].min()} to {transactions_df['transaction_date'].max()}")
    print(f"\nTransaction types:")
    print(transactions_df['transaction_type'].value_counts().to_string())
    print(f"\nCurrency distribution:")
    print(transactions_df['currency'].value_counts().to_string())
    print(f"\nAmount statistics:")
    print(transactions_df['amount'].describe().to_string())
    print(f"\nSample transactions:")
    print(transactions_df[['transaction_id', 'account_id', 'amount', 'currency', 
                          'description', 'data_source']].head(5).to_string(index=False))


def validate_data_lineage(banks_df, accounts_df, transactions_df):
    """Validate that synthetic transactions are properly linked to real accounts"""
    print("\n" + "=" * 60)
    print("DATA LINEAGE VALIDATION")
    print("=" * 60)
    
    # Check banks data source
    banks_real = (banks_df['data_source'] == 'REAL_API').sum()
    print(f"[SUCCESS] Banks: {banks_real}/{len(banks_df)} from REAL_API")
    
    # Check accounts data source
    accounts_real = (accounts_df['data_source'] == 'REAL_API').sum()
    print(f"[SUCCESS] Accounts: {accounts_real}/{len(accounts_df)} from REAL_API")
    
    # Check transactions data source
    transactions_synthetic = (transactions_df['data_source'] == 'SYNTHETIC').sum()
    print(f"[SUCCESS] Transactions: {transactions_synthetic}/{len(transactions_df)} SYNTHETIC")
    
    # Validate linkage
    real_account_ids = set(accounts_df['account_id'])
    transaction_account_ids = set(transactions_df['account_id'])
    
    if transaction_account_ids.issubset(real_account_ids):
        print(f"[SUCCESS] All synthetic transactions linked to REAL accounts")
        print(f"   {len(transaction_account_ids)} unique accounts with transactions")
    else:
        orphaned = transaction_account_ids - real_account_ids
        print(f"[WARNING] {len(orphaned)} orphaned transaction accounts")
    
    # Validate bank linkage
    real_bank_ids = set(banks_df['bank_id'])
    transaction_bank_ids = set(transactions_df['bank_id'])
    
    if transaction_bank_ids.issubset(real_bank_ids):
        print(f"[SUCCESS] All transactions linked to REAL banks")
    else:
        orphaned = transaction_bank_ids - real_bank_ids
        print(f"[WARNING] {len(orphaned)} orphaned transaction banks")


def main():
    """Main hybrid pipeline execution"""
    print("\n" + "=" * 70)
    print("HYBRID DATA PIPELINE: Real API + Synthetic Transactions")
    print("=" * 70)
    print("\nStrategy:")
    print("  1. Fetch REAL banks from OBP API")
    print("  2. Fetch REAL accounts from OBP API")
    print("  3. Generate SYNTHETIC transactions linked to real accounts")
    print("  4. Save with clear data source labeling")
    print("=" * 70)
    
    try:
        # Validate config
        Config.validate_directlogin()
        print("\n[SUCCESS] Configuration validated")
        
        # Step 1: Authenticate
        token = authenticate()
        
        # Step 2: Fetch real banks
        banks_data = fetch_real_banks(token)
        banks_df = pd.DataFrame(banks_data)
        
        # Step 3: Fetch real accounts (try first 3 banks)
        bank_ids_to_try = banks_df['bank_id'].head(3).tolist()
        accounts_data = fetch_real_accounts(token, bank_ids_to_try)
        
        if not accounts_data:
            print("\n[WARNING] No accounts found, trying more banks...")
            bank_ids_to_try = banks_df['bank_id'].head(10).tolist()
            accounts_data = fetch_real_accounts(token, bank_ids_to_try)
        
        if not accounts_data:
            raise Exception("No accounts found in any banks")
        
        accounts_df = pd.DataFrame(accounts_data)
        
        # Step 4: Generate synthetic transactions
        transactions_data = generate_synthetic_transactions(accounts_df, transactions_per_account=100)
        transactions_df = pd.DataFrame(transactions_data)
        
        # Step 5: Save datasets
        banks_file, accounts_file, transactions_file = save_hybrid_datasets(
            banks_df, accounts_df, transactions_df
        )
        
        # Step 6: Display summary
        display_data_summary(banks_df, accounts_df, transactions_df)
        
        # Step 7: Validate data lineage
        validate_data_lineage(banks_df, accounts_df, transactions_df)
        
        # Success message
        print("\n" + "=" * 70)
        print("[SUCCESS] HYBRID PIPELINE COMPLETE!")
        print("=" * 70)
        print(f"\nOutput Files:")
        print(f"   1. {banks_file}")
        print(f"   2. {accounts_file}")
        print(f"   3. {transactions_file}")
        print(f"\nData Summary:")
        print(f"   - Banks: {len(banks_df)} (REAL API)")
        print(f"   - Accounts: {len(accounts_df)} (REAL API)")
        print(f"   - Transactions: {len(transactions_df)} (SYNTHETIC)")
        print(f"\nThis is production-ready test data:")
        print(f"   - Real account IDs and structure")
        print(f"   - Synthetic transactions for testing")
        print(f"   - Clear data lineage tracking")
        
    except Exception as e:
        print(f"\n[ERROR] Pipeline failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

