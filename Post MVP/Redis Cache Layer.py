#Connect from Databricks
# Install redis-py (run in a notebook cell)
%pip install redis

# Write ML results to Redis
import redis

# Connect to Redis
r = redis.Redis(
  host="peak-redis.abc123.ng.0001.use1.cache.amazonaws.com",
  port=6379,
  decode_responses=True
)

# Cache leaderboard (e.g., top 10 classes)
top_classes = spark.sql("""
  SELECT class_name, COUNT(*) as visits 
  FROM class_attendance 
  GROUP BY 1 
  ORDER BY 2 DESC 
  LIMIT 10
""").collect()

# Store in Redis
for row in top_classes:
  r.zadd("leaderboard:classes", {row["class_name"]: row["visits"]})

# Demo: Fetch from Redis
print(r.zrevrange("leaderboard:classes", 0, -1, withscores=True))