variable "youtube_pipeline_cluster" {
  description = "Name for the ECS cluster"
  type        = string
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
}

variable "youtube_pipeline_task_family" {
  description = "Family name for the ECS task definition"
  type        = string
}

variable "youtube_pipeline_task_name" {
  description = "Name for the container in the task definition"
  type        = string
}

variable "ecr_repo_url" {
  description = "The ECR repository URL"
  type        = string
}

variable "ecs_task_execution_role_name" {
  description = "Name for the ECS task execution role"
  type        = string
}
