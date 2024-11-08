from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Spark Test") \
    .getOrCreate()

# Create test data
data = [
    (1, "Test1", 100),
    (2, "Test2", 200),
    (3, "Test3", 300)
]

# Define schema
schema = StructType([
    StructField("id", IntegerType(), False),
    StructField("name", StringType(), False),
    StructField("value", IntegerType(), False)
])

# Create DataFrame
df = spark.createDataFrame(data, schema)

print("생성된 데이터:")
df.show()

# Perform aggregation
agg_df = df.agg({
    "id": "count",
    "value": "sum",
    "value": "avg"
}).toDF(
    "count",
    "total_value",
    "avg_value"
)

print("\n집계 결과:")
agg_df.show()

# Stop Spark session
spark.stop()
