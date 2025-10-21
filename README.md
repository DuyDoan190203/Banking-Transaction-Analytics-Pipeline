# Banking Transaction Analytics Pipeline

End-to-end data pipeline for banking transaction analysis and fraud detection using Open Bank Project API.

## Project Structure

* `lambda/` - Python code for data extraction
* `terraform/` - Infrastructure as Code
* `dbt/` - Data transformation models
* `.gitignore` - Git ignore file

## Prerequisites

* AWS account
* Terraform installed (version >= 1.0.0)
* Python 3.11
* Open Bank Project API credentials

## Setup

1. Clone this repository

2. Set up your AWS credentials:
   * Create an AWS IAM user with appropriate permissions
   * Configure your AWS CLI or set the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables

3. Create a `.env` file in the `lambda/` directory with the following content:
   ```
   OBP_BASE_URL=https://apisandbox.openbankproject.com
   OBP_API_VERSION=v5.1.0
   OBP_USERNAME=your_username
   OBP_PASSWORD=your_password
   OBP_CONSUMER_KEY=your_consumer_key
   OBP_DIRECTLOGIN_ENDPOINT=https://apisandbox.openbankproject.com/my/logins/direct
   ```

4. Install Python dependencies:
   ```
   cd lambda
   pip install -r requirements.txt
   ```

## Usage

### Test API Connection

Test the Open Bank Project API connection:

```bash
cd lambda
python test_fetch_data.py
```

### Generate Hybrid Dataset

Generate hybrid dataset with real API data and synthetic transactions:

```bash
cd lambda
python hybrid_data_pipeline.py
```

The pipeline will:
1. Fetch real banks from OBP API
2. Fetch real accounts from OBP API
3. Generate 100 synthetic transactions per account using Faker
4. Save to CSV files with clear data source labeling

Output files:
* `hybrid_banks_YYYYMMDD_HHMMSS.csv` - Real banks (data_source: REAL_API)
* `hybrid_accounts_YYYYMMDD_HHMMSS.csv` - Real accounts (data_source: REAL_API)
* `hybrid_transactions_YYYYMMDD_HHMMSS.csv` - Synthetic transactions (data_source: SYNTHETIC)

### Deploy Infrastructure

Deploy AWS infrastructure using Terraform:

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

## Data Pipeline Architecture

```
Open Bank Project API
        ↓
   AWS Lambda (Python)
        ↓
   S3 Data Lake (Raw)
        ↓
   dbt Transformations
        ↓
   Data Warehouse
        ↓
   BI Dashboards
```

## Technology Stack

| Component | Technology |
|-----------|------------|
| Data Source | Open Bank Project API |
| Extraction | AWS Lambda |
| Storage | AWS S3 |
| Orchestration | AWS EventBridge |
| Transformation | dbt |
| Infrastructure | Terraform |
| Language | Python 3.11 |

## Data Models

### Staging Layer
* `stg_transactions` - Cleaned transaction data
* `stg_accounts` - Cleaned account data
* `stg_banks` - Cleaned bank data

### Marts Layer
* `dim_account` - Account dimension
* `fact_transactions` - Transaction fact table
* `fct_fraud_scores` - Fraud detection model

## Key Features

* Real-time fraud detection using statistical anomalies
* Multi-currency transaction support
* Automated data quality checks
* Clear data lineage tracking
* Privacy-compliant synthetic test data

## Security

* `.env` file is in `.cursorignore` - never committed to git
* CSV output files are ignored
* Only example templates are tracked in version control

## Cleanup

To remove all created resources:

```bash
cd terraform
terraform destroy
```

## About

This project demonstrates production data engineering patterns:
* REST API integration with banking systems
* Hybrid data approach (real structure + synthetic data)
* Infrastructure as Code with Terraform
* Data transformation with dbt
* Statistical fraud detection
* End-to-end data pipeline architecture

