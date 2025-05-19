# PEAK FITNESS - TECHNICAL DESIGN DOCUMENT

**Authors:** Kris Liu  
**Stakeholders:** Peak Fitness Marketing & Retention Team, BeFit Inc.  
**Approvals:** Minjia

## Overview

Peak Fitness, a boutique fitness studio recently acquired by BeFit Inc., currently relies on the third-party platform Mindbody to manage class bookings and customer data. However, the business faces growing limitations: customer engagement data is fragmented, analytics are manual and delayed, and marketing teams lack real-time access to actionable insights.

This project proposes a custom, cloud-based data platform that centralizes and transforms Peak’s raw operational data into a scalable analytics infrastructure. By building an end-to-end data pipeline using AWS services—including S3, Glue, Lambda, and Athena—and surfacing insights via a dashboard and leaderboard API, the platform aims to support customer retention, optimize scheduling, and enable data-driven decisions across marketing and operations. The ultimate goal is to modernize the company’s data foundation in a way that is cost-effective, flexible, and secure.

## Glossary of Terms

| Term/Acronym | Definition |
|--------------|------------|
| ETL | Extract, Transform, Load |
| AWS S3 | Amazon Simple Storage Service |
| AWS Glue | Serverless ETL using Spark or Python |
| AWS Lambda | Serverless compute to trigger ETL tasks or APIs |
| Athena | SQL-on-S3 query engine |
| Redis | In-memory store for caching |
| Databricks | ML/analytics notebook platform |
| Streamlit | Interactive dashboard builder |
| PII | Personally Identifiable Information |
| MVP | Minimum Viable Product |

## Current State

- Relies on Mindbody with no central warehouse
- Manual CSV exports used for analysis
- Analytics delayed and not real-time
- No CRM or lifecycle marketing integrations
- Static campaign lists used

## Goals

### Primary Goals
- Migrate to AWS-based data platform
- Build ETL using Python and Boto3
- Create Athena-accessible tables
- Power dashboards and CRM triggers
- Ensure data quality, security, and scalability

### Secondary Goals
- Use Athena for internal exploration
- Minimize cost via Free Tier tools
- Enable predictive modeling in future
- Leverage Databricks for cohort analysis

### Non-functional Requirements
- **Scalability**: Expand without major rework
- **Availability**: Daily updates with minimal failure
- **Security**: IAM roles, encryption, no PII exposure
- **Performance**: Fast dashboard/API responses

### Non-goals
- Replacing booking/scheduling features
- Real-time ingestion (MVP is batch)
- Customer-facing app or frontend
- Full CRM automation
- Advanced ML during MVP

## Impact / Measures of Success

### System Performance & Stability
- 95%+ daily ETL success rate
- Data queryable in Athena within 30 minutes
- 95%+ record validation pass rate
- Schema updates cause < 1 hour downtime
- Partitioning cuts query cost by >50%
- Glue logs include row counts, durations, failures

### Analytics & Campaign Enablement
- 100% of instructor/class/location covered
- Aggregates for top 10 metrics exposed
- Fields added for CRM segmentation (e.g., frequency)
- Campaign-ready cohort logic available
- Retention metrics enabled (e.g., no-show, trends)
- Supports lifecycle queries and CRM campaigns

### Data Integration & Future Use Cases
- Streamlit dashboard <2s response time
- One streaming-ready table included
- Modular Glue/Lambda code for new tables
- CloudWatch triggers on ETL failures
- Key behavior signals exposed (e.g., recency)

## Partitioned Athena Table Design

- Partitioned by `class_date`, `location_id`, or `class_type`
- Reduces full scans
- Improves performance and lowers costs
- Enables fast filtering and segmentation

## ETL Logging with CloudWatch

- ETL job logs retained for 7–14 days
- Metrics: row count, errors, job durations
- Alerts via metric filters on critical failures
- Only critical jobs (e.g., class_attendance repair) logged

## Educational / Student Extensibility

- Modular ETL code with comments
- One full pipeline from raw to Athena (e.g., `dim_users`)
- GitHub includes “How to Extend” guide
- Sample extension table: `class_feedback`
- Sample scripts using Boto3 included
- Local testing support with manual Athena creation
- Reusable Lambda/Glue job templates

## Architecture Overview
![Image](https://github.com/user-attachments/assets/23db60a7-914a-40a7-8f62-7a2ae713a87f)

### Tools Used
- **S3**: Raw/processed layer
- **Glue**: ETL and partitioned Parquet output
- **Lambda**: Orchestration and MSCK REPAIR
- **Athena**: Query layer
- **Streamlit**: Dashboard frontend
- **CloudWatch**: Logging and monitoring
- **Databricks** (Post-MVP): ML pipelines
- **Kinesis** (Post-MVP): Streaming simulation
- **Redis** (Post-MVP): Cache leaderboard results

### Tradeoffs
- Optimized for Availability + Partition tolerance (CAP)
- Eventual consistency acceptable for batch updates
- Validation logic enforces data correctness

### Data Flow
- Upload CSV/JSON to S3
- Glue transforms and partitions into Parquet
- Lambda triggers MSCK REPAIR TABLE
- Athena queries partitioned datasets
- Streamlit dashboard reads from Athena

## Schema Design

### Core Tables
- `dim_users`
- `dim_classes`
- `dim_locations`
- `dim_instructors`
- `class_attendance`

Covers users, classes, locations, instructors, and behavior. Future additions like transactions, feedback, and CRM output will layer on top.

### Sample Schema: `dim_users`
- `user_id` (PK)
- `full_name`
- `email`
- `city`
- `signup_date`
- `birth_year`
- `gender`

### Sample Schema: `dim_classes`
- `class_id` (PK)
- `class_name`
- `class_type`
- `instructor_id` (FK)
- `location_id` (FK)
- `start_time`, `end_time`

### Sample Schema: `class_attendance`
- `attendance_id` (PK)
- `user_id` (FK)
- `class_id` (FK)
- `checkin_time`
- `status`
- `class_date` (partition)

## API Interface

### Leaderboard API (MVP)
- Read-only
- Queries Athena for attendance metrics
- Supports filters (week, location, class type)
- Output: JSON top instructors/classes
- Backend: Streamlit or Flask
- Secured with IAM roles

## Productionization

### Availability Tier
- Tier 2: batch updates via Glue + Lambda
- Athena <2s query response
- Dashboard API <500ms

### Monitoring
- Logs in CloudWatch: execution time, record count
- Metric filters detect anomalies
- Schema checks: type match, required fields, nulls
- Raw vs processed row validation

### Rollout Plan
- Initial: 10% data sample (Jan 2023)
- Glue used for Parquet transformation
- Lambda automates MSCK REPAIR
- Only MVP schema/tables processed initially
- Manual test data deleted post-dev

### Post-MVP Enhancements
- `fact_transactions`, `class_feedback`, CRM logic
- Real-time Kinesis stream
- ML via SageMaker (e.g., churn prediction)
- Redis cache layer
- Databricks Delta Lake integration

### CRM Sync Prep
- `dim_users` has user_id, email, city, created_at
- `class_attendance` summarized per user:
  - last active date
  - favorite class
  - frequency

### Kinesis Mock Stream
- Simulates check-ins with `put_record()`
- Useful for streaming dashboard mockups

### Redis Cache Layer
- Sorted sets to store top classes/users
- API returns fast leaderboard results
- Use case: class attendance tracking

## Accessibility

- No public-facing UI
- Internal-only access via Streamlit IAM auth
- No user interaction; view-only dashboard

## Security & Privacy

- IAM roles scoped per service
- Glue and Lambda use `requester-pays`
- No PII in outputs; only anonymized user_ids
- PII handled only inside Glue
- Logs do not store PII
- No dynamic SQL/user input

## Educational Features

- `local_etl/` folder included
- Boto3-based ETL simulates Glue behavior
- CSV/JSON upload + manual Athena setup for practice

## Rollback Plan

- Process only 10% of data initially
- Versioned S3 bucket allows rollback
- No downstream sync during MVP
- Component isolation: API won’t break if ETL fails
- Schema changes staged in `dev_` tables
- CloudWatch alerts log and contain failures

## Appendix

### Alternatives Considered
- Redshift/Snowflake: Rejected due to cost
- Tableau: Rejected to stay fully serverless
- Real-time ingestion: Deferred to post-MVP

### Related Artifacts
- GitHub repo
- ERD diagram
- Sample Athena queries
- AWS CLI examples
- Databricks churn notebook (if published)

### Sections Skipped
- CSRF/web form security: not applicable
- DDoS protection: IAM-restricted APIs only
- A/B testing: internal rollout only
- Accessibility testing: not public UI
