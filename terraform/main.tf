terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.92"
    }
  }

  backend "s3" {
    bucket         = "terraform-387"
    key            = "tf-infra/terraform.tfstate"
    region         = "ap-southeast-2"
    dynamodb_table = "tf-state"
    encrypt        = true
  }

  required_version = ">= 1.4"
}


module "tf-state" {
  source      = "./modules/tf-state"
  bucket_name = local.bucket_name
  table_name  = local.table_name
}

module "ecr" {
  source        = "./modules/ecr"
  ecr_repo_name = local.ecr_repo_name
}

module "ecs" {
  source                       = "./modules/ecs"
  youtube_pipeline_cluster     = local.youtube_pipeline_cluster
  youtube_pipeline_task_family = local.youtube_pipeline_task_family
  youtube_pipeline_task_name   = local.youtube_pipeline_task_name
  ecr_repo_url                 = module.ecr.repository_url
  ecs_task_execution_role_name = local.ecs_task_execution_role_name
  availability_zones           = local.availability_zones
}