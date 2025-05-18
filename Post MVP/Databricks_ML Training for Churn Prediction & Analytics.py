#Data Loeading
# Configure AWS S3 access (Requester Pays)
spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.requester.pays.enabled", "true")
spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.access.key", "YOUR_KEY")  # Replace!
spark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.secret.key", "YOUR_SECRET")

# Load attendance data
df = spark.read.parquet("s3a://peak-fitness-kris-processed/class_attendance/")
print(f"Total records: {df.count()}")
display(df.limit(5))

#Feature Engineering + Visualization
from pyspark.sql.functions import *

# Calculate user activity features
features = df.groupBy("user_id").agg(
    count("*").alias("total_visits"),
    datediff(current_date(), max("class_date")).alias("days_since_last_visit")
)

# Label churn risk (1 if inactive >30 days)
train_data = features.withColumn("churn_risk", (col("days_since_last_visit") > 30).cast("int"))

# Show distribution
display(train_data.select("days_since_last_visit", "churn_risk"))

#Model Training
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import LogisticRegression

# Prepare features
assembler = VectorAssembler(
    inputCols=["total_visits", "days_since_last_visit"],
    outputCol="features"
)
train_df = assembler.transform(train_data)

# Train model
lr = LogisticRegression(featuresCol="features", labelCol="churn_risk")
model = lr.fit(train_df)

# Show coefficients (interpretability)
print("Model coefficients:", model.coefficients)

#Results & Business Impact
# Count at-risk users
at_risk_users = model.transform(train_df).filter(col("prediction") == 1)
at_risk_count = at_risk_users.count()
total_users = train_df.count()
print(f"At-risk users: {at_risk_count}/{total_users} ({at_risk_count/total_users*100:.1f}%)")

# Save for marketing team
at_risk_users.write.mode("overwrite").csv("/FileStore/at_risk_users.csv")