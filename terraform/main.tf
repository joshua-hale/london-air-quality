# ============================================
# ECR Module - Container Registries
# ============================================

module "ecr" {
  source = "./modules/ecr"
  
  project_name = var.project_name
  environment  = var.environment
  
  # Create both API and Poller repositories
  create_poller_repository = true
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
  
  # Cost optimization: single node
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
  
  # Network configuration
  vpc_id                = module.networking.vpc_id
  subnet_ids            = module.networking.public_subnet_ids
  ecs_security_group_id = module.networking.ecs_security_group_id
  
  # ALB integration
  target_group_arn = module.alb.target_group_arn
  
  # Container image (API)
  ecr_repository_url = module.ecr.repository_url
  image_tag          = var.ecs_image_tag
  
  # Redis connection
  redis_host = module.elasticache.redis_endpoint
  redis_port = module.elasticache.redis_port
    
  # Task configuration
  task_cpu       = var.ecs_task_cpu
  task_memory    = var.ecs_task_memory
  desired_count  = var.ecs_desired_count
  container_port = 8000
  
  # Health check
  health_check_path = "/health"
}

# ============================================
# Poller Module - Scheduled Cache Population
# ============================================

module "poller" {
  source = "./modules/poller"
  
  project_name = var.project_name
  environment  = var.environment
  
  # Network configuration
  vpc_id                = module.networking.vpc_id
  subnet_ids            = module.networking.public_subnet_ids
  ecs_security_group_id = module.networking.ecs_security_group_id
  
  # ECS configuration (reuse from API module)
  ecs_cluster_arn    = module.ecs.cluster_arn  # ← Changed to use ARN explicitly
  execution_role_arn = module.ecs.execution_role_arn
  task_role_arn      = module.ecs.task_role_arn
  
  # Poller-specific image
  poller_repository_url = module.ecr.poller_repository_url
  image_tag             = var.ecs_image_tag
  
  # Redis connection
  redis_host = module.elasticache.redis_endpoint
  redis_port = module.elasticache.redis_port
  
  # Application secrets
  openweather_api_key = var.openweather_api_key
  
  # Schedule (runs every hour)
  schedule_expression = "rate(1 hour)"
  
  # Task resources
  task_cpu    = var.poller_task_cpu    
  task_memory = var.poller_task_memory

}
