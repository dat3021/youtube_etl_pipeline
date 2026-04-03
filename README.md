# YouTube Data Pipeline & Backup (Iceberg Edition)

## 1. Project Overview
**Project Title:** YouTube Iceberg Data Lake Pipeline  
**Context:** This project is an automated ETL pipeline designed to extract metadata from YouTube playlists and items using the YouTube Data API v3. The data is ingested into an AWS S3 landing zone and transformed into the **Apache Iceberg** table format for high-performance analytics and historical versioning.  
**Motivation:** The goal is to create a robust, "storage-first" data backup solution that leverages modern data lakehouse architecture. By using Iceberg and Glue, we ensure schema evolution, ACID transactions on S3, and the ability to query data using multiple engines (DuckDB, Apache Superset, Streamlit) without data duplication.

## 2. System Architecture
### Visual Workflow
`YouTube API` → `Airflow (ECS)` → `S3 (Raw JSON)` → `DuckDB/PyIceberg` → `S3 (Iceberg Parquet)` → `Glue Catalog` → `Streamlit / Superset`

### Tech Stack
1.  **Orchestration:** Apache Airflow (running in Docker/ECS)
2.  **Extraction:** Python + Google Client Library (YouTube API v3)
3.  **Data Lake Format:** Apache Iceberg (Glue Data Catalog)
4.  **Transformation Engine:** **DuckDB** (for fast JSON-to-Arrow processing)
5.  **Catalog Management:** AWS Glue Data Catalog + **PyIceberg**
6.  **Infrastructure as Code:** Terraform (ECR, ECS, S3/DynamoDB Backend)
7.  **Storage:** Amazon S3
8.  **Visualization:** Streamlit & Apache Superset

## 3. Repository Structure
```text
.
├── common/             # Shared utilities for S3, PyIceberg, and YouTube API
├── dags/               # Airflow DAG definition (youtube_pipeline)
├── extract/            # Scripts for fetching data from YouTube API
├── transform/          # DuckDB transformation logic and PyIceberg writers
├── terraform/          # IaC modules for ECR, ECS, and TF state management
├── store/              # Placeholder for dbt (future)
├── streamlit-dashboard/# Visualization layer
├── docker-compose.yaml # Local Airflow development setup
└── dockerfile          # Airflow image with uv package manager
```

## 4. Data Flow & Transformation
*   **Ingestion:** Python scripts in `extract/` fetch paginated results from the YouTube API. Data is saved as raw JSON in `s3://{bucket}/raw/youtube/{date_str}/`.
*   **Storage & Warehouse:** S3 serves as both the landing zone and the permanent warehouse. The Iceberg format organizes data into metadata and data (Parquet) layers, registered in the Glue Data Catalog.
*   **Transformation:** The `transform/` layer uses **DuckDB** to perform "schema-on-read" for JSON files. It converts the raw JSON into Arrow tables, which are then appended to Iceberg tables via **PyIceberg**. This approach avoids traditional heavy Spark clusters and allows for lightweight, fast transformations.
*   **Orchestration:** Tasks are managed by the `youtube_pipeline` DAG, handling dependencies between extraction and transformation with daily scheduling.

## 5. Final Output & Visualization
*   **Reporting Tools:** 
    *   **Streamlit Dashboard:** A native Python app (`streamlit-dashboard/dashboard.py`) that uses DuckDB to scan Iceberg metadata directly from S3 for real-time insights.
    *   **Apache Superset:** Can connect to the Iceberg tables directly or via querying engines (like Athena or DuckDB) to join Iceberg data with other datasets for comprehensive BI dashboards.
*   **Key Insights:** Monitors total playlist counts, video density per playlist, and channel-level content growth.

## 6. Prerequisites & Environment
*   **Hardware/OS Notes:** Optimized for Linux/macOS. Docker is required for Airflow orchestration.
*   **Python Environment:** Managed via `uv`. Requires Python 3.12+.
*   **AWS Configuration:** Requires an IAM User/Role with permissions for S3, Glue, ECR, and ECS.
*   **YouTube API:** Requires a valid API Key from the Google Cloud Console.

## 7. Implementation Guide
1.  **Repository Setup:**
    ```bash
    git clone <repo-url>
    cd ytb_backup_project
    uv sync  # Install dependencies locally
    ```
2.  **API/Credential Configuration:**
    *   Set `YOUTUBE_API_KEY` in your environment.
    *   Configure AWS credentials (`~/.aws/credentials`).
3.  **Cloud Infrastructure Setup:**
    ```bash
    cd terraform
    terraform init
    terraform apply
    ```
4.  **Containerization:**
    *   Build and push the Docker image to the ECR repository (`youtube-pipeline`) created by Terraform.
5.  **Running the Pipeline:**
    *   **Local Development:** `docker-compose up -d`
    *   **Cloud Deployment:** Trigger the ECS tasks via the Airflow instance running in your cluster.

## 8. Project Maintenance
*   **Termination:** Run `terraform destroy` within the `terraform/` directory to tear down all AWS resources and stop incurring costs.
*   **Future Improvements:** 
    *   Implement **dbt-glue** for more complex transformation modeling.
    *   Add automated Iceberg table maintenance (compaction and snapshot expiration).
    *   Expand extraction to include video comments and engagement metrics.
