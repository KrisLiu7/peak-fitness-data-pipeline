# PEAK FITNESS - TECHNICAL DESIGN DOCUMENT

## 1. Scope
**In Scope:**

- End-to-end Data Pipeline: Design and implement a cloud-based data pipeline using Lambda, Glue, and Athena for class signups, transactions, and engagement data.
- Streamlit Dashboard: Build a leaderboard and interactive dashboard for customer engagement and retention metrics.
- HubSpot CRM Sync: Implement integration for churn and retention tracking by syncing data to HubSpot CRM.
- Marketing Email Campaigns: Implement member retention and lifecycle email campaigns.
- Free Tier Cost Optimization: Minimize AWS costs by utilizing free-tier resources where possible.
- ETL Development: Convert raw CSV/JSON files into Parquet format for efficient analytics.
- Database Creation (Athena): Set up Athena for querying and analytics on the transformed data.
- Education Flexibility: Provide ETL templates and a sandbox Athena database for future student/user empowerment.
- CAP Theorem Balancing: Ensure data availability and consistency while managing partition tolerance for the system.
- Machine Learning: Integrate SageMaker Autopilot for predictive analytics (e.g., churn prediction) after MVP.

## 2. Technical Architecture Diagram
The following diagram and steps explain the data flow from raw ingestion to actionable insights:


flowchart TD
    A[CSV/JSON Files] -->|Lambda| B[S3 Raw Zone]
    B --> C{Glue ETL Job}
    C -->|Valid| D[S3 Processed Zone\nParquet]
    C -->|Invalid| E[S3 Quarantine]
    D --> F[Athena Catalog]
    F --> G[Streamlit Dashboard]
    F --> H[HubSpot CRM Sync]
    F --> I[Leaderboard Redis]
    G --> J[Member Retention Emails]
    H --> K[Location-Based Campaigns]
    


**Data Flow:**

1. Ingest: Lambda converts CSV/JSON files into Parquet format for efficient storage.
2. Process: Glue Spark jobs clean and partition the data for analysis.
3. Serve: Athena queries power the Streamlit dashboard and HubSpot CRM integration.
4. Act: Emails are triggered via SES to engage users based on marketing campaigns.

## 3. Proposed Tech Stack
| Tool           | Use Case           | Reason                                            |
| -------------- | ------------------ | ------------------------------------------------- |
| **AWS Lambda** | ETL, CRM Sync      | Free Tier, event-driven, cost-efficient           |
| **Glue Spark** | Parquet Conversion | OLAP-ready, scalable, managed service             |
| **Athena**     | Analytics          | Pay-per-query, serverless, no infrastructure need |
| **Streamlit**  | Dashboard          | Python-native, embeddable, fast prototyping       |

## 4. Design Decisions & Tradeoffs
| Decision                 | Pros                           | Cons                                |
| ------------------------ | ------------------------------ | ----------------------------------- |
| **Lambda over Kinesis**  | No cost at low volume          | No real-time streaming capabilities |
| **Athena over Redshift** | No cluster management required | Slower for complex joins            |
| **Glue over EMR**        | Fully managed service          | Limited customization               |

## 5. Data Management
**Data Integration Pattern:**
- Type: Batch (daily)
- Direction: Outbound (Athena → HubSpot CRM)
- Tech: Lambda to pull data from Athena and push to HubSpot API.

**Data Processing Pattern:**
- Data is loaded into Athena for analytics queries and S3 for storage.
- Athena serves as the data warehouse for querying and reporting.

**Data Layers & Storage:**
- Raw Layer: Stored in CSV/JSON format in S3 for audit trail and ingestion (Retention: 30 days).
- Processed Layer: Transformed data in Parquet format for analytics (Retention: 1 year).
- Aggregated Layer: Redis for leaderboard caching (Retention: 7 days).

**Data Model:**
- Fact Table: FACT_ATTENDANCE (user_id, class_id, dt)
- Dimension Tables:
  - DIM_USERS (user_id, location, join_date)
  - DIM_CLASSES (class_id, instructor, time)

## 6. CAP Theorem Balancing
| Requirement             | Implementation     | Trade-off                           |
| ----------------------- | ------------------ | ----------------------------------- |
| **Consistency**         | Glue Job bookmarks | 24h latency in analytics            |
| **Availability**        | S3 + Athena        | Eventual consistency in queries     |
| **Partition Tolerance** | Multi-AZ S3        | Higher storage costs for redundancy |

**Event vs Historical Data Flow:**
```python
if is_real_time(event):
    firehose.put_record(DeliveryStreamName='real-time-events')
else:
    glue.start_job_run(JobName='batch-processing')
```
## 7. Education & Flexibility
**Student/User Empowerment:**
- Provide a sandbox environment in Athena for learning and experimentation:
- aws athena create-work-group --name student_sandbox

### Storage Layers

| Layer     | Format    | Purpose      | Retention  |
|-----------|-----------|--------------|------------|
| Raw       | CSV/JSON  | Audit trail  | 30 days    |
| Processed | Parquet   | Analytics    | 1 year     |
| Aggregated| Redis     | Leaderboard  | 7 days     |

## 8. Practicalities
**Cost Estimates:**
- S3 Storage: ~0.03 USD/GB per month for raw/processed data.
- Athena Queries: 5 USD per TB scanned for queries.
- Lambda Costs: Based on execution time, with the free tier covering low-volume processing.
**Work Estimation:**
- Implementation Time: Approximately 3-4 weeks for initial pipeline setup and integration.
- Testing/Optimization: 1-2 weeks for final optimization and cost checks.
 
## 9. Privacy and Security
- Sensitive Data: No sensitive personal or financial data is handled by the pipeline.
- Security Approval: New technologies (Glue, Athena, Lambda) introduced; review with the security team is recommended if required.

### 10. Future Enhancements
- Real-time Data: Integration of AWS Kinesis for real-time data streaming, if needed.
- Machine Learning: Post-MVP integration with SageMaker Autopilot for predictive analytics.
  
### Author: Kris Liu
**Email:** kris.shuyi.l@gmail.com
