# ============================================
# CloudWatch Log Group for Pipeline
# ============================================

resource "aws_cloudwatch_log_group" "pipeline" {
  name              = "/ecs/${var.project_name}-${var.environment}-pipeline"
  retention_in_days = 7

  tags = {
    Name        = "${var.project_name}-${var.environment}-pipeline-logs"
    Environment = var.environment
  }
}

# ============================================
# ECS Task Definition for Pipeline
# ============================================

resource "aws_ecs_task_definition" "pipeline" {
  family                   = "${var.project_name}-${var.environment}-pipeline"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.task_cpu
  memory                   = var.task_memory
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = var.task_role_arn

  container_definitions = jsonencode([
    {
      name      = "pipeline"
      image     = "${var.pipeline_repository_url}:${var.image_tag}"
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
          name  = "S3_BUCKET"
          value = var.s3_bucket
        },
        {
          name  = "LOG_LEVEL"
          value = "INFO"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.pipeline.name
          "awslogs-region"        = data.aws_region.current.name
          "awslogs-stream-prefix" = "pipeline"
        }
      }
    }
  ])

  tags = {
    Name        = "${var.project_name}-${var.environment}-pipeline-task"
    Environment = var.environment
  }
}

# ============================================
# EventBridge Rule (Hourly Schedule)
# ============================================

resource "aws_cloudwatch_event_rule" "pipeline_schedule" {
  name                = "${var.project_name}-${var.environment}-pipeline-schedule"
  description         = "Trigger ML pipeline every hour"
  schedule_expression = var.schedule_expression

  tags = {
    Name        = "${var.project_name}-${var.environment}-pipeline-schedule"
    Environment = var.environment
  }
}

# ============================================
# EventBridge Target (ECS Task)
# ============================================

resource "aws_cloudwatch_event_target" "pipeline" {
  rule     = aws_cloudwatch_event_rule.pipeline_schedule.name
  arn      = var.ecs_cluster_arn
  role_arn = aws_iam_role.eventbridge_ecs_role.arn

  ecs_target {
    task_count          = 1
    task_definition_arn = aws_ecs_task_definition.pipeline.arn
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
  name = "${var.project_name}-${var.environment}-pipeline-eventbridge-role"

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
    Name        = "${var.project_name}-${var.environment}-pipeline-eventbridge-role"
    Environment = var.environment
  }
}

resource "aws_iam_role_policy" "eventbridge_ecs_policy" {
  name = "${var.project_name}-${var.environment}-pipeline-eventbridge-policy"
  role = aws_iam_role.eventbridge_ecs_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
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

data "aws_region" "current" {}