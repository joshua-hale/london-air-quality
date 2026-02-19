terraform {
  backend "s3" {
    bucket         = "london-air-quality-terraform-state"
    key            = "london-air-quality/terraform.tfstate"
    region         = "eu-west-2"
    encrypt        = true
    }
}