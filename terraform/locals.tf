locals {
  bucket_name = "terraform-387"
  table_name  = "tf-state"

  ecr_repo_name                = "youtube-pipeline"
  youtube_pipeline_cluster     = "youtube-pipeline-cluster"
  youtube_pipeline_task_family = "youtube-pipeline-task-family"
  youtube_pipeline_task_name   = "youtube-pipeline-task"
  ecs_task_execution_role_name = "youtube-pipeline-ecs-task-execution-role"
  availability_zones           = ["ap-southeast-2a", "ap-southeast-2b"]
}