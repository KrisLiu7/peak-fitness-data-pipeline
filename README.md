# Peak Fitness Data Platform (AWS Serverless)

This project builds a scalable, secure, and cost-efficient data pipeline for Peak Fitness using AWS Glue, Lambda, S3, and Athena. It enables downstream products like a leaderboard dashboard and future CRM integrations.


## Key Features  
- 🚀 Serverless ETL Pipeline using AWS Glue and Lambda  
- 📊 Serverless SQL Queries via Athena
- AStreamlit BI dashboard with user churn, engagement, and popularity metrics
- Optional post-MVP tools: Databricks (notebooks), Redis (cache), Kinesis (streaming)

## Folders

- `streamlit_dashboard/`: Streamlit app for leaderboard analytics
- `glue_jobs/`: All AWS Glue ETL scripts
- `lambda_functions/`: Lambda for partition syncing
- `local_etl/`: Optional local ETL method with Python + Boto3
- `notebooks/`: Databricks Spark notebooks for validation, modeling
- `docs/`: TDD and supplementary files

## Setup

Install Python packages:

```bash
pip install -r requirements.txt
