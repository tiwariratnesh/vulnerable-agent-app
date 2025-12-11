variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
  default     = "vpc-12345678"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "db_password" {
  description = "Database password"
  type        = string
  default     = "insecure_password"
}

variable "api_key" {
  description = "API key for services"
  type        = string
  default     = "sk-api-key-hardcoded-12345"
}

variable "allowed_ips" {
  description = "Allowed IP addresses"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}


