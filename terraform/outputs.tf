# ============================================
# ECR Outputs
# ============================================

output "ecr_repository_url" {
  description = "ECR repository URL for API images"
  value       = module.ecr.repository_url
}

output "ecr_repository_name" {
  description = "ECR repository name for API"
  value       = module.ecr.repository_name
}

output "ecr_poller_repository_url" {
  description = "ECR repository URL for Poller images"
  value       = module.ecr.poller_repository_url
}

output "ecr_poller_repository_name" {
  description = "ECR repository name for Poller"
  value       = module.ecr.poller_repository_name
}

output "ecr_pipeline_repository_url" {
  description = "ECR repository URL for Pipeline images"
  value       = module.ecr.pipeline_repository_url
}

output "ecr_pipeline_repository_name" {
  description = "ECR repository name for Pipeline"
  value       = module.ecr.pipeline_repository_name
}

# ============================================
# Networking Outputs
# ============================================

output "vpc_id" {
  description = "VPC ID"
  value       = module.networking.vpc_id
}

output "vpc_cidr" {
  description = "VPC CIDR block"
  value       = module.networking.vpc_cidr
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = module.networking.public_subnet_ids
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = module.networking.private_subnet_ids
}

output "alb_security_group_id" {
  description = "ALB security group ID"
  value       = module.networking.alb_security_group_id
}

output "ecs_security_group_id" {
  description = "ECS security group ID"
  value       = module.networking.ecs_security_group_id
}

output "redis_security_group_id" {
  description = "Redis security group ID"
  value       = module.networking.redis_security_group_id
}

# ============================================
# ElastiCache Outputs
# ============================================

output "redis_endpoint" {
  description = "Redis endpoint address"
  value       = module.elasticache.redis_endpoint
}

output "redis_port" {
  description = "Redis port"
  value       = module.elasticache.redis_port
}

output "redis_connection_string" {
  description = "Redis connection string"
  value       = module.elasticache.redis_connection_string
  sensitive   = true
}

output "redis_cluster_id" {
  description = "ElastiCache cluster ID"
  value       = module.elasticache.cluster_id
}

# ============================================
# ALB Outputs
# ============================================

output "alb_dns_name" {
  description = "ALB DNS name"
  value       = module.alb.alb_dns_name
}

output "api_url" {
  description = "API base URL"
  value       = module.alb.api_url
}

output "target_group_arn" {
  description = "Target group ARN"
  value       = module.alb.target_group_arn
}

# ============================================
# ECS Outputs
# ============================================

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = module.ecs.cluster_name
}

output "ecs_cluster_id" {
  description = "ECS cluster ID"
  value       = module.ecs.cluster_id
}

output "ecs_service_name" {
  description = "ECS service name"
  value       = module.ecs.service_name
}

output "ecs_task_definition_family" {
  description = "ECS task definition family"
  value       = module.ecs.task_definition_family
}

output "ecs_log_group_name" {
  description = "CloudWatch log group for ECS"
  value       = module.ecs.log_group_name
}

# ============================================
# Poller Outputs
# ============================================

output "poller_task_definition_arn" {
  description = "Poller task definition ARN"
  value       = module.poller.task_definition_arn
}

output "poller_task_definition_family" {
  description = "Poller task definition family"
  value       = module.poller.task_definition_family
}

output "poller_schedule_rule" {
  description = "Poller EventBridge schedule rule name"
  value       = module.poller.schedule_rule_name
}

output "poller_log_group" {
  description = "Poller CloudWatch log group"
  value       = module.poller.log_group_name
}

# ============================================
# Pipeline Outputs
# ============================================

output "pipeline_task_definition_arn" {
  description = "Pipeline task definition ARN"
  value       = module.pipeline.task_definition_arn
}

output "pipeline_task_definition_family" {
  description = "Pipeline task definition family"
  value       = module.pipeline.task_definition_family
}

output "pipeline_schedule_rule" {
  description = "Pipeline EventBridge schedule rule name"
  value       = module.pipeline.schedule_rule_name
}

output "pipeline_log_group" {
  description = "Pipeline CloudWatch log group"
  value       = module.pipeline.log_group_name
}

# ============================================
# S3 Outputs
# ============================================

output "s3_bucket_name" {
  description = "S3 bucket name"
  value       = module.s3.bucket_name
}

output "s3_bucket_arn" {
  description = "S3 bucket ARN"
  value       = module.s3.bucket_arn
}

# ============================================
# Frontend Outputs
# ============================================

output "frontend_url" {
  description = "Frontend CloudFront URL"
  value       = module.frontend.frontend_url
}

output "frontend_bucket" {
  description = "Frontend S3 bucket name"
  value       = module.frontend.bucket_name
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID"
  value       = module.frontend.cloudfront_distribution_id
}

output "cloudfront_domain_name" {
  description = "CloudFront domain name"
  value       = module.frontend.cloudfront_domain_name
}

# ============================================
# Domain Outputs
# ============================================

output "domain_name" {
  description = "Custom domain name"
  value       = var.domain_name
}