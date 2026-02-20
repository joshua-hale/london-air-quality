variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where ALB will be deployed"
  type        = string
}

variable "subnet_ids" {
  description = "Subnet IDs for ALB (use public subnets)"
  type        = list(string)
}

variable "security_group_id" {
  description = "Security group ID for ALB"
  type        = string
}

variable "health_check_path" {
  description = "Health check path for target group"
  type        = string
  default     = "/health"
}

variable "health_check_interval" {
  description = "Health check interval in seconds"
  type        = number
  default     = 30
}

variable "health_check_timeout" {
  description = "Health check timeout in seconds"
  type        = number
  default     = 5
}

variable "health_check_healthy_threshold" {
  description = "Number of consecutive successful health checks"
  type        = number
  default     = 2
}

variable "health_check_unhealthy_threshold" {
  description = "Number of consecutive failed health checks"
  type        = number
  default     = 3
}

variable "health_check_matcher" {
  description = "HTTP status codes to consider healthy"
  type        = string
  default     = "200-399"
}

variable "deregistration_delay" {
  description = "Time to wait before deregistering target (seconds)"
  type        = number
  default     = 30
}

variable "target_port" {
  description = "Port on which targets receive traffic"
  type        = number
  default     = 8000
}

variable "enable_deletion_protection" {
  description = "Enable deletion protection for ALB"
  type        = bool
  default     = false
}

variable "idle_timeout" {
  description = "Idle timeout value in seconds"
  type        = number
  default     = 60
}