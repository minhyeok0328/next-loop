import logging
import sys
import json
import re

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, when, explode, lit, udf, isnull
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType, ArrayType
from datetime import datetime

logger = logging.getLogger(__name__)
today = datetime.now().strftime('%Y-%m-%d')

output_path = f"gs://dowhat-de1-datawarehouse/v1/hotel_order/{today}"

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
    StructField("price", IntegerType(), True),
    StructField("waitingPeriod", IntegerType(), True),
    StructField("delayPeriod", IntegerType(), True),
    StructField("freeCount", IntegerType(), True),
    StructField("couponSeq", IntegerType(), True),
    StructField("resultPrice", IntegerType(), True),
    StructField("completePeriod", IntegerType(), True)
])

# UDF 정의: contents 컬럼의 dict 또는 list 형태 처리
def parse_contents(contents_str):
    try:
        if contents_str is None or contents_str.strip() == "":
            return []

        contents_str = contents_str.strip('"')
        contents_str = contents_str.replace('""', '"')
        contents_str = re.sub(r'\s+', ' ', contents_str).strip()
        contents_str = re.sub(r'[\r\n\t]', '', contents_str)

        contents = json.loads(contents_str)

        if isinstance(contents, dict):
            return [contents]
        elif isinstance(contents, list):
            return contents
        else:
            return []
            
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e} - Content: {contents_str}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error parsing contents: {e} - Content: {contents_str}")
        return []

parse_contents_udf = udf(parse_contents, ArrayType(contents_schema))

def main(input_files_str):
    if not input_files_str:
        raise ValueError("No input files provided")

    input_files = input_files_str.split(',')
    logger.info(f"Processing files: {input_files}")

    df = None
    for file in input_files:
        temp_df = spark.read.csv(
            file,
            header=True,
            inferSchema=True,
            multiLine=True,
            quote='"',
            escape='"'
        )
        df = temp_df if df is None else df.union(temp_df)

    logger.info("CSV files loaded successfully")
    logger.info(f"Initial Data Count: {df.count()}")

    df = df.filter(col("status") == "COMPLETE" ) \
           .drop("room_name", "customer_name", "refuse_date")

    df = df.withColumn("order_seq", col("order_seq").cast("int")) \
           .withColumn("order_price", col("order_price").cast("int")) \
           .withColumn("check_in", col("check_in").cast("timestamp")) \
           .withColumn("check_out", col("check_out").cast("timestamp")) \
           .withColumn("check_out_expected", col("check_out_expected").cast("timestamp")) \
           .withColumn("reg_date", col("reg_date").cast("timestamp")) \
           .withColumn("check_date", col("check_date").cast("timestamp")) \
           .withColumn("complete_date", when((col("complete_date") != r"\N") & (~isnull(col("complete_date"))), col("complete_date")).cast("timestamp")) \
           .withColumn("contents", parse_contents_udf(col("contents")))

    logger.info(f"Data Count after contents parsing: {df.count()}")

    df.select("contents").show(truncate=False)
    df = df.withColumn("contents", explode(col("contents")))

    logger.info(f"Data Count after explode: {df.count()}")

    df = df.withColumn("item_seq", col("contents.itemSeq")) \
           .withColumn("item_name", col("contents.itemName")) \
           .withColumn("item_count", col("contents.count")) \
           .withColumn("department_seq", col("contents.departmentSeq")) \
           .withColumn("price", col("contents.price")) \
           .withColumn("waiting_period", col("contents.waitingPeriod")) \
           .withColumn("delay_period", col("contents.delayPeriod")) \
           .withColumn("free_count", col("contents.freeCount")) \
           .withColumn("coupon_seq", col("contents.couponSeq")) \
           .withColumn("result_price", col("contents.resultPrice")) \
           .withColumn("complete_period", col("contents.completePeriod")) \
           .drop("contents")

    logger.info(f"Data Count after feature extraction: {df.count()}")

    df = df.filter(~isnull(col("item_count")) & (col("order_price") > 0))

    logger.info("Data processing completed")
    df.write.parquet(output_path)

    logger.info(f"Parquet file saved at: {output_path}")

if __name__ == "__main__":
    input_files_str = sys.argv[1]
    main(input_files_str)
