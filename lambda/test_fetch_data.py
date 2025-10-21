"""
Simple test script for Open Bank Project API
Tests authentication and fetches sample data to CSV

Prerequisites:
    1. Create .env file with OBP credentials 
    2. pip install -r requirements.txt
    
Usage:
    python test_fetch_data.py
"""

import requests
import pandas as pd
from datetime import datetime
from config import Config


def authenticate():
    """Test DirectLogin authentication and return token"""
    print("\n" + "=" * 60)
    print("STEP 1: Testing Authentication")
    print("=" * 60)
    
    url = Config.OBP_DIRECTLOGIN_ENDPOINT
    headers = {
        "Authorization": f'DirectLogin username="{Config.OBP_USERNAME}", password="{Config.OBP_PASSWORD}", consumer_key="{Config.OBP_CONSUMER_KEY}"',
        "Accept": "application/json"
    }
    
    print(f"Endpoint: {url}")
    print(f"Username: {Config.OBP_USERNAME}")
    
    response = requests.post(url, headers=headers)
    
    if response.status_code == 201:
        token = response.json()["token"]
        print(f"[SUCCESS] Authentication successful! Token: {token[:20]}...")
        return token
    else:
        print(f"[ERROR] Authentication failed: {response.status_code}")
        print(f"Response: {response.text}")
        raise Exception("Authentication failed")

def fetch_banks(token):
    """Fetch list of banks"""
    print("\n" + "=" * 60)
    print("STEP 2: Fetching Banks")
    print("=" * 60)
    
    url = f"{Config.OBP_BASE_URL}/obp/{Config.OBP_API_VERSION}/banks"
    headers = {
        "Authorization": f'DirectLogin token="{token}"',
        "Accept": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        banks = response.json()["banks"]
        print(f"[SUCCESS] Found {len(banks)} banks")
        print(f"\nFirst 3 banks:")
        for bank in banks[:3]:
            print(f"  - {bank['id']}: {bank.get('full_name', 'N/A')}")
        return banks
    else:
        print(f"[ERROR] Failed: {response.status_code} - {response.text}")
        raise Exception("Failed to fetch banks")

def fetch_accounts(token, bank_id):
    """Fetch PUBLIC accounts for a specific bank (no user linking required)"""
    print("\n" + "=" * 60)
    print(f"STEP 3: Fetching PUBLIC Accounts for Bank: {bank_id}")
    print("=" * 60)
    
    # Try public accounts endpoint first (most likely to have test data)
    url = f"{Config.OBP_BASE_URL}/obp/{Config.OBP_API_VERSION}/banks/{bank_id}/accounts/public"
    headers = {
        "Authorization": f'DirectLogin token="{token}"',
        "Accept": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        
        # Handle different response formats
        if isinstance(data, list):
            accounts = data
        elif isinstance(data, dict):
            accounts = data.get("accounts", [])
        else:
            accounts = []
        
        if accounts:
            print(f"[SUCCESS] Found {len(accounts)} public accounts")
            print(f"\nFirst 3 accounts:")
            for account in accounts[:3]:
                account_id = account.get('id', 'N/A')
                account_label = account.get('label', account.get('account_label', 'N/A'))
                print(f"  - {account_id}: {account_label}")
            return accounts
    
    print(f"[WARNING] No public accounts found (status: {response.status_code})")
    return []

def fetch_transactions(token, bank_id, account_id):
    """Fetch transactions for a public account"""
    print("\n" + "=" * 60)
    print(f"STEP 4: Fetching Transactions")
    print(f"Bank: {bank_id}, Account: {account_id}")
    print("=" * 60)
    
    # Try public view first, then owner view
    endpoints = [
        f"{Config.OBP_BASE_URL}/obp/{Config.OBP_API_VERSION}/banks/{bank_id}/accounts/{account_id}/public/transactions",
        f"{Config.OBP_BASE_URL}/obp/{Config.OBP_API_VERSION}/banks/{bank_id}/accounts/{account_id}/owner/transactions"
    ]
    
    headers = {
        "Authorization": f'DirectLogin token="{token}"',
        "Accept": "application/json"
    }
    
    for url in endpoints:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # Handle different response formats
            if isinstance(data, list):
                transactions = data
            elif isinstance(data, dict):
                transactions = data.get("transactions", [])
            else:
                transactions = []
            
            if transactions:
                print(f"[SUCCESS] Found {len(transactions)} transactions")
                
                print(f"\nFirst transaction sample:")
                tx = transactions[0]
                details = tx.get('details', {})
                value = details.get('value', {})
                print(f"  ID: {tx.get('id', 'N/A')}")
                print(f"  Amount: {value.get('amount', 'N/A')} {value.get('currency', 'N/A')}")
                print(f"  Description: {details.get('description', 'N/A')}")
                print(f"  Date: {details.get('completed', details.get('posted', 'N/A'))}")
                
                return transactions
    
    print(f"[WARNING] No transactions found")
    return []

def save_to_csv(transactions, bank_id):
    """Save transactions to local CSV"""
    print("\n" + "=" * 60)
    print("STEP 5: Saving to CSV")
    print("=" * 60)
    
    if not transactions:
        print("[WARNING] No transactions to save")
        return None
    
    data = []
    for tx in transactions:
        try:
            this_account = tx.get('this_account', tx.get('account', {}))
            details = tx.get('details', {})
            value = details.get('value', {})
            new_balance = details.get('new_balance', {})
            
            data.append({
                'transaction_id': tx.get('id', 'N/A'),
                'bank_id': bank_id,
                'account_id': this_account.get('id', 'N/A'),
                'amount': value.get('amount', 0),
                'currency': value.get('currency', 'N/A'),
                'description': details.get('description', 'N/A'),
                'transaction_date': details.get('completed', details.get('posted', 'N/A')),
                'balance_after': new_balance.get('amount', 0),
                'extracted_at': datetime.now().isoformat()
            })
        except Exception as e:
            print(f"[WARNING] Skipping transaction due to parsing error: {e}")
            continue
    
    if not data:
        print("[ERROR] No valid transactions to save")
        return None
    
    df = pd.DataFrame(data)
    filename = f"sample_transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(filename, index=False)
    
    print(f"[SUCCESS] Saved {len(df)} transactions to: {filename}")
    print(f"\nData shape: {df.shape}")
    print(f"\nFirst 3 rows:")
    print(df.head(3).to_string())
    print(f"\nColumn types:")
    print(df.dtypes.to_string())
    
    return df

def main():
    """Run all test steps"""
    print("\n" + "=" * 60)
    print("OPEN BANK PROJECT API - TEST SCRIPT")
    print("=" * 60)
    
    try:
        Config.validate_directlogin()
        print("[SUCCESS] Configuration loaded from .env")
    except ValueError as e:
        print(f"[ERROR] Config error: {e}")
        print("\nRequired in .env file:")
        print("   - OBP_USERNAME")
        print("   - OBP_PASSWORD")
        print("   - OBP_CONSUMER_KEY")
        print("   - OBP_DIRECTLOGIN_ENDPOINT")
        return
    
    try:
        token = authenticate()
        banks = fetch_banks(token)
        
        if not banks:
            print("\n[ERROR] No banks available")
            return
        
        bank_id = banks[0].get('id', '')
        if not bank_id:
            print("\n[ERROR] Invalid bank data structure")
            return
        
        accounts = fetch_accounts(token, bank_id)
        
        if not accounts:
            print("\n[WARNING] No accounts found, trying next bank...")
            for bank in banks[1:4]:
                bank_id = bank.get('id', '')
                if bank_id:
                    accounts = fetch_accounts(token, bank_id)
                    if accounts:
                        break
        
        if not accounts:
            print("\n[ERROR] No accounts found in any bank")
            return
        
        account_id = accounts[0].get('id', '')
        if not account_id:
            print("\n[ERROR] Invalid account data structure")
            return
        
        transactions = fetch_transactions(token, bank_id, account_id)
        
        if transactions:
            save_to_csv(transactions, bank_id)
            print("\n" + "=" * 60)
            print("[SUCCESS] TEST COMPLETE - API WORKS!")
            print("=" * 60)
            print("\nNext steps:")
            print("1. Review the generated CSV file")
            print("2. Validate data schema and quality")
            print("3. Ready to build Lambda function for S3 upload")
        else:
            print("\n[WARNING] No transactions found for this account")
            print("Trying more accounts...")
            
            # Try up to 10 accounts to find transactions
            for account in accounts[1:10]:
                account_id = account.get('id', '')
                if account_id:
                    transactions = fetch_transactions(token, bank_id, account_id)
                    if transactions:
                        save_to_csv(transactions, bank_id)
                        print("\n" + "=" * 60)
                        print("[SUCCESS] TEST COMPLETE - FOUND TRANSACTIONS!")
                        print("=" * 60)
                        break
            else:
                # If still no transactions, try another bank
                print("\n[WARNING] No transactions in this bank, trying another bank...")
                for bank in banks[1:5]:
                    bank_id = bank.get('id', '')
                    if bank_id:
                        accounts = fetch_accounts(token, bank_id)
                        if accounts:
                            for account in accounts[:5]:
                                account_id = account.get('id', '')
                                if account_id:
                                    transactions = fetch_transactions(token, bank_id, account_id)
                                    if transactions:
                                        save_to_csv(transactions, bank_id)
                                        print("\n" + "=" * 60)
                                        print("[SUCCESS] TEST COMPLETE - FOUND TRANSACTIONS!")
                                        print("=" * 60)
                                        return
                
                print("\n[WARNING] No transactions found in any accounts")
                print("This is okay - authentication and account fetching work!")
                print("You can proceed with building the Lambda function.")
            
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        print("\nFull error details:")
        traceback.print_exc()


if __name__ == "__main__":
    main()
