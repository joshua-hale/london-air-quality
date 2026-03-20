variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "eu-west-2"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

# ============================================
# S3 Configuration
# ============================================

variable "s3_bucket" {
  description = "S3 bucket name for parquet data and model storage"
  type        = string
}

# ============================================
# API ECS Configuration
# ============================================

variable "ecs_task_cpu" {
  description = "CPU units for API task"
  type        = number
  default     = 256
}

variable "ecs_task_memory" {
  description = "Memory for API task in MB"
  type        = number
  default     = 512
}

variable "ecs_desired_count" {
  description = "Number of API tasks to run"
  type        = number
  default     = 2
}

variable "ecs_image_tag" {
  description = "Docker image tag to deploy"
  type        = string
  default     = "latest"
}

# ============================================
# Poller Configuration
# ============================================

variable "poller_task_cpu" {
  description = "CPU units for poller task"
  type        = number
  default     = 512
}

variable "poller_task_memory" {
  description = "Memory for poller task in MB"
  type        = number
  default     = 1024
}

# ============================================
# Pipeline Configuration
# ============================================

variable "pipeline_task_cpu" {
  description = "CPU units for pipeline task"
  type        = number
  default     = 1024
}

variable "pipeline_task_memory" {
  description = "Memory for pipeline task in MB"
  type        = number
  default     = 2048
}

# ============================================
# Domain Name
# ============================================


variable "domain_name" {
  description = "Custom domain name"
  type        = string
}