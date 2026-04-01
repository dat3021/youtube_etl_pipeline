resource "aws_ecs_cluster" "youtube_pipeline_cluster" {
  name = var.youtube_pipeline_cluster
}

resource "aws_default_vpc" "default_vpc" {}

resource "aws_default_subnet" "default_subnet" {
  availability_zone = var.availability_zones[0]
}

resource "aws_ecs_task_definition" "youtube_pipeline_task" {
  family                   = var.youtube_pipeline_task_family
  task_role_arn            = data.aws_iam_role.iam_task_role.arn
  container_definitions    = <<DEFINITION
  [
    {
      "name": "${var.youtube_pipeline_task_name}",
      "image": "${var.ecr_repo_url}",
      "essential": true,
      "command": ["bash", "-c"," airflow db migrate && airflow dags test youtube_pipeline"],
      "secrets": [
        {
          "name": "YOUTUBE_TOKEN",
          "valueFrom": "arn:aws:ssm:ap-southeast-2:072456928762:parameter/youtube-pipeline/youtube_token"
        },
        {
          "name": "YOUTUBE_CLIENT_SECRET",
          "valueFrom": "arn:aws:ssm:ap-southeast-2:072456928762:parameter/youtube-pipeline/youtube_client_secret"
        },
        {
          "name": "MY_AWS_REGION",
          "valueFrom": "arn:aws:ssm:ap-southeast-2:072456928762:parameter/youtube-pipeline/aws_region"
        },
        {
          "name": "MY_AWS_ACCESS_KEY_ID",
          "valueFrom": "arn:aws:ssm:ap-southeast-2:072456928762:parameter/youtube-pipeline/access_key"
        },
        {
          "name": "MY_AWS_SECRET_ACCESS_KEY",
          "valueFrom": "arn:aws:ssm:ap-southeast-2:072456928762:parameter/youtube-pipeline/aws_secret_access_key"
        }
      ],
      "environment": [
        { "name": "PYTHONPATH", "value": "/opt/airflow" },
        { "name": "S3_BUCKET_NAME", "value": "terraform-387" }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/youtube-pipeline",
          "awslogs-region": "ap-southeast-2",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "memory": 2048,
      "cpu": 1024
    }
  ]
DEFINITION
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  memory                   = 2048
  cpu                      = 1024
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
}

resource "aws_iam_role" "ecs_task_execution_role" {
  name               = var.ecs_task_execution_role_name
  assume_role_policy = data.aws_iam_policy_document.assume_role_policy.json
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy" "ecs_execution_ssm_policy" {
  name = "ecs-execution-ssm-policy"
  role = aws_iam_role.ecs_task_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = [
          "ssm:GetParameters",
          "secretsmanager:GetSecretValue",
          "kms:Decrypt"
        ]
        Resource = [
          "arn:aws:ssm:ap-southeast-2:072456928762:parameter/youtube-pipeline/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy" "ecs_task_s3_policy" {
  name = "youtube-pipeline-s3-access"
  role = data.aws_iam_role.iam_task_role.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket",
          "s3:GetBucketLocation"
        ]
        Resource = ["arn:aws:s3:::project-zone"]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject"
        ]
        Resource = ["arn:aws:s3:::project-zone/*"]
      }
    ]
  })
}

resource "aws_iam_role_policy" "ecs_task_glue_policy" {
  name = "youtube-pipeline-glue-access"
  role = data.aws_iam_role.iam_task_role.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
                  "glue:GetDatabase",
                  "glue:GetDatabases",    
                  "glue:GetTable",
                  "glue:GetTables",        
                  "glue:CreateTable",
                  "glue:UpdateTable",
                  "glue:DeleteTable",      
                  "glue:CreateDatabase",
                  "glue:GetUserDefinedFunctions" 
                ]
        Resource = ["*"]
      }
    ]
  })
}

resource "aws_security_group" "service_security_group" {
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_cloudwatch_log_group" "youtube_pipeline_logs" {
  name              = "/ecs/youtube-pipeline"
  retention_in_days = 7
}

#eventbridge rule to trigger ecs task every week
resource "aws_iam_role" "eventbridge_invocation_role" {
  name               = "eventbridge-ecs-invocation-role"
  assume_role_policy = data.aws_iam_policy_document.eventbridge_assume_role.json
}

resource "aws_cloudwatch_event_rule" "youtube_etl_schedule" {
  name                = "youtube-etl-weekly-schedule"
  description         = "run youtube etl task every week"
  schedule_expression = "cron(0 6 ? * SAT *)" 
}

resource "aws_cloudwatch_event_target" "ecs_scheduled_task" {
  rule      = aws_cloudwatch_event_rule.youtube_etl_schedule.name
  arn       = aws_ecs_cluster.youtube_pipeline_cluster.arn
  role_arn  = aws_iam_role.eventbridge_invocation_role.arn

  ecs_target {
    task_count          = 1
    task_definition_arn = aws_ecs_task_definition.youtube_pipeline_task.arn
    launch_type         = "FARGATE"
    
    network_configuration {
      subnets          = [aws_default_subnet.default_subnet.id]
      security_groups  = [aws_security_group.service_security_group.id]
      assign_public_ip = true 
    }
  }
}

resource "aws_iam_role_policy" "eventbridge_ecs_policy" {
  name = "eventbridge-ecs-run-task-policy"
  role = aws_iam_role.eventbridge_invocation_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "ecs:RunTask"
        Resource = [aws_ecs_task_definition.youtube_pipeline_task.arn]
      },
      {
        Effect   = "Allow"
        Action   = "iam:PassRole"
        Resource = [
          aws_iam_role.ecs_task_execution_role.arn,
          data.aws_iam_role.iam_task_role.arn
        ]
      }
    ]
  })
}