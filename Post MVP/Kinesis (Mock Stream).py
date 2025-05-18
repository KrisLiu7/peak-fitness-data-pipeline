import json, time, random
import boto3

kinesis = boto3.client("kinesis", region_name="us-east-1")

while True:
    data = {
        "user_id": f"user_{random.randint(1, 100)}",
        "class_id": f"class_{random.randint(1, 10)}",
        "timestamp": int(time.time())
    }
    kinesis.put_record(
        StreamName="mock-checkin-stream",
        Data=json.dumps(data),
        PartitionKey="partitionKey"
    )
    time.sleep(1)
