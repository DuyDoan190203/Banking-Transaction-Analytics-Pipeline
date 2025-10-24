output "s3_bucket_name" {
  description = "Name of the S3 bucket for raw data"
  value       = module.s3_bucket.bucket_name
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = module.s3_bucket.bucket_arn
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = module.lambda_function.lambda_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = module.lambda_function.lambda_arn
}

output "eventbridge_rule_name" {
  description = "Name of the EventBridge schedule rule"
  value       = module.eventbridge_schedule.rule_name
}

output "eventbridge_rule_arn" {
  description = "ARN of the EventBridge schedule rule"
  value       = module.eventbridge_schedule.rule_arn
}

