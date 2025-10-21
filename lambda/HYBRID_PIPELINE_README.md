# Hybrid Data Pipeline - Real API + Synthetic Transactions

## What This Does

Combines real banking API data with synthetic transactions - this is the production pattern for test data generation.

### Data Flow

```
Real OBP API              Synthetic Generator           Output
─────────────            ────────────────────          ───────

Banks API         →      [Keep Real]            →      hybrid_banks.csv
  ↓                                                     (REAL_API)
Accounts API      →      [Keep Real]            →      hybrid_accounts.csv
  ↓                                                     (REAL_API)
Real Account IDs  →      Generate 100 txns      →      hybrid_transactions.csv
                         per account                    (SYNTHETIC)
```

## Why This Approach?

- Real API Structure - Actual bank and account IDs from OBP
- Synthetic Transactions - Generated with Faker for testing
- Data Lineage - Clear labeling of data source
- Production Pattern - How data engineers test pipelines
- Privacy Compliant - No real transaction data

## Quick Start

### 1. Install Faker

```bash
pip install Faker==22.0.0
```

### 2. Run the Pipeline

```bash
python hybrid_data_pipeline.py
```

### 3. Check Output

Three CSV files will be created:
- `hybrid_banks_YYYYMMDD_HHMMSS.csv` - Real banks from API
- `hybrid_accounts_YYYYMMDD_HHMMSS.csv` - Real accounts from API
- `hybrid_transactions_YYYYMMDD_HHMMSS.csv` - 100 synthetic transactions per account

## What Gets Generated

### Banks (Real API Data)
```csv
bank_id,bank_name,data_source,extracted_at
rbs,The Royal Bank of Scotland,REAL_API,2025-01-21T...
test-bank,Test Bank,REAL_API,2025-01-21T...
```

### Accounts (Real API Data)
```csv
account_id,bank_id,account_label,account_type,data_source,extracted_at
MyAcc9821,rbs,ManualAccount,N/A,REAL_API,2025-01-21T...
rbs-02,rbs,None,N/A,REAL_API,2025-01-21T...
```

### Transactions (Synthetic Data)
```csv
transaction_id,bank_id,account_id,amount,currency,transaction_type,description,merchant,transaction_date,balance_after,data_source
synth_MyAcc9821_0001,rbs,MyAcc9821,-45.67,GBP,POS Purchase,POS Purchase at Starbucks,Starbucks,2025-01-15T14:30:00,1234.56,SYNTHETIC
synth_MyAcc9821_0002,rbs,MyAcc9821,2500.00,GBP,Salary Deposit,Salary Deposit from Tech Corp,None,2025-01-01T09:00:00,3734.56,SYNTHETIC
```

## Transaction Types Generated

The synthetic data includes realistic transaction types:

| Type | Direction | Amount Range |
|------|-----------|--------------|
| ATM Withdrawal | Debit | $5 - $500 |
| POS Purchase | Debit | $5 - $500 |
| Online Transfer | Debit | $5 - $500 |
| Direct Debit | Debit | $5 - $500 |
| Bill Payment | Debit | $5 - $500 |
| Salary Deposit | Credit | $500 - $5000 |
| Refund | Credit | $500 - $5000 |
| Cash Deposit | Credit | $500 - $5000 |

## Data Characteristics

### Realistic Patterns
- Dates: Last 90 days
- Times: Random hours (0-23)
- Weekday/Weekend flags
- Balance tracking
- Currency variety (GBP, EUR, USD)
- Merchants and counterparties
- Running account balance

### Data Volume
- Banks: 10 (from API)
- Accounts: ~10 (from API, varies by sandbox)
- Transactions: 100 per account = 1,000 total

## Use Cases

### 1. Lambda Development
Test your extraction logic with real account IDs

### 2. S3 Data Lake
Upload structured data for pipeline testing

### 3. dbt Transformations
Build dimensional models with realistic data

### 4. Fraud Detection
Train models on synthetic transactions with patterns

### 5. BI Dashboards
Create visualizations with meaningful data

## Data Source Tracking

Every row is labeled:

```python
# Real data
'data_source': 'REAL_API'

# Synthetic data
'data_source': 'SYNTHETIC'
```

This ensures clear data lineage - crucial for compliance.

## Sample Output

```
============================================================
HYBRID DATA PIPELINE: Real API + Synthetic Transactions
============================================================

STEP 1: Authentication (REAL API)
✅ Authentication successful! Token: eyJhbGciOiJIUzI1NiJ9...

STEP 2: Fetching Banks (REAL API)
✅ Found 195 real banks
✅ Processed 10 banks

STEP 3: Fetching Accounts (REAL API)
  ✅ rbs: Found 8 accounts
  ✅ test-bank: Found 1 accounts
✅ Total accounts fetched: 9

STEP 4: Generating Synthetic Transactions (100 per account)
  ✅ Generated 100 transactions for account: MyAcc9821
  ✅ Generated 100 transactions for account: rbs-02
  ...
✅ Total synthetic transactions: 900

STEP 5: Saving Hybrid Datasets
✅ Saved 10 banks to: hybrid_banks_20250121_143000.csv
✅ Saved 9 accounts to: hybrid_accounts_20250121_143000.csv
✅ Saved 900 transactions to: hybrid_transactions_20250121_143000.csv

DATA SUMMARY
📊 BANKS (Real API Data)
Total banks: 10

📊 ACCOUNTS (Real API Data)
Total accounts: 9
Accounts per bank:
rbs         8
test-bank   1

📊 TRANSACTIONS (Synthetic Data)
Total transactions: 900
Transactions per account: 100
Date range: 2024-10-23T... to 2025-01-21T...

Transaction types:
ATM Withdrawal     112
POS Purchase       115
Online Transfer    108
...

DATA LINEAGE VALIDATION
✅ Banks: 10/10 from REAL_API
✅ Accounts: 9/9 from REAL_API
✅ Transactions: 900/900 SYNTHETIC
✅ All synthetic transactions linked to REAL accounts
✅ All transactions linked to REAL banks

✅ HYBRID PIPELINE COMPLETE!
```

## Why This is Production-Ready

### 1. Real API Integration
- Actual banking API authentication
- Real bank and account structures
- Production API endpoints

### 2. Synthetic Test Data
- Privacy-compliant (no real PII)
- Realistic transaction patterns
- Scalable (100 txns per account)

### 3. Data Lineage
- Clear source labeling
- Audit trail
- Compliance-ready

### 4. Testing Flexibility
- Can regenerate data anytime
- Controllable transaction patterns
- Known data distributions

## Next Steps

1. Upload to S3 - Use these CSVs as your raw layer
2. Build Lambda - Extract logic validated
3. Create dbt models - Transform to dimensional schema
4. Train fraud models - Synthetic data is perfect for ML
5. Build dashboards - Visualize realistic patterns

## File Structure

```
lambda/
├── hybrid_data_pipeline.py       ← Main pipeline script
├── config.py                     ← Credentials loader
├── requirements.txt              ← Includes Faker
└── Output CSVs:
    ├── hybrid_banks_*.csv        ← Real API data
    ├── hybrid_accounts_*.csv     ← Real API data
    └── hybrid_transactions_*.csv ← Synthetic data
```

## What This Demonstrates

For your portfolio, this shows:

- API Integration - Real banking API
- Data Generation - Faker for test data
- Data Lineage - Source tracking
- Production Patterns - Real + synthetic approach
- Scalability - Parameterized generation
- Data Quality - Validation checks

This is exactly how data engineers create test data in production.

Run it now:
```bash
pip install Faker==22.0.0
python hybrid_data_pipeline.py
```

