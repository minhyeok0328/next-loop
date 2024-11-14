from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.window import Window

def process_parquet():
    spark = SparkSession.builder \
        .appName("Parquet Processing Test") \
        .config("spark.driver.memory", "2g") \
        .config("spark.executor.memory", "2g") \
        .getOrCreate()
    
    try:
        # Parquet 파일 읽기
        print("Parquet 파일 읽기 시작...")
        df = spark.read.parquet("/opt/spark/data/output/processed_data.parquet")
        
        print("\n원본 Parquet 데이터 스키마:")
        df.printSchema()
        
        # 고급 데이터 처리 예시
        window_spec = Window.partitionBy('year', 'month').orderBy('processed_date')
        
        advanced_df = df \
            .withColumn("row_number", row_number().over(window_spec)) \
            .withColumn("moving_avg", avg("value").over(window_spec)) \
            .withColumn("rank", rank().over(window_spec))
        
        print("\n처리된 데이터:")
        advanced_df.show(5)
        
        # 처리된 데이터를 다시 Parquet으로 저장
        output_path = "/opt/spark/data/output/advanced_processed.parquet"
        advanced_df.write \
            .mode("overwrite") \
            .parquet(output_path)
        
        print(f"\n고급 처리된 데이터가 {output_path}에 저장되었습니다.")
        
        # 성능 메트릭 출력
        print("\n처리 통계:")
        print(f"총 레코드 수: {advanced_df.count()}")
        print(f"파티션 수: {advanced_df.rdd.getNumPartitions()}")
        
    except Exception as e:
        print(f"에러 발생: {str(e)}")
        raise e
    finally:
        spark.stop()

if __name__ == "__main__":
    process_parquet()
