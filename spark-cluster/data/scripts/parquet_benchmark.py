from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType, DoubleType
import random
from datetime import datetime, timedelta
import time
import json
import os

class ParquetBenchmark:
    def __init__(self, spark):
        self.spark = spark
        self.results = {}
    
    def measure_time(self, func, scenario_name):
        """함수 실행 시간 측정"""
        start_time = time.time()
        result = func()
        end_time = time.time()
        duration = end_time - start_time
        self.results[scenario_name] = duration
        print(f"{scenario_name}: {duration:.2f} 초")
        return result
    
    def create_test_dataset(self, num_records=1000000):
        """테스트 데이터셋 생성"""
        schema = StructType([
            StructField("user_id", StringType(), False),
            StructField("timestamp", TimestampType(), False),
            StructField("category", StringType(), False),
            StructField("amount", DoubleType(), False),
            StructField("item_count", IntegerType(), False),
            StructField("region", StringType(), False)
        ])
        
        base_date = datetime.now()
        categories = ["Electronics", "Clothing", "Food", "Books", "Sports"]
        regions = ["Seoul", "Busan", "Incheon", "Daegu", "Daejeon"]
        
        data = []
        for i in range(num_records):
            data.append((
                f"user_{i % 10000:05d}",
                base_date + timedelta(minutes=i % 1440),
                random.choice(categories),
                round(random.uniform(10.0, 1000.0), 2),
                random.randint(1, 10),
                random.choice(regions)
            ))
        
        return self.spark.createDataFrame(data, schema)

    def run_write_benchmarks(self, df):
        """다양한 쓰기 시나리오 벤치마크"""
        print("\n=== 쓰기 성능 벤치마크 ===")
        
        # 기본 Parquet 쓰기
        self.measure_time(
            lambda: df.write.mode("overwrite")
                .parquet("/opt/spark/data/benchmark/basic.parquet"),
            "기본 Parquet 쓰기"
        )
        
        # GZIP 압축 사용
        self.measure_time(
            lambda: df.write.mode("overwrite")
                .option("compression", "gzip")
                .parquet("/opt/spark/data/benchmark/gzip.parquet"),
            "GZIP 압축 Parquet 쓰기"
        )
        
        # SNAPPY 압축 사용
        self.measure_time(
            lambda: df.write.mode("overwrite")
                .option("compression", "snappy")
                .parquet("/opt/spark/data/benchmark/snappy.parquet"),
            "SNAPPY 압축 Parquet 쓰기"
        )
        
        # 파티셔닝 적용
        self.measure_time(
            lambda: df.write.mode("overwrite")
                .partitionBy("region", "category")
                .parquet("/opt/spark/data/benchmark/partitioned.parquet"),
            "파티셔닝된 Parquet 쓰기"
        )

    def run_read_benchmarks(self):
        """다양한 읽기 시나리오 벤치마크"""
        print("\n=== 읽기 성능 벤치마크 ===")
        
        # 파일 존재 여부 확인
        basic_path = "/opt/spark/data/benchmark/basic.parquet"
        gzip_path = "/opt/spark/data/benchmark/gzip.parquet"
        snappy_path = "/opt/spark/data/benchmark/snappy.parquet"
        partitioned_path = "/opt/spark/data/benchmark/partitioned.parquet"
        
        print(f"Checking files:")
        print(f"Basic parquet exists: {os.path.exists(basic_path)}")
        print(f"GZIP parquet exists: {os.path.exists(gzip_path)}")
        print(f"SNAPPY parquet exists: {os.path.exists(snappy_path)}")
        print(f"Partitioned parquet exists: {os.path.exists(partitioned_path)}")
        
        schema = StructType([
            StructField("user_id", StringType(), False),
            StructField("timestamp", TimestampType(), False),
            StructField("category", StringType(), False),
            StructField("amount", DoubleType(), False),
            StructField("item_count", IntegerType(), False),
            StructField("region", StringType(), False)
        ])
        
        if os.path.exists(basic_path):
            print("\n기본 Parquet 읽기 테스트:")
            self.measure_time(
                lambda: self.spark.read.schema(schema).parquet(basic_path).count(),
                "전체 데이터 읽기"
            )
            
        if os.path.exists(gzip_path):
            print("\nGZIP 압축 Parquet 읽기 테스트:")
            self.measure_time(
                lambda: self.spark.read.schema(schema).parquet(gzip_path).count(),
                "GZIP 압축 데이터 읽기"
            )
            
        if os.path.exists(snappy_path):
            print("\nSNAPPY 압축 Parquet 읽기 테스트:")
            self.measure_time(
                lambda: self.spark.read.schema(schema).parquet(snappy_path).count(),
                "SNAPPY 압축 데이터 읽기"
            )
            
        if os.path.exists(partitioned_path):
            print("\n파티션 필터링 테스트:")
            self.measure_time(
                lambda: self.spark.read.schema(schema).parquet(partitioned_path)
                    .where("region = 'Seoul' AND category = 'Electronics'")
                    .count(),
                "파티션 필터링 읽기"
            )

    def save_results(self):
        """벤치마크 결과 저장"""
        with open('/opt/spark/data/benchmark/results.json', 'w') as f:
            json.dump(self.results, f, indent=2)

def main():
    # Spark 세션 생성
    spark = SparkSession.builder\
        .appName("Parquet Benchmark")\
        .config("spark.sql.parquet.compression.codec", "snappy")\
        .getOrCreate()

    try:
        benchmark = ParquetBenchmark(spark)
        
        # 클러스터 정보 출력
        print("=== Spark 클러스터 정보 ===")
        print(f"Spark 버전: {spark.version}")
        print(f"마스터: {spark.sparkContext.master}")
        print(f"사용 가능한 코어: {spark.sparkContext.defaultParallelism}")
        
        # 벤치마크 실행
        print("\n데이터셋 생성 중...")
        df = benchmark.create_test_dataset(1000000)  # 100만 레코드
        
        # 쓰기 벤치마크
        benchmark.run_write_benchmarks(df)
        
        # 읽기 벤치마크
        benchmark.run_read_benchmarks()
        
        # 결과 저장
        benchmark.save_results()
        
        print("\n벤치마크 완료! 결과는 /opt/spark/data/benchmark/results.json 에 저장되었습니다.")

    finally:
        spark.stop()

if __name__ == "__main__":
    main()

