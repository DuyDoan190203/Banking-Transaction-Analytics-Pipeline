variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "eu-north-1"
}

variable "aws_access_key" {
  description = "AWS access key (set via TF_VAR_aws_access_key)"
  type        = string
  sensitive   = true
}

variable "aws_secret_key" {
  description = "AWS secret key (set via TF_VAR_aws_secret_key)"
  type        = string
  sensitive   = true
}

variable "aws_account_id" {
  description = "AWS account ID for unique bucket naming (set via TF_VAR_aws_account_id)"
  type        = string
}

variable "obp_base_url" {
  description = "Open Bank Project API base URL"
  type        = string
  default     = "https://apisandbox.openbankproject.com"
}

variable "obp_api_version" {
  description = "Open Bank Project API version"
  type        = string
  default     = "v5.1.0"
}

variable "obp_username" {
  description = "Open Bank Project username (set via TF_VAR_obp_username)"
  type        = string
  sensitive   = true
}

variable "obp_password" {
  description = "Open Bank Project password (set via TF_VAR_obp_password)"
  type        = string
  sensitive   = true
}

variable "obp_consumer_key" {
  description = "Open Bank Project consumer key (set via TF_VAR_obp_consumer_key)"
  type        = string
  sensitive   = true
}

variable "obp_directlogin_endpoint" {
  description = "Open Bank Project DirectLogin endpoint"
  type        = string
  default     = "https://apisandbox.openbankproject.com/my/logins/direct"
}

variable "schedule_expression" {
  description = "EventBridge schedule expression (cron or rate)"
  type        = string
  default     = "rate(1 day)"
}

