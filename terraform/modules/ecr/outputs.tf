output "repository_url" {
  description = "URL of the API ECR repository"
  value       = aws_ecr_repository.main.repository_url
}

output "repository_arn" {
  description = "ARN of the API ECR repository"
  value       = aws_ecr_repository.main.arn
}

output "repository_name" {
  description = "Name of the API ECR repository"
  value       = aws_ecr_repository.main.name
}

# Poller Repository Outputs 
output "poller_repository_url" {
  description = "URL of the Poller ECR repository"
  value       = var.create_poller_repository ? aws_ecr_repository.poller[0].repository_url : null
}

output "poller_repository_arn" {
  description = "ARN of the Poller ECR repository"
  value       = var.create_poller_repository ? aws_ecr_repository.poller[0].arn : null
}

output "poller_repository_name" {
  description = "Name of the Poller ECR repository"
  value       = var.create_poller_repository ? aws_ecr_repository.poller[0].name : null
}

output "pipeline_repository_url" {
  description = "URL of the Pipeline ECR repository"
  value       = var.create_pipeline_repository ? aws_ecr_repository.pipeline[0].repository_url : null
}

output "pipeline_repository_arn" {
  description = "ARN of the Pipeline ECR repository"
  value       = var.create_pipeline_repository ? aws_ecr_repository.pipeline[0].arn : null
}

output "pipeline_repository_name" {
  description = "Name of the Pipeline ECR repository"
  value       = var.create_pipeline_repository ? aws_ecr_repository.pipeline[0].name : null
}