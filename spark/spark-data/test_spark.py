from pyspark.sql import SparkSession
from pyspark.sql.functions import *

def test_spark_postgres():
    # Spark 세션 생성
    spark = SparkSession.builder \
        .appName("Spark Test") \
        .config("spark.jars", "/opt/spark/jars/postgresql-42.6.0.jar") \
        .getOrCreate()

    # 테스트 데이터 생성
    test_data = [
        (1, "Test1", "2024-01-01"),
        (2, "Test2", "2024-01-02"),
        (3, "Test3", "2024-01-03")
    ]
    
    # DataFrame 생성
    df = spark.createDataFrame(test_data, ["id", "name", "date"])
    
    # 간단한 변환
    processed_df = df.withColumn("processed_date", current_timestamp())
    
    # PostgreSQL에 저장
    processed_df.write \
        .format("jdbc") \
        .option("url", "jdbc:postgresql://postgres:5432/sparkdb") \
        .option("dbtable", "test_data") \
        .option("user", "spark") \
        .option("password", "sparkpass") \
        .mode("overwrite") \
        .save()
        
    print("테스트 데이터 처리 완료")
    
    # 저장된 데이터 확인
    saved_data = spark.read \
        .format("jdbc") \
        .option("url", "jdbc:postgresql://postgres:5432/sparkdb") \
        .option("dbtable", "test_data") \
        .option("user", "spark") \
        .option("password", "sparkpass") \
        .load()
        
    print("저장된 데이터 수:", saved_data.count())
    saved_data.show()
    
    spark.stop()

if __name__ == "__main__":
    test_spark_postgres()
