#Write Processed Data from Databricks to S3 (Athena-Compatible)
# In Databricks notebook: After ML predictions
at_risk_users.write \
  .format("parquet") \
  .mode("overwrite") \
  .partitionBy("class_date") \  # Align with your TDD partitioning strategy
  .save("s3a://peak-fitness-processed/at_risk_users/")  # Use your processed bucket

#Create Athena Tables
CREATE EXTERNAL TABLE peak_fitness.at_risk_users (
  user_id STRING,
  total_visits INT,
  days_since_last_visit INT,
  churn_risk INT
)
PARTITIONED BY (class_date DATE)
STORED AS PARQUET
LOCATION 's3://peak-fitness-processed/at_risk_users/';

##Refresh partitions
MSCK REPAIR TABLE peak_fitness.at_risk_users;