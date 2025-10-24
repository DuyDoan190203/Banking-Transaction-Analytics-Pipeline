terraform {
  required_version = ">= 1.0.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region     = var.aws_region
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
}

locals {
  project_name = "banking-transaction-pipeline"
  environment  = "prod"
  
  common_tags = {
    Project     = local.project_name
    Environment = local.environment
    ManagedBy   = "Terraform"
  }
}

# S3 Bucket for raw data storage
module "s3_bucket" {
  source = "./modules/s3"
  
  bucket_name = "${local.project_name}-raw-data-${var.aws_account_id}"
  environment = local.environment
  tags        = local.common_tags
}

# Lambda function for data ingestion
module "lambda_function" {
  source = "./modules/lambda"
  
  function_name = "${local.project_name}-ingestion"
  s3_bucket_name = module.s3_bucket.bucket_name
  
  environment_variables = {
    OBP_BASE_URL              = var.obp_base_url
    OBP_API_VERSION           = var.obp_api_version
    OBP_USERNAME              = var.obp_username
    OBP_PASSWORD              = var.obp_password
    OBP_CONSUMER_KEY          = var.obp_consumer_key
    OBP_DIRECTLOGIN_ENDPOINT  = var.obp_directlogin_endpoint
    S3_BUCKET_NAME            = module.s3_bucket.bucket_name
  }
  
  s3_bucket_arn = module.s3_bucket.bucket_arn
  tags          = local.common_tags
}

# EventBridge schedule for daily execution
module "eventbridge_schedule" {
  source = "./modules/eventbridge"
  
  schedule_name   = "${local.project_name}-daily-schedule"
  lambda_arn      = module.lambda_function.lambda_arn
  lambda_name     = module.lambda_function.lambda_name
  schedule_expression = var.schedule_expression
  
  tags = local.common_tags
}

