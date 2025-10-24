# Banking Transaction Analytics Pipeline

End-to-end data pipeline for banking transaction analysis and fraud detection using Open Bank Project API.

## Project Structure

* `terraform/`: Terraform configuration files
* `lambda/`: Python code for the Lambda function
* `dbt/` - Data transformation models
* `.gitignore`: Git ignore file

## Prerequisites

* AWS account
* Terraform installed (version >= 1.0.0)
* Python 3.10
* Open Bank Project API credentials

## Setup

1. Clone this repository

2. Set up your AWS credentials:
   * Create an AWS IAM user with appropriate permissions
   * Configure your AWS CLI or set environment variables

3. Create a `.env` file with the following content:
   ```
   OBP_BASE_URL=https://apisandbox.openbankproject.com
   OBP_API_VERSION=v5.1.0
   OBP_USERNAME=your_username
   OBP_PASSWORD=your_password
   OBP_CONSUMER_KEY=your_consumer_key
   OBP_DIRECTLOGIN_ENDPOINT=https://apisandbox.openbankproject.com/my/logins/direct
   ```

4. Package the Lambda function:
   ```
   cd terraform
   .\build_lambda.ps1
   ```

## Deployment

1. Set environment variables for Terraform:
   ```powershell
   $env:TF_VAR_aws_access_key = "your_aws_access_key"
   $env:TF_VAR_aws_secret_key = "your_aws_secret_key"
   $env:TF_VAR_aws_account_id = "your_account_id"
   $env:TF_VAR_obp_username = "your_username"
   $env:TF_VAR_obp_password = "your_password"
   $env:TF_VAR_obp_consumer_key = "your_consumer_key"
   ```

2. Initialize Terraform:
   ```
   cd terraform
   terraform init
   ```

3. Review the Terraform plan:
   ```
   terraform plan
   ```

4. Apply the Terraform configuration:
   ```
   terraform apply
   ```

## Usage

| Component | Technology |
|-----------|------------|
| Data Source | Open Bank Project API |
| Extraction | AWS Lambda |
| Storage | AWS S3 |
| Orchestration | AWS EventBridge |
| Transformation | dbt |
| Infrastructure | Terraform |
| Language | Python 3.11 |

The Lambda function will automatically fetch banking data and generate synthetic transactions, storing them in the S3 bucket. The data is stored in CSV format with date partitioning:

### Staging Layer
* `stg_transactions` - Cleaned transaction data
* `stg_accounts` - Cleaned account data
* `stg_banks` - Cleaned bank data
* `raw/banks/YYYY/MM/DD/banks_YYYYMMDD_HHMMSS.csv`
* `raw/accounts/YYYY/MM/DD/accounts_YYYYMMDD_HHMMSS.csv`
* `raw/transactions/YYYY/MM/DD/transactions_YYYYMMDD_HHMMSS.csv`

## Key Features

* Real-time fraud detection using statistical anomalies
* Multi-currency transaction support
* Automated data quality checks
* Clear data lineage tracking
* Privacy-compliant synthetic test data

The pipeline runs automatically on a daily schedule via AWS EventBridge.

## Cleanup

To remove all created resources:

```
terraform destroy
```

## Architecture

```
┌─────────────────────┐
│  EventBridge        │  Daily Schedule
│  (Scheduler)        │
└──────────┬──────────┘
           │ Trigger
           ▼
┌─────────────────────┐
│  Lambda Function    │  1. Authenticate with OBP API
│                     │  2. Fetch real banks & accounts
│                     │  3. Generate synthetic transactions
└──────────┬──────────┘
           │ Upload CSV
           ▼
┌─────────────────────┐
│  S3 Data Lake       │  Date-partitioned storage
│  (Raw Layer)        │  raw/{dataset}/YYYY/MM/DD/
└─────────────────────┘
```

## Technology Stack

| Component | Technology |
|-----------|------------|
| Data Source | Open Bank Project API |
| Extraction | AWS Lambda (Python 3.10) |
| Storage | AWS S3 |
| Orchestration | AWS EventBridge |
| Infrastructure | Terraform |


