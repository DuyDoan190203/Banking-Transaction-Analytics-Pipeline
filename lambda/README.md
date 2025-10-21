# Banking Transaction Pipeline - Lambda Functions

Simple test script to verify Open Bank Project API connection before deploying to AWS Lambda.

## Quick Start

### 1. Install Dependencies

```bash
cd lambda
pip install -r requirements.txt
```

### 2. Configure Credentials

Your `.env` file should already have these values (keep it in `.cursorignore`):

```
OBP_BASE_URL=https://apisandbox.openbankproject.com
OBP_API_VERSION=v5.1.0
OBP_USERNAME=your_username
OBP_PASSWORD=your_password
OBP_CONSUMER_KEY=your_consumer_key
OBP_DIRECTLOGIN_ENDPOINT=https://apisandbox.openbankproject.com/my/logins/direct
```

### 3. Run Test Script

```bash
python test_fetch_data.py
```

## What the Test Does

1. **Authenticate** - Tests DirectLogin authentication and gets token
2. **Fetch Banks** - Retrieves list of available banks
3. **Fetch Accounts** - Gets accounts for the first bank
4. **Fetch Transactions** - Retrieves transactions for the first account
5. **Save to CSV** - Exports sample data to local CSV file

## Expected Output

```
============================================================
OPEN BANK PROJECT API - TEST SCRIPT
============================================================
✅ Configuration loaded from .env

============================================================
STEP 1: Testing Authentication
============================================================
Endpoint: https://apisandbox.openbankproject.com/my/logins/direct
Username: your_username
✅ Authentication successful! Token: abcd1234efgh5678...

============================================================
STEP 2: Fetching Banks
============================================================
✅ Found 3 banks

First 3 banks:
  - gh.29.uk: The Royal Bank of Scotland
  - ...

============================================================
STEP 3: Fetching Accounts for Bank: gh.29.uk
============================================================
✅ Found 5 accounts

First 3 accounts:
  - account_id_1: Savings Account
  - ...

============================================================
STEP 4: Fetching Transactions
Bank: gh.29.uk, Account: account_id_1
============================================================
✅ Found 20 transactions

First transaction sample:
  ID: tx_abc123
  Amount: -50.00 GBP
  Description: ATM Withdrawal
  Date: 2025-01-15T14:30:00Z

============================================================
STEP 5: Saving to CSV
============================================================
✅ Saved 20 transactions to: sample_transactions_20250121_143000.csv

Data shape: (20, 9)

First 3 rows:
   transaction_id  bank_id  account_id  amount currency ...
0        tx_abc123  gh.29.uk  acc_123   -50.00      GBP ...
...

============================================================
✅ TEST COMPLETE - API WORKS!
============================================================

Next steps:
1. Review the generated CSV file
2. Validate data schema and quality
3. Ready to build Lambda function for S3 upload
```

## Output

The script generates a CSV file with this schema:

| Column | Type | Description |
|--------|------|-------------|
| `transaction_id` | string | Unique transaction ID |
| `bank_id` | string | Bank identifier |
| `account_id` | string | Account identifier |
| `amount` | float | Transaction amount (negative for debits) |
| `currency` | string | Currency code (GBP, USD, etc.) |
| `description` | string | Transaction description |
| `transaction_date` | datetime | When transaction occurred |
| `balance_after` | float | Account balance after transaction |
| `extracted_at` | datetime | When data was fetched |

## Troubleshooting

### Authentication Failed

```
❌ Authentication failed: 401
```

**Fix:** Check your credentials in `.env`:
- `OBP_USERNAME`
- `OBP_PASSWORD`
- `OBP_CONSUMER_KEY`

### No Banks Found

```
❌ Failed: 403 - Insufficient permissions
```

**Fix:** Your API credentials may not have access. Register at:
https://apisandbox.openbankproject.com

### No Transactions

```
⚠️  No transactions found for this account
```

**Note:** This is normal - some sandbox accounts may be empty. The test will try multiple banks/accounts.

## Files

- `test_fetch_data.py` - Main test script
- `config.py` - Configuration loader from .env
- `requirements.txt` - Python dependencies
- `.env` - Your credentials (in `.cursorignore`)

## Security

- `.env` file is in `.cursorignore` - never committed to git
- CSV files with `sample_transactions_*.csv` pattern are also ignored
- Only example templates (`env.example`) are tracked in git

## Next Steps

Once this test works:
1. Review the CSV data structure
2. Implement Lambda function with same logic
3. Add S3 upload instead of CSV save
4. Deploy with Terraform
5. Schedule with EventBridge

