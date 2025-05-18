import pandas as pd
import boto3
import os

# ✅ Use the correct JSON parsing mode
df = pd.read_json(r"C:\Users\Kris OH\Documents\AWS Cloud Essential Course\Project\Datasets\class_attendance.json", lines=False)

print("Loaded columns:", df.columns.tolist())
print(df.head())

# Convert timestamp to datetime
df['class_date'] = pd.to_datetime(df['class_datetime'], unit='ms', errors='coerce')

# Drop bad rows
df = df.dropna(subset=['class_date'])

# Filter to ~10% sample (e.g., Jan 2024)
df = df[df['class_date'] < "2024-02-01"]

# Partition and save
dates = df['class_date'].dt.date.unique()
for d in dates:
    part_df = df[df['class_date'].dt.date == d]
    folder = f"fact_attendance/class_datetime={d}/"
    os.makedirs(folder, exist_ok=True)
    part_df.to_parquet(f"{folder}data.parquet", index=False)

# Upload to S3
s3 = boto3.client('s3')
bucket = 'peak-fitness-kris-processed'
for d in dates:
    key = f"fact_attendance/class_datetime={d}/data.parquet"
    local_path = f"fact_attendance/class_datetime={d}/data.parquet"
    s3.upload_file(local_path, bucket, key)

print("✅ Upload completed.")

