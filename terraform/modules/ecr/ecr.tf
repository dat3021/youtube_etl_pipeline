resource "aws_ecr_repository" "youtube-pipeline" {
  name = var.ecr_repo_name
}