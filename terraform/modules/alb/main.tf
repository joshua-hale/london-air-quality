# ============================================
# Application Load Balancer
# ============================================

resource "aws_lb" "main" {
  name               = "${var.project_name}-${var.environment}-alb"
  internal           = false  # Internet-facing
  load_balancer_type = "application"
  security_groups    = [var.security_group_id]
  subnets            = var.subnet_ids

  enable_deletion_protection = var.enable_deletion_protection
  idle_timeout              = var.idle_timeout

  # Enable access logs (optional, add if neccesary)
  # access_logs {
  #   bucket  = aws_s3_bucket.alb_logs.id
  #   prefix  = "alb"
  #   enabled = true
  # }

  tags = {
    Name        = "${var.project_name}-${var.environment}-alb"
    Environment = var.environment
  }
}

# ============================================
# Target Group (for ECS tasks)
# ============================================

resource "aws_lb_target_group" "main" {
  name        = "${var.project_name}-${var.environment}-tg"
  port        = var.target_port
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"  # Required for Fargate

  # Health check configuration
  health_check {
    enabled             = true
    path                = var.health_check_path
    port                = "traffic-port"
    protocol            = "HTTP"
    interval            = var.health_check_interval
    timeout             = var.health_check_timeout
    healthy_threshold   = var.health_check_healthy_threshold
    unhealthy_threshold = var.health_check_unhealthy_threshold
    matcher             = var.health_check_matcher
  }

  # Deregistration delay (connection draining)
  deregistration_delay = var.deregistration_delay

  # Stickiness (optional - usually not needed for stateless APIs)
  stickiness {
    type    = "lb_cookie"
    enabled = false
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-tg"
    Environment = var.environment
  }

  # Ensure target group is created before ALB listener
  lifecycle {
    create_before_destroy = true
  }
}

# ============================================
# Listener - HTTP (port 80)
# ============================================

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  # Default action: forward to target group
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.main.arn
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-listener-http"
    Environment = var.environment
  }
}

# ============================================
# Listener - HTTPS (port 443) - Optional later addition
# Uncomment when I have SSL certificate
# ============================================

# resource "aws_lb_listener" "https" {
#   load_balancer_arn = aws_lb.main.arn
#   port              = 443
#   protocol          = "HTTPS"
#   ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
#   certificate_arn   = var.ssl_certificate_arn
#
#   default_action {
#     type             = "forward"
#     target_group_arn = aws_lb_target_group.main.arn
#   }
# }
#
# # Redirect HTTP to HTTPS
# resource "aws_lb_listener_rule" "redirect_http_to_https" {
#   listener_arn = aws_lb_listener.http.arn
#   priority     = 1
#
#   action {
#     type = "redirect"
#     redirect {
#       port        = "443"
#       protocol    = "HTTPS"
#       status_code = "HTTP_301"
#     }
#   }
#
#   condition {
#     path_pattern {
#       values = ["/*"]
#     }
#   }
# }