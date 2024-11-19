from pyspark.sql import SparkSession

def test_spark_cluster():
    try:
        # SparkSession 설정
        spark = SparkSession.builder \
            .appName("SparkClusterTest") \
            .master("spark://spark-master:7077") \
            .config("spark.pyspark.python", "/usr/local/bin/python3") \
            .config("spark.pyspark.driver.python", "/usr/local/bin/python3") \
            .config("spark.executorEnv.PYSPARK_PYTHON", "/usr/local/bin/python3") \
            .config("spark.driver.extraJavaOptions", "-Dlog4j.rootCategory=DEBUG,console") \
            .config("spark.executor.extraJavaOptions", "-Dlog4j.rootCategory=DEBUG,console") \
            .config("spark.driver.memory", "1g") \
            .config("spark.executor.memory", "1g") \
            .config("spark.executor.cores", "2") \
            .config("spark.executor.instances", "2") \
            .config("spark.dynamicAllocation.enabled", "true") \
            .config("spark.dynamicAllocation.minExecutors", "1") \
            .config("spark.dynamicAllocation.maxExecutors", "2") \
            .config("spark.network.timeout", "1200s") \
            .config("spark.executor.heartbeatInterval", "30s") \
            .config("spark.driver.host", "10.0.1.3") \
            .config("spark.driver.bindAddress", "0.0.0.0") \
            .config("spark.python.worker.reuse", "true") \
            .config("spark.python.worker.memory", "512m") \
            .config("spark.driver.maxResultSize", "512m") \
            .config("spark.rpc.askTimeout", "180s") \
            .config("spark.rpc.lookupTimeout", "180s") \
            .config("spark.memory.fraction", "0.6") \
            .config("spark.memory.storageFraction", "0.5") \
            .getOrCreate()

        # 로그 레벨 설정
        spark.sparkContext.setLogLevel("INFO")

        # 간단한 테스트 연산 수행
        print("Creating test RDD...")
        nums = spark.sparkContext.parallelize(range(1, 1001), 4)
        
        print("Performing count operation...")
        count = nums.count()
        print(f"Count result: {count}")
        
        print("Performing simple transformation and action...")
        squared = nums.map(lambda x: x * x)
        sum_squares = squared.reduce(lambda x, y: x + y)
        print(f"Sum of squares: {sum_squares}")

        # 정상적으로 SparkSession 종료
        print("Stopping SparkSession...")
        spark.stop()
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"Error occurred during Spark test: {str(e)}")
        raise

if __name__ == "__main__":
    test_spark_cluster()
