"""
AWS Lambda Handler for Banking Transaction Data Pipeline 
Fetches data from Open Bank Project API and uploads to S3
"""

import json
import boto3
import requests
from datetime import datetime, timedelta
from faker import Faker
import random
import os
import csv
from io import StringIO

fake = Faker()

# Environment variables
OBP_BASE_URL = os.environ.get('OBP_BASE_URL')
OBP_API_VERSION = os.environ.get('OBP_API_VERSION')
OBP_USERNAME = os.environ.get('OBP_USERNAME')
OBP_PASSWORD = os.environ.get('OBP_PASSWORD')
OBP_CONSUMER_KEY = os.environ.get('OBP_CONSUMER_KEY')
OBP_DIRECTLOGIN_ENDPOINT = os.environ.get('OBP_DIRECTLOGIN_ENDPOINT')
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')

s3_client = boto3.client('s3')


def authenticate():
    """Authenticate with OBP API and return token"""
    print("Authenticating with OBP API...")
    
    headers = {
        "Authorization": f'DirectLogin username="{OBP_USERNAME}", password="{OBP_PASSWORD}", consumer_key="{OBP_CONSUMER_KEY}"',
        "Accept": "application/json"
    }
    
    response = requests.post(OBP_DIRECTLOGIN_ENDPOINT, headers=headers)
    
    if response.status_code == 201:
        token = response.json()["token"]
        print(f"Authentication successful")
        return token
    else:
        raise Exception(f"Authentication failed: {response.status_code}")


def fetch_real_banks(token):
    """Fetch real banks from OBP API"""
    print("Fetching banks...")
    
    url = f"{OBP_BASE_URL}/obp/{OBP_API_VERSION}/banks"
    headers = {
        "Authorization": f'DirectLogin token="{token}"',
        "Accept": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        banks = response.json()["banks"]
        
        banks_data = []
        for bank in banks[:10]:
            banks_data.append({
                'bank_id': bank['id'],
                'bank_name': bank.get('full_name', bank.get('short_name', 'N/A')),
                'data_source': 'REAL_API',
                'extracted_at': datetime.now().isoformat()
            })
        
        print(f"Fetched {len(banks_data)} banks")
        return banks_data
    else:
        raise Exception(f"Failed to fetch banks: {response.status_code}")


def fetch_real_accounts(token, bank_ids):
    """Fetch real public accounts from OBP API"""
    print("Fetching accounts...")
    
    all_accounts = []
    
    for bank_id in bank_ids:
        url = f"{OBP_BASE_URL}/obp/{OBP_API_VERSION}/banks/{bank_id}/accounts/public"
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
                for account in accounts:
                    all_accounts.append({
                        'account_id': account.get('id', 'N/A'),
                        'bank_id': bank_id,
                        'account_label': account.get('label', account.get('account_label', 'N/A')),
                        'account_type': account.get('account_type', 'N/A'),
                        'data_source': 'REAL_API',
                        'extracted_at': datetime.now().isoformat()
                    })
    
    print(f"Fetched {len(all_accounts)} accounts")
    return all_accounts


def generate_synthetic_transactions(accounts, transactions_per_account=100):
    """Generate synthetic transactions linked to real account IDs"""
    print(f"Generating {transactions_per_account} synthetic transactions per account...")
    
    all_transactions = []
    transaction_types = ['ATM Withdrawal', 'POS Purchase', 'Online Transfer', 'Direct Debit', 
                        'Salary Deposit', 'Refund', 'Bill Payment', 'Cash Deposit']
    
    merchants = ['Amazon', 'Walmart', 'Starbucks', 'Shell Gas', 'Netflix', 'Spotify', 
                'Uber', 'Restaurant', 'Supermarket', 'Pharmacy']
    
    for account in accounts:
        account_id = account['account_id']
        bank_id = account['bank_id']
        
        starting_balance = random.uniform(1000, 50000)
        current_balance = starting_balance
        
        for i in range(transactions_per_account):
            days_ago = random.randint(0, 90)
            tx_date = datetime.now() - timedelta(days=days_ago)
            
            tx_type = random.choice(transaction_types)
            
            if tx_type in ['Salary Deposit', 'Refund', 'Cash Deposit']:
                amount = round(random.uniform(500, 5000), 2)
                is_debit = False
            else:
                amount = round(random.uniform(5, 500), 2)
                is_debit = True
            
            if is_debit:
                current_balance -= amount
                amount_signed = -amount
            else:
                current_balance += amount
                amount_signed = amount
            
            if tx_type == 'POS Purchase':
                description = f"{tx_type} at {random.choice(merchants)}"
            elif tx_type == 'Online Transfer':
                description = f"{tx_type} to {fake.name()}"
            elif tx_type == 'Salary Deposit':
                description = f"{tx_type} from {fake.company()}"
            else:
                description = tx_type
            
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
    
    print(f"Generated {len(all_transactions)} transactions")
    return all_transactions


def dict_list_to_csv(data_list):
    """Convert list of dictionaries to CSV string"""
    if not data_list:
        return ""
    
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=data_list[0].keys())
    writer.writeheader()
    writer.writerows(data_list)
    return output.getvalue()


def upload_to_s3(data_list, dataset_name, timestamp):
    """Upload data list to S3 as CSV"""
    csv_content = dict_list_to_csv(data_list)
    
    date_partition = timestamp.strftime('%Y/%m/%d')
    file_key = f"raw/{dataset_name}/{date_partition}/{dataset_name}_{timestamp.strftime('%Y%m%d_%H%M%S')}.csv"
    
    s3_client.put_object(
        Bucket=S3_BUCKET_NAME,
        Key=file_key,
        Body=csv_content,
        ContentType='text/csv'
    )
    
    print(f"Uploaded {len(data_list)} records to s3://{S3_BUCKET_NAME}/{file_key}")
    return file_key


def lambda_handler(event, context):
    """Main Lambda handler"""
    print("Starting Banking Transaction Pipeline...")
    
    try:
        timestamp = datetime.now()
        
        # Step 1: Authenticate
        token = authenticate()
        
        # Step 2: Fetch real banks
        banks_data = fetch_real_banks(token)
        
        # Step 3: Fetch real accounts
        bank_ids_to_try = [bank['bank_id'] for bank in banks_data[:3]]
        accounts_data = fetch_real_accounts(token, bank_ids_to_try)
        
        if not accounts_data:
            print("No accounts found in first 3 banks, trying more...")
            bank_ids_to_try = [bank['bank_id'] for bank in banks_data[:10]]
            accounts_data = fetch_real_accounts(token, bank_ids_to_try)
        
        if not accounts_data:
            raise Exception("No accounts found in any banks")
        
        # Step 4: Generate synthetic transactions
        transactions_data = generate_synthetic_transactions(accounts_data, transactions_per_account=100)
        
        # Step 5: Upload to S3
        banks_key = upload_to_s3(banks_data, 'banks', timestamp)
        accounts_key = upload_to_s3(accounts_data, 'accounts', timestamp)
        transactions_key = upload_to_s3(transactions_data, 'transactions', timestamp)
        
        # Success response
        result = {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Pipeline completed successfully',
                'timestamp': timestamp.isoformat(),
                'records': {
                    'banks': len(banks_data),
                    'accounts': len(accounts_data),
                    'transactions': len(transactions_data)
                },
                's3_files': {
                    'banks': banks_key,
                    'accounts': accounts_key,
                    'transactions': transactions_key
                }
            })
        }
        
        print(f"Pipeline completed: {len(banks_data)} banks, {len(accounts_data)} accounts, {len(transactions_data)} transactions")
        return result
        
    except Exception as e:
        print(f"Pipeline failed: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Pipeline failed',
                'error': str(e)
            })
        }

