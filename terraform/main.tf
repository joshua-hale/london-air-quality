# ============================================
# ECR Module - Container Registries
# ============================================

module "ecr" {
  source = "./modules/ecr"

  project_name = var.project_name
  environment  = var.environment

  create_poller_repository   = true
  create_pipeline_repository = true
}

# ============================================
# Networking Module - VPC, Subnets, Security Groups
# ============================================

module "networking" {
  source = "./modules/networking"

  project_name = var.project_name
  environment  = var.environment
  vpc_cidr     = var.vpc_cidr
}

# ============================================
# ElastiCache Module - Redis Cache
# ============================================

module "elasticache" {
  source = "./modules/elasticache"

  project_name      = var.project_name
  environment       = var.environment
  vpc_id            = module.networking.vpc_id
  subnet_ids        = module.networking.private_subnet_ids
  security_group_id = module.networking.redis_security_group_id

  node_type       = "cache.t3.micro"
  num_cache_nodes = 1
}

# ============================================
# ALB Module - Application Load Balancer
# ============================================

module "alb" {
  source = "./modules/alb"

  project_name      = var.project_name
  environment       = var.environment
  vpc_id            = module.networking.vpc_id
  subnet_ids        = module.networking.public_subnet_ids
  security_group_id = module.networking.alb_security_group_id
}

# ============================================
# ECS Module - Container Orchestration (API)
# ============================================

module "ecs" {
  source = "./modules/ecs"

  project_name = var.project_name
  environment  = var.environment

  vpc_id                = module.networking.vpc_id
  subnet_ids            = module.networking.public_subnet_ids
  ecs_security_group_id = module.networking.ecs_security_group_id

  target_group_arn = module.alb.target_group_arn

  ecr_repository_url = module.ecr.repository_url
  image_tag          = var.ecs_image_tag

  redis_host = module.elasticache.redis_endpoint
  redis_port = module.elasticache.redis_port

  task_cpu       = var.ecs_task_cpu
  task_memory    = var.ecs_task_memory
  desired_count  = var.ecs_desired_count
  container_port = 8000

  s3_bucket = var.s3_bucket

  health_check_path = "/health"
}

# ============================================
# Poller Module - Scheduled Data Ingestion
# ============================================

module "poller" {
  source = "./modules/poller"

  project_name = var.project_name
  environment  = var.environment

  vpc_id                = module.networking.vpc_id
  subnet_ids            = module.networking.public_subnet_ids
  ecs_security_group_id = module.networking.ecs_security_group_id

  ecs_cluster_arn    = module.ecs.cluster_arn
  execution_role_arn = module.ecs.execution_role_arn
  task_role_arn      = module.ecs.task_role_arn

  poller_repository_url = module.ecr.poller_repository_url
  image_tag             = var.ecs_image_tag

  redis_host = module.elasticache.redis_endpoint
  redis_port = module.elasticache.redis_port

  s3_bucket = var.s3_bucket

  schedule_expression = "rate(1 hour)"

  task_cpu    = var.poller_task_cpu
  task_memory = var.poller_task_memory
}

# ============================================
# Pipeline Module - Scheduled ML Inference
# ============================================

module "pipeline" {
  source = "./modules/pipeline"

  project_name = var.project_name
  environment  = var.environment

  vpc_id                = module.networking.vpc_id
  subnet_ids            = module.networking.public_subnet_ids
  ecs_security_group_id = module.networking.ecs_security_group_id

  ecs_cluster_arn    = module.ecs.cluster_arn
  execution_role_arn = module.ecs.execution_role_arn
  task_role_arn      = module.ecs.task_role_arn

  pipeline_repository_url = module.ecr.pipeline_repository_url
  image_tag               = var.ecs_image_tag

  redis_host = module.elasticache.redis_endpoint
  redis_port = module.elasticache.redis_port

  s3_bucket = var.s3_bucket

  schedule_expression = "rate(1 hour)"

  task_cpu    = var.pipeline_task_cpu
  task_memory = var.pipeline_task_memory
}

# ============================================
# S3 Module - Data Lake and Model Storage
# ============================================

module "s3" {
  source = "./modules/s3"

  s3_bucket   = var.s3_bucket
  environment = var.environment
}

# ============================================
# Frontend Module - S3
# ============================================

module "frontend" {
  source = "./modules/frontend"

  project_name = var.project_name
  environment  = var.environment
}
