variable "function_name" {
  description = "Name of the Lambda function"
  type        = string
}

variable "s3_bucket_name" {
  description = "Name of the S3 bucket for data storage"
  type        = string
}

variable "s3_bucket_arn" {
  description = "ARN of the S3 bucket"
  type        = string
}

variable "environment_variables" {
  description = "Environment variables for Lambda function"
  type        = map(string)
  default     = {}
}

variable "tags" {
  description = "Common tags for resources"
  type        = map(string)
  default     = {}
}

