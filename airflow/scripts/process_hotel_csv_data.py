import logging
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, when
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType

logger = logging.getLogger(__name__)

output_path = "gs://dowhat-datawarehouse/data.parquet"

# Spark Session 생성
spark = SparkSession.builder \
    .appName("Hotel CSV File Processing") \
    .getOrCreate()

# JSON 필드(contents)의 스키마 정의
contents_schema = StructType([
    StructField("orderType", StringType(), True),
    StructField("itemSeq", IntegerType(), True),
    StructField("count", IntegerType(), True),
    StructField("itemName", StringType(), True),
    StructField("departmentSeq", IntegerType(), True),
    StructField("person", IntegerType(), True),
    StructField("price", IntegerType(), True),
    StructField("wantStart", StringType(), True),
    StructField("wantEnd", StringType(), True)
])

def main(input_files_str):
    if not input_files_str:
        raise ValueError("No input files provided")

    input_files = input_files_str.split(',')
    logger.info(f"Processing files: {input_files}")

    df = None
    for file in input_files:
        temp_df = spark.read.csv(file, header=True, inferSchema=True)
        df = temp_df if df is None else df.union(temp_df)

    logger.info("CSV files loaded successfully")

    # 데이터 전처리
    df = df.withColumn("order_seq", col("order_seq").cast("int")) \
           .withColumn("order_price", col("order_price").cast("int")) \
           .withColumn("check_in", col("check_in").cast("timestamp")) \
           .withColumn("check_out", col("check_out").cast("timestamp")) \
           .withColumn("check_out_expected", col("check_out_expected").cast("timestamp")) \
           .withColumn("reg_date", col("reg_date").cast("timestamp")) \
           .withColumn("check_date", col("check_date").cast("timestamp")) \
           .withColumn("refuse_date", when(col("refuse_date") != "\\N", col("refuse_date")).cast("timestamp")) \
           .withColumn("complete_date", when(col("complete_date") != "\\N", col("complete_date")).cast("timestamp")) \
           .withColumn("contents", from_json(col("contents"), contents_schema)) \
           .dropna()

    logger.info("Data processing completed")

    # 결과를 Parquet 파일로 저장
    df.write.parquet(output_path)

    logger.info(f"Parquet file saved at: {output_path}")

if __name__ == "__main__":
    input_files_str = sys.argv[1]
    main(input_files_str)
