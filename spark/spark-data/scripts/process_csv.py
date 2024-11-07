from pyspark.sql import SparkSession
from pyspark.sql.functions import *

def process_csv():
    # Spark 세션 생성 - JDBC 드라이버 클래스 명시적 지정
    spark = SparkSession.builder \
        .appName("CSV Processing Test") \
        .config("spark.jars", "/opt/spark/jars/postgresql-42.6.0.jar") \
        .config("spark.driver.extraClassPath", "/opt/spark/jars/postgresql-42.6.0.jar") \
        .config("spark.executor.extraClassPath", "/opt/spark/jars/postgresql-42.6.0.jar") \
        .getOrCreate()
    
    try:
        # CSV 파일 읽기
        print("CSV 파일 읽기 시작...")
        df = spark.read \
            .option("header", "true") \
            .option("inferSchema", "true") \
            .csv("/opt/spark/data/input/test.csv")
        
        print("데이터 스키마:")
        df.printSchema()
        
        print("\n원본 데이터:")
        df.show()
        
        # 데이터 처리
        processed_df = df \
            .groupBy("name") \
            .agg(
                count("*").alias("count"),
                sum("value").alias("total_value"),
                avg("value").alias("avg_value")
            )
        
        print("\n처리된 데이터:")
        processed_df.show()
        
        # PostgreSQL에 저장
        print("\nPostgreSQL에 데이터 저장 중...")
        processed_df.write \
            .format("jdbc") \
            .option("url", "jdbc:postgresql://postgres:5432/sparkdb") \
            .option("driver", "org.postgresql.Driver") \
            .option("dbtable", "sales_summary") \
            .option("user", "spark") \
            .option("password", "sparkpass") \
            .mode("overwrite") \
            .save()
        
        print("처리 완료!")
        
    except Exception as e:
        print(f"에러 발생: {str(e)}")
        raise e
    finally:
        spark.stop()

if __name__ == "__main__":
    process_csv()
