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
  description = "Subnet IDs for pipeline task"
  type        = list(string)
}

variable "ecs_security_group_id" {
  description = "ECS security group ID"
  type        = string
}

variable "ecs_cluster_arn" {
  description = "ECS cluster ARN"
  type        = string
}

variable "execution_role_arn" {
  description = "ECS execution role ARN"
  type        = string
}

variable "task_role_arn" {
  description = "ECS task role ARN"
  type        = string
}

variable "pipeline_repository_url" {
  description = "ECR repository URL for pipeline image"
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

variable "s3_bucket" {
  description = "S3 bucket name for models and parquet storage"
  type        = string
}

variable "schedule_expression" {
  description = "EventBridge schedule expression"
  type        = string
  default     = "rate(1 hour)"
}

variable "task_cpu" {
  description = "CPU units for pipeline task"
  type        = number
  default     = 1024  # 1 vCPU — more than poller, runs ML inference
}

variable "task_memory" {
  description = "Memory for pipeline task in MB"
  type        = number
  default     = 2048  # 2GB — needs to load 12 LightGBM models into memory
}