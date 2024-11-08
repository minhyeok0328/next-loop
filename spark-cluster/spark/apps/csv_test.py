from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import os

def process_csv():
    # Spark 세션 생성
    spark = SparkSession.builder \
        .appName("CSV Processing Test") \
        .config("spark.driver.memory", "2g") \
        .config("spark.executor.memory", "2g") \
        .getOrCreate()
    
    try:
        # CSV 파일 읽기
        print("CSV 파일 읽기 시작...")
        df = spark.read \
            .option("header", "true") \
            .option("inferSchema", "true") \
            .csv("/opt/spark/data/input/test.csv")
        
        print("\n원본 데이터 스키마:")
        df.printSchema()
        
        print("\n원본 데이터 샘플:")
        df.show()
        
        # 데이터 처리
        processed_df = df \
            .withColumn("processed_date", current_timestamp()) \
            .withColumn("year", year(col("date"))) \
            .withColumn("month", month(col("date")))
        
        print("\n처리된 데이터:")
        processed_df.show()
        
        # 출력 디렉토리 생성 확인
        output_path = "/opt/spark/data/output/processed_data.parquet"
        
        # Parquet 형식으로 저장
        processed_df.write \
            .mode("overwrite") \
            .format("parquet") \
            .save(output_path)
        
        print(f"\n데이터가 {output_path}에 저장되었습니다.")
        
    except Exception as e:
        print(f"에러 발생: {str(e)}")
        raise e
    finally:
        spark.stop()

if __name__ == "__main__":
    process_csv()
