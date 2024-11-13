from pyspark.sql import SparkSession
import sys

# network timeout과 heartbeat 간격 조정
def test_spark_cluster():
    try:
        spark = SparkSession.builder \
            .appName("SparkClusterTest") \
            .config("spark.executor.memory", "1g") \
            .config("spark.executor.cores", "1") \
            .config("spark.executor.instances", "2") \
            .config("spark.network.timeout", "800s") \
            .config("spark.executor.heartbeatInterval", "60s") \
            .config("spark.dynamicAllocation.enabled", "false") \
            .getOrCreate()

        # 간단한 DataFrame 테스트로 변경
        df = spark.createDataFrame([(1,), (2,), (3,)], ["number"])
        result = df.count()
        
        print(f"Test Result: {result}")
        print("Spark Cluster Test Completed Successfully!")

    except Exception as e:
        print(f"Error in Spark job: {str(e)}", file=sys.stderr)
        raise
    finally:
        if 'spark' in locals():
            spark.stop()

if __name__ == "__main__":
    test_spark_cluster()
