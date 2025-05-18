import pandas as pd
import os
import boto3

# Load the schedule sample file
df = pd.read_csv("C:/Users/Kris OH/Documents/AWS Cloud Essential Course/Project/Datasets/schedule_sample.csv")

# Extract unique instructor info
df = df[['instructor_id', 'instructor_name']].drop_duplicates().copy()

# Save as Parquet
os.makedirs("dim_instructors", exist_ok=True)
df.to_parquet("dim_instructors/dim_instructors.parquet", index=False)

# Upload to S3
s3 = boto3.client('s3')
s3.upload_file("dim_instructors/dim_instructors.parquet", "peak-fitness-kris-processed", "dim_instructors/dim_instructors.parquet")

print("✅ dim_instructors.parquet uploaded to s3://peak-fitness-kris-processed/dim_instructors/")
