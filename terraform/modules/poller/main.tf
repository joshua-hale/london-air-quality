# ============================================
# CloudWatch Log Group for Poller
# ============================================

resource "aws_cloudwatch_log_group" "poller" {
  name              = "/ecs/${var.project_name}-${var.environment}-poller"
  retention_in_days = 7

  tags = {
    Name        = "${var.project_name}-${var.environment}-poller-logs"
    Environment = var.environment
  }
}

# ============================================
# ECS Task Definition for Poller
# ============================================

resource "aws_ecs_task_definition" "poller" {
  family                   = "${var.project_name}-${var.environment}-poller"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.task_cpu
  memory                   = var.task_memory
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = var.task_role_arn

  container_definitions = jsonencode([
    {
      name      = "poller"
      image     = "${var.poller_repository_url}:${var.image_tag}"
      essential = true

      command = ["python", "main.py"]

      environment = [
        {
          name  = "REDIS_HOST"
          value = var.redis_host
        },
        {
          name  = "REDIS_PORT"
          value = tostring(var.redis_port)
        },
        {
          name  = "OPENWEATHER_API_KEY"
          value = var.openweather_api_key
        },
        {
          name  = "openweather_api_key"
          value = var.openweather_api_key
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.poller.name
          "awslogs-region"        = data.aws_region.current.name
          "awslogs-stream-prefix" = "poller"
        }
      }
    }
  ])

  tags = {
    Name        = "${var.project_name}-${var.environment}-poller-task"
    Environment = var.environment
  }
}

# ============================================
# EventBridge Rule (Hourly Schedule)
# ============================================

resource "aws_cloudwatch_event_rule" "poller_schedule" {
  name                = "${var.project_name}-${var.environment}-poller-schedule"
  description         = "Trigger poller every hour"
  schedule_expression = var.schedule_expression

  tags = {
    Name        = "${var.project_name}-${var.environment}-poller-schedule"
    Environment = var.environment
  }
}

# ============================================
# EventBridge Target (ECS Task)
# ============================================

resource "aws_cloudwatch_event_target" "poller" {
  rule     = aws_cloudwatch_event_rule.poller_schedule.name
  arn      = var.ecs_cluster_arn  # Must be cluster ARN
  role_arn = aws_iam_role.eventbridge_ecs_role.arn

  ecs_target {
    task_count          = 1
    task_definition_arn = aws_ecs_task_definition.poller.arn
    launch_type         = "FARGATE"

    network_configuration {
      subnets          = var.subnet_ids
      security_groups  = [var.ecs_security_group_id]
      assign_public_ip = true
    }
  }
}

# ============================================
# IAM Role for EventBridge to Run ECS Tasks
# ============================================

resource "aws_iam_role" "eventbridge_ecs_role" {
  name = "${var.project_name}-${var.environment}-eventbridge-ecs-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-${var.environment}-eventbridge-ecs-role"
    Environment = var.environment
  }
}

resource "aws_iam_role_policy" "eventbridge_ecs_policy" {
  name = "${var.project_name}-${var.environment}-eventbridge-ecs-policy"
  role = aws_iam_role.eventbridge_ecs_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # Allow RunTask + TagResource scoped to specific cluster
      {
        Effect = "Allow"
        Action = [
          "ecs:RunTask",
          "ecs:TagResource"
        ]
        Resource = "*"
        Condition = {
          ArnEquals = {
            "ecs:cluster" = var.ecs_cluster_arn
          }
        }
      },
      # Allow passing IAM roles to ECS tasks
      {
        Effect = "Allow"
        Action = [
          "iam:PassRole"
        ]
        Resource = [
          var.execution_role_arn,
          var.task_role_arn
        ]
        Condition = {
          StringLike = {
            "iam:PassedToService" = "ecs-tasks.amazonaws.com"
          }
        }
      }
    ]
  })
}

# ============================================
# Data Sources
# ============================================

data "aws_region" "current" {}