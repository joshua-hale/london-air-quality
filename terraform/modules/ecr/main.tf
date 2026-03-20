resource "aws_ecr_repository" "main" {
  name                 = "${var.project_name}-${var.environment}"
  image_tag_mutability = var.image_tag_mutability

  # Enable vulnerability scanning
  image_scanning_configuration {
    scan_on_push = var.scan_on_push
  }

  # Encryption at rest
  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}"
    Environment = var.environment
  }
}

# Lifecycle policy - keep only last N images
resource "aws_ecr_lifecycle_policy" "main" {
  repository = aws_ecr_repository.main.name

  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep last ${var.max_image_count} images"
      selection = {
        tagStatus     = "any"
        countType     = "imageCountMoreThan"
        countNumber   = var.max_image_count
      }
      action = {
        type = "expire"
      }
    }]
  })
}

# Poller Repository
resource "aws_ecr_repository" "poller" {
  count = var.create_poller_repository ? 1 : 0

  name                 = "${var.project_name}-${var.environment}-poller"
  image_tag_mutability = var.image_tag_mutability

  image_scanning_configuration {
    scan_on_push = var.scan_on_push
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-poller"
    Environment = var.environment
  }
}

resource "aws_ecr_lifecycle_policy" "poller" {
  count = var.create_poller_repository ? 1 : 0

  repository = aws_ecr_repository.poller[0].name
  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep last ${var.max_image_count} images"
      selection = {
        tagStatus     = "any"
        countType     = "imageCountMoreThan"
        countNumber   = var.max_image_count
      }
      action = {
        type = "expire"
      }
    }]
  })
}

# Pipeline repository
resource "aws_ecr_repository" "pipeline" {
  count = var.create_pipeline_repository ? 1 : 0

  name                 = "${var.project_name}-${var.environment}-pipeline"
  image_tag_mutability = var.image_tag_mutability

  image_scanning_configuration {
    scan_on_push = var.scan_on_push
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-pipeline"
    Environment = var.environment
  }
}

resource "aws_ecr_lifecycle_policy" "pipeline" {
  count = var.create_pipeline_repository ? 1 : 0

  repository = aws_ecr_repository.pipeline[0].name
  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep last ${var.max_image_count} images"
      selection = {
        tagStatus     = "any"
        countType     = "imageCountMoreThan"
        countNumber   = var.max_image_count
      }
      action = {
        type = "expire"
      }
    }]
  })
}
