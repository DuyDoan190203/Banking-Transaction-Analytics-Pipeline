variable "schedule_name" {
  description = "Name of the EventBridge schedule rule"
  type        = string
}

variable "lambda_arn" {
  description = "ARN of the Lambda function to trigger"
  type        = string
}

variable "lambda_name" {
  description = "Name of the Lambda function"
  type        = string
}

variable "schedule_expression" {
  description = "Schedule expression (cron or rate)"
  type        = string
}

variable "tags" {
  description = "Common tags for resources"
  type        = map(string)
  default     = {}
}

