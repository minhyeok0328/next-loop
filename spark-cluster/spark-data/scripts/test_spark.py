from pyspark.sql import SparkSession
from pyspark.sql.functions import *

def test_spark():
    # Spark 세션 생성
    spark = SparkSession.builder \
        .appName("Spark Test") \
        .getOrCreate()
    
    try:
        # 데이터 읽기
        print("데이터 읽기 시작...")
        data = [
            (1, "Test1", 100),
            (2, "Test2", 200),
            (3, "Test3", 300)
        ]
        
        df = spark.createDataFrame(data, ["id", "name", "value"])
        
        print("\n생성된 데이터:")
        df.show()
        
        # 간단한 집계
        print("\n집계 결과:")
        df.agg(
            count("*").alias("count"),
            sum("value").alias("total_value"),
            avg("value").alias("avg_value")
        ).show()
        
    except Exception as e:
        print(f"에러 발생: {str(e)}")
        raise e
    finally:
        spark.stop()

if __name__ == "__main__":
    test_spark()
