import pandas as pd
import os
import boto3

# Load your schedule CSV
df = pd.read_csv("C:/Users/Kris OH/Documents/AWS Cloud Essential Course/Project/Datasets/schedule_sample.csv")

# Extract unique location info
df = df[['loc_id', 'location_name']].drop_duplicates().copy()
df.rename(columns={'loc_id': 'location_id'}, inplace=True)

# Save as Parquet
os.makedirs("dim_locations", exist_ok=True)
df.to_parquet("dim_locations/dim_locations.parquet", index=False)

# Upload to S3
s3 = boto3.client('s3')
s3.upload_file("dim_locations/dim_locations.parquet", "peak-fitness-kris-processed", "dim_locations/dim_locations.parquet")

print("✅ dim_locations.parquet uploaded to s3://peak-fitness-kris-processed/dim_locations/")
