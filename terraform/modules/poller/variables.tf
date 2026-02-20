variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "subnet_ids" {
  description = "Subnet IDs for poller task"
  type        = list(string)
}

variable "ecs_security_group_id" {
  description = "ECS security group ID"
  type        = string
}

variable "ecs_cluster_arn" {  # ← Changed from ecs_cluster_id
  description = "ECS cluster ARN (must be full ARN, not just name)"
  type        = string
}

variable "execution_role_arn" {
  description = "ECS execution role ARN (from ECS module)"
  type        = string
}

variable "task_role_arn" {
  description = "ECS task role ARN (from ECS module)"
  type        = string
}

variable "poller_repository_url" {
  description = "ECR repository URL for poller image"
  type        = string
}

variable "image_tag" {
  description = "Docker image tag"
  type        = string
  default     = "latest"
}

variable "redis_host" {
  description = "Redis endpoint"
  type        = string
}

variable "redis_port" {
  description = "Redis port"
  type        = number
  default     = 6379
}

variable "openweather_api_key" {
  description = "OpenWeather API key"
  type        = string
  sensitive   = true
}

variable "schedule_expression" {
  description = "EventBridge schedule expression"
  type        = string
  default     = "rate(1 hour)"
}

variable "task_cpu" {
  description = "CPU units for poller task"
  type        = number
  default     = 512  # 0.5 vCPU
}

variable "task_memory" {
  description = "Memory for poller task in MB"
  type        = number
  default     = 1024  # 1 GB
}