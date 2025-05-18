import pandas as pd
import boto3
import os

# Load CSV
df = pd.read_csv("C:/Users/Kris OH/Documents/AWS Cloud Essential Course/Project/Datasets/schedule_sample.csv")

# Select and rename columns
df = df[[
    'session_id', 'class_name', 'instructor_name', 'loc_id', 'datetime', 'duration_mins'
]].rename(columns={
    'loc_id': 'location_id',
    'datetime': 'start_time'
})

# Convert time columns
df['start_time'] = pd.to_datetime(df['start_time'], errors='coerce')
df['end_time'] = df['start_time'] + pd.to_timedelta(df['duration_mins'], unit='m')
df.drop(columns=['duration_mins'], inplace=True)

# Save locally
os.makedirs("dim_classes", exist_ok=True)
df.to_parquet("dim_classes/dim_classes.parquet", index=False)

# Upload to S3
s3 = boto3.client('s3')
s3.upload_file("dim_classes/dim_classes.parquet", "peak-fitness-kris-processed", "dim_classes/dim_classes.parquet")

print("✅ dim_classes.parquet uploaded to s3://peak-fitness-kris-processed/dim_classes/")
