output "task_definition_arn" {
  description = "Poller task definition ARN"
  value       = aws_ecs_task_definition.poller.arn
}

output "task_definition_family" {
  description = "Poller task definition family"
  value       = aws_ecs_task_definition.poller.family
}

output "schedule_rule_name" {
  description = "EventBridge schedule rule name"
  value       = aws_cloudwatch_event_rule.poller_schedule.name
}

output "schedule_rule_arn" {
  description = "EventBridge schedule rule ARN"
  value       = aws_cloudwatch_event_rule.poller_schedule.arn
}

output "log_group_name" {
  description = "CloudWatch log group name"
  value       = aws_cloudwatch_log_group.poller.name
}

output "log_group_arn" {
  description = "CloudWatch log group ARN"
  value       = aws_cloudwatch_log_group.poller.arn
}