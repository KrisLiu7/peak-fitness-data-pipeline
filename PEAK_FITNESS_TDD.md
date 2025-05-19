### Monitoring and Logging

- All ETL operations are monitored through CloudWatch.
- CloudWatch logs record ETL job activity, including record counts, execution time, and failure traces.
- Metric filters are configured to detect failed runs or significant drops in processed record counts.
- Athena partition sync (via Lambda) is validated weekly to ensure queryable table consistency.
- **Schema enforcement checks include:**
  - Type validation for key fields
  - Required field presence
  - Null value filtering
- Record counts are compared between raw and processed S3 layers to ensure no unintentional loss.
- All validation failures or anomalies are logged in CloudWatch and flagged for review. This provides early warning for pipeline or schema drift issues.