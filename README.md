# YouTube - ELT Pipeline

An automated ETL pipeline designed to extract data from YouTube Data API (playlists and PlaylistItems), store in an AWS S3 landing zone, and transform them into **Apache Iceberg** tables using Duckdb and Pyiceberg.

---

##  Project Overview

The goal of this project is to perform data analytics and backup on Youtube data using various tools and technologies, automates API ingestion into Amazon S3 using Apache Iceberg and AWS Glue for ACID transactions and schema evolution. Orchestrated via Apache Airflow (Docker/ECS) and provisioned with Terraform, the pipeline leverages DuckDB and PyIceberg, powering Streamlit dashboard for data exploration.

---

## Tools & Tech Stack

### Core Technologies
- **Orchestration:** [Apache Airflow](https://airflow.apache.org/) (managed via Docker/ECS).
- **Extraction:** Python + [Google API Client](https://github.com/googleapis/google-api-python-client).
- **Data Lake Format:** [Apache Iceberg](https://iceberg.apache.org/).
- **Transformation Engine:** [DuckDB](https://duckdb.org/) & [PyIceberg](https://py.iceberg.apache.org/).
- **Catalog:** AWS Glue Data Catalog.
- **Storage:** Amazon S3.
- **Infrastructure:** [Terraform](https://www.terraform.io/).
- **Visualization:** [Streamlit](https://streamlit.io/).

### Prerequisites
- **Python 3.12+** (Managed via [`uv`](https://github.com/astral-sh/uv)).
- **Docker & Docker Compose** (for local orchestration).
- **Terraform** (for cloud deployment).
- **AWS CLI** configured with appropriate permissions.
- **YouTube Data API v3 Key**.

---

## Project Architecture

### Local Workflow
1.  **Extract:** Python scripts fetch paginated metadata  from the YouTube API.
2.  **Load (Raw):** Data is saved as raw JSON files in an S3 landing zone
3.  **Transform:**
    - **DuckDB** reads raw JSON and converts it into Arrow tables (schema-on-read).
    - **PyIceberg** writes the Arrow data into Iceberg Parquet files.
4.  **Register:** Metadata is registered in the **AWS Glue Data Catalog**.
5.  **Visualize:** **Streamlit** queries the Iceberg tables directly from S3.

### Visual Architecture


<img width="1979" height="738" alt="local" src="https://github.com/user-attachments/assets/ca50969c-5e1c-424d-9476-28ca5c88e2ac" />


### Cloud Runtime Workflow (Serverless Automation)
1. Trigger: AWS EventBridge initiates based on a predefined Cron schedule

2. Launch: AWS ECS Fargate pulls the latest containerized image from  ECR to execute the ELT tasks in a serverless environment.

3. Processing: The containerized task handles YouTube API authentication and pagination, load and transform raw data.

4. Cataloging: Metadata y managed via the AWS Glue Data Catalog

### Visual Architecture
<img width="800" height="600" alt="cloud" src="https://github.com/user-attachments/assets/afcd3f91-bee6-486d-94f3-8ced16843f8f" />

### Visualize On Dashboard

## Project Structure

```text
.
├── common/             # Shared utilities (service wrappers)
├── dags/               # Airflow DAG definitions (youtube_pipeline.py)
├── extract/            # Scripts for fetching data from YouTube API
├── transform/          # DuckDB transformation logic and Iceberg writers
├── terraform/          # IaC modules (ECR, ECS, TF State, S3/DynamoDB)
│   └── modules/        # Reusable modules for ECR, ECS, and State management
├── streamlit-dashboard/# Visualization app (dashboard.py)
├── docker-compose.yaml # Local Airflow setup (Postgres, Redis, Celery)
├── dockerfile          # Custom Airflow image with 'uv' and project deps
└── pyproject.toml      # Project dependencies and metadata
```

---

##  Platforms & Deployment

The project is designed to run in two environments:

### 1. Local Development (Docker)
Ideal for testing DAGs and extraction logic locally.
- **Setup:**
  ```bash
  uv sync                        

  cat <<EOF > .env
    YOUTUBE_TOKEN=your_token
    YOUTUBE_CLIENT_SECRET=your_secret
    MY_AWS_REGION=us-east-1
    MY_AWS_ACCESS_KEY_ID=your_access_key
    MY_AWS_SECRET_ACCESS_KEY=your_secret_key
    EOF

  docker-compose up -d            
  ```
- **Access:** Airflow UI at `http://localhost:8080` (Default: `admin/admin`).

### 2. Cloud Production (AWS)
Managed via Terraform for a scalable, production-grade environment.
- **Infrastructure:**
    - **ECS (Fargate):** Runs Airflow tasks as containers.
    - **ECR:** Hosts the custom Airflow Docker image.
    - **S3:** Primary data lake storage and Terraform state backend.
    - **Glue:** Manages the Iceberg table catalog.
- **Deployment:**
  ```bash
  cd terraform
  terraform init
  terraform apply
  ```
 **Note:** 
- Build the Docker image and push it to the ECR repository.
- Manage credentials using AWS Secrets Manager.

---

##  Other Requirements

### AWS Permissions
Your IAM User/Role requires permissions for:
- `s3:*` (Data Lake and TF State).
- `glue:*` (Catalog Management).
- `ecs:*` & `ecr:*` (Container Orchestration).
- `dynamodb:*` (TF State Locking).


### Project Maintenance
- **Clean Up:** Run `terraform destroy` to tear down all cloud resources.
- **Updates:** Use `uv lock` to update dependencies and rebuild the Docker image.
