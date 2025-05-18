import pandas as pd
import os
import boto3

# Load the CSV
df = pd.read_csv("C:/Users/Kris OH/Documents/AWS Cloud Essential Course/Project/Datasets/mindbody_user_snapshot.csv")

# Select needed columns
df = df[[
    'user_id', 'first_name', 'last_name', 'gender', 'email',
    'phone_number', 'date_of_birth', 'city',
    'preferred_location_id', 'created_at'
]]

# Clean date columns
df['date_of_birth'] = pd.to_datetime(df['date_of_birth'], errors='coerce')
df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')

# Save to Parquet
os.makedirs("dim_users", exist_ok=True)
df.to_parquet("dim_users/dim_users.parquet", index=False)

# Upload to S3
s3 = boto3.client('s3')
s3.upload_file("dim_users/dim_users.parquet", "peak-fitness-kris-processed", "dim_users/dim_users.parquet")

print("✅ dim_users.parquet uploaded to s3://peak-fitness-kris-processed/dim_users/")
